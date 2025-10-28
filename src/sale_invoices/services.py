import base64
from datetime import datetime
import json
import uuid
from src.core.utils.json_helper import ToStrEncoder
from src.core.config import settings
from src.users.schemas import UserInDB, UserOut
from src.users.services import UserService
from src.zatca.services import ZatcaService
from src.csid.services import CSIDService
from src.customers.services import CustomerService
from src.items.services import ItemService
from src.core.enums import DocumentType, InvoicingType, Stage, TaxExemptionReasonCode, PartyIdentificationScheme, InvoiceType, InvoiceTypeCode, PaymentMeansCode, TaxCategory
from .schemas import (
    PagintationParams,
    SaleInvoiceFilters,
    SaleInvoiceCreate,
    SaleInvoiceUpdate,
    SuccessfulResponse,
    SaleInvoiceLineCreate, SaleInvoiceLineOut,
    SaleInvoiceHeaderOut, SaleInvoiceCreate, SaleInvoiceOut,
    CustomerOut
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .repositories import SaleInvoiceRepository
from .exceptions import BaseAppException, InvoiceNotFoundException, InvoiceSigningError, IntegrityErrorException, InvoiceUpdateNotAllowed, raise_integrity_error
from .utils.invoice_helper import invoice_helper
from src.core.utils.math_helper import round_decimal
from decimal import Decimal
from src.core.consts import TAX_RATE, KSA_TZ

class SaleInvoiceService:
    def __init__(self, db: Session, user: UserOut, csid_service: CSIDService, customer_service: CustomerService, item_service: ItemService, zatca_service: ZatcaService, user_service: UserService, sale_invoice_repository: SaleInvoiceRepository):
        self.db = db
        self.user = user
        self.csid_service = csid_service
        self.customer_service = customer_service
        self.item_service = item_service
        self.zatca_service = zatca_service
        self.user_service = user_service
        self.sale_invoice_repository = sale_invoice_repository


    async def get_new_pih(self, user_id: int, stage: Stage) -> str:
        invoice = await self.sale_invoice_repository.get_last_invoice(user_id, stage)
        if invoice is None:
            return "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ=="
        return invoice.invoice_hash


    async def get_new_icv(self, user_id: int, stage: Stage) -> str:
        icv = await self.sale_invoice_repository.get_invoice_count(user_id, stage)
        return icv+1


    async def generate_invoice_number(self, user_id: int, docuemnt_type: DocumentType, invoice_type: InvoiceType, invoice_type_code: InvoiceTypeCode) -> str:
        """Returns the sequence number along with the formatted invoice number."""
        year = datetime.now(KSA_TZ).year
        if docuemnt_type == DocumentType.INVOICE:
            filters = {
                "document_type": docuemnt_type,
                "invoice_type": invoice_type,
                "invoice_type_code": invoice_type_code,
                "year": year
            }
        if docuemnt_type == DocumentType.QUOTATION:
            filters = {
                "document_type": docuemnt_type,
                "year": year
            }
        
        last_invoice = await self.sale_invoice_repository.get_last_invoice(user_id, self.user.stage, filters)
        seq_number = (last_invoice.seq_number if last_invoice else 0) + 1
        return seq_number, invoice_helper.format_invoice_number(invoice_type, invoice_type_code, year, seq_number)


    async def get_invoice_lines(self, invoice_id: int) -> list[SaleInvoiceLineOut]:
        invoice_lines = await self.sale_invoice_repository.get_invoice_lines_by_invoice_id(invoice_id)
        result = []
        for line in invoice_lines:
            full_line = SaleInvoiceLineOut.model_validate(line)
            full_line.item = await self.item_service.get(line.item_id)
            result.append(full_line)
        return result


    async def get_invoice_customer(self, invoice_id: int) -> CustomerOut | None:
        db_invoice = await self.sale_invoice_repository.get_invoice(self.user.id, invoice_id)
        return await self.customer_service.get(db_invoice.customer_id)


    async def get_invoice_header(self, invoice_id: int) -> SaleInvoiceHeaderOut | None:
        invoice_header = await self.sale_invoice_repository.get_invoice(self.user.id, invoice_id)
        if not invoice_header:
            return None
        return SaleInvoiceHeaderOut.model_validate(invoice_header)


    async def get_invoice(self, invoice_id: int) -> SaleInvoiceOut:
        invoice_header = await self.get_invoice_header(invoice_id)
        if not invoice_header:
            raise InvoiceNotFoundException()
        invoice_lines = await self.get_invoice_lines(invoice_id)
        invoice_customer = await self.get_invoice_customer(invoice_id)
        return SaleInvoiceOut(invoice_lines=invoice_lines, customer=invoice_customer, **invoice_header.model_dump())


    async def create_invoice_header(self, user_id: int, data: dict) -> SaleInvoiceHeaderOut:
        year = datetime.now(KSA_TZ).year
        seq_number, invoice_number = await self.generate_invoice_number(user_id, data["document_type"], data["invoice_type"], data["invoice_type_code"])
        data.update({
            "year": year, 
            "seq_number": seq_number, 
            "invoice_number": invoice_number,
            "is_locked": True if data["document_type"] == DocumentType.INVOICE else False
        })
        invoice = await self.sale_invoice_repository.create_invoice(self.user.id, data)
        return SaleInvoiceHeaderOut.model_validate(invoice)


    async def create_invoice_lines(self, invoice_id: int, data: list[dict]) -> None:
        invoice_lines = data.copy()
        for line in invoice_lines:
            line.update({
                "invoice_id": invoice_id,    
                "tax_rate": TAX_RATE[line["classified_tax_category"]]
            })
        await self.sale_invoice_repository.create_invoice_lines(data)


    async def calculate_amounts(self, data: SaleInvoiceCreate) -> dict:
        """Calculates amounts for invoice lines and totals. Returns a dict representing the new invoice."""
        invoice = data.model_dump()
        # Create invoice lines
        invoice_lines = []
        for line in data.invoice_lines:
            item_price_afer_price_discount = round_decimal(line.item_price - line.price_discount, 2)
            total = round_decimal(item_price_afer_price_discount * line.quantity - line.discount_amount, 2)
            tax_rate = TAX_RATE[line.classified_tax_category]

            if(data.prices_include_tax == True):
                line_extension_amount = round_decimal((total * 100) / (tax_rate + 100), 2)
                tax_amount = round_decimal(total - line_extension_amount, 2)
            else:
                line_extension_amount = total
                tax_amount = round_decimal(line_extension_amount * tax_rate / 100, 2)
                
            rounding_amount = round_decimal(line_extension_amount + tax_amount, 2)
            line_dict = line.model_dump()
            line_dict.update({
                "line_extension_amount": line_extension_amount,
                "tax_amount": tax_amount,
                "rounding_amount": rounding_amount,
            })
            invoice_lines.append(line_dict)

        invoice.update({"invoice_lines": invoice_lines})

        # Add invoice totals
        invoice_line_extension_amount = round_decimal(sum(line["line_extension_amount"] for line in invoice_lines), 2)
        tax_categories = set(line["classified_tax_category"] for line in invoice_lines)
        if(len(tax_categories) == 1):
            tax_rate = Decimal(settings.STANDARD_TAX_RATE) if tax_categories.pop() == TaxCategory.S else Decimal("0") 
            invoice_taxable_amount = round_decimal(invoice_line_extension_amount - data.discount_amount, 2)
            invoice_tax_amount = round_decimal(invoice_taxable_amount * tax_rate / 100, 2)
        else:
            invoice_taxable_amount = invoice_line_extension_amount
            invoice_tax_amount = round_decimal(sum(line["tax_amount"] for line in invoice_lines), 2)
        invoice_tax_inclusive_amount = round_decimal(invoice_taxable_amount + invoice_tax_amount, 2)
        
        invoice.update({
            "line_extension_amount": invoice_line_extension_amount,
            "taxable_amount": invoice_taxable_amount,
            "tax_amount": invoice_tax_amount,
            "tax_inclusive_amount": invoice_tax_inclusive_amount,
            "payable_amount": invoice_tax_inclusive_amount
        })
        return invoice

    async def add_customer_to_invoice_dict(self, invoice_dict: dict) -> None:
        customer = await self.customer_service.get(invoice_dict.get("customer_id"))
        invoice_dict.update({
            "customer": customer.model_dump()
        })

    async def add_additional_field_to_invoice_dict(self, invoice_dict: dict) -> None:
        """Adds pih, icv, uuid, stage to invoice dict."""
        pih = await self.get_new_pih(self.user.id, self.user.stage)
        icv = await self.get_new_icv(self.user.id, self.user.stage)
        invoice_dict.update({
            "pih": pih,
            "icv": icv,
            "uuid": uuid.uuid4(),
            "stage": self.user.stage
        })


    async def prepare_invoice_for_signing(self, invoice_id: int) -> dict[str, str]:
        """Create a dictionary representing the invoice and transform all numeric values into strings."""
        invoice = await self.get_invoice(invoice_id)
        invoice_lines = invoice.invoice_lines
        invoice_dict = invoice.model_dump(exclude_none=True, exclude_unset=True)
        
        # Add item price before discount
        for line in invoice_dict["invoice_lines"]:
            line.update({
                "item_price_before_discount": line["item_price"],
                "item_price_after_discount": round_decimal(line["item_price"] - line["price_discount"], 2), 
            })

        tax_categories = {
            'S': {"taxable_amount": Decimal("0"), "tax_amount": Decimal("0"), "classified_tax_category": 'S', "tax_rate": Decimal(settings.STANDARD_TAX_RATE), "tax_exemption_reason_code": None, "tax_exemption_reason": None, "used": False}, 
            'Z': {"taxable_amount": Decimal("0"), "tax_amount": Decimal("0"), "classified_tax_category": 'Z', "tax_rate": Decimal("0"), "tax_exemption_reason_code": None, "tax_exemption_reason": None, "used": False},
            'E': {"taxable_amount": Decimal("0"), "tax_amount": Decimal("0"), "classified_tax_category": 'E', "tax_rate": Decimal("0"), "tax_exemption_reason_code": None, "tax_exemption_reason": None, "used": False},
            'O': {"taxable_amount": Decimal("0"), "tax_amount": Decimal("0"), "classified_tax_category": 'O', "tax_rate": Decimal("0"), "tax_exemption_reason_code": None, "tax_exemption_reason": None, "used": False},
        }

        # Invoice can have document level discount amount only if all lines have the same VAT category
        if invoice.discount_amount > 0:
            has_total_discount = True
            tax_category = invoice_lines[0].classified_tax_category
            tax_categories[tax_category]['used'] = True
            tax_categories[tax_category]['taxable_amount'] = invoice.taxable_amount
            tax_categories[tax_category]['tax_amount'] = invoice.tax_amount
            tax_categories[tax_category]['tax_exemption_reason_code'] = invoice_lines[0].tax_exemption_reason_code
            tax_categories[tax_category]['tax_exemption_reason'] = invoice_lines[0].tax_exemption_reason
        else:
            has_total_discount = False
            for line in invoice_lines:
                tax_category = line.classified_tax_category
                tax_categories[tax_category]['taxable_amount'] += line.line_extension_amount
                tax_categories[tax_category]['tax_amount'] += line.tax_amount
                tax_categories[tax_category]['tax_exemption_reason_code'] = line.tax_exemption_reason_code
                tax_categories[tax_category]['tax_exemption_reason'] = line.tax_exemption_reason
                tax_categories[tax_category]['used'] = True
        tax_categories = {k: v for k, v in tax_categories.items() if v['used'] == True}

        invoice_dict.update({
            "has_total_discount": has_total_discount,
            "supplier": self.user.model_dump(exclude={"created_at", "updated_at"}),
            "tax_categories": tax_categories
        })
        invoice_json = json.dumps(invoice_dict, cls=ToStrEncoder)
        invoice_dict: dict = json.loads(invoice_json, parse_int=lambda x : str(x))
        return invoice_dict


    async def sign_and_send_to_zatca(self, invoice_id: int) -> None:
        """Signs the invoice and send it to zatca."""
        invoice_header = await self.get_invoice_header(invoice_id)
        
        if(self.user.stage == Stage.COMPLIANCE):
            csid = await self.csid_service.get_compliance_csid(self.user.id)
        else:
            csid = await self.csid_service.get_production_csid(self.user.id)

        invoice_data = await self.prepare_invoice_for_signing(invoice_id)
        try:
            invoice_request = invoice_helper.sign_and_get_request(invoice_data, csid.private_key, csid.certificate)
        except Exception as e:
            raise InvoiceSigningError()
        # with open('inv.xml', "w") as f:
        #     f.write(base64.b64decode(invoice_request["invoice"]).decode())
        if(self.user.stage == Stage.COMPLIANCE):
            zatca_result = await self.zatca_service.send_compliance_invoice(invoice_request, invoice_header.invoice_type, csid.binary_security_token, csid.secret)
        elif(self.user.stage == Stage.PRODUCTION and invoice_header.invoice_type == InvoiceType.STANDARD):
            zatca_result = await self.zatca_service.send_standard_invoice(invoice_request, csid.binary_security_token, csid.secret)
        elif(self.user.stage == Stage.PRODUCTION and invoice_header.invoice_type == InvoiceType.SIMPLIFIED):
            zatca_result = await self.zatca_service.send_simplified_invoice(invoice_request, csid.binary_security_token, csid.secret)

        if invoice_header.invoice_type == InvoiceType.SIMPLIFIED:
            base64_invoice = invoice_request.get("invoice", None)
            zatca_response = json.dumps(zatca_result.zatca_response)
        elif invoice_header.invoice_type == InvoiceType.STANDARD:
            base64_invoice = zatca_result.zatca_response.get("clearedInvoice", None)
            zatca_result.zatca_response.pop("clearedInvoice", None)
            zatca_response = json.dumps(zatca_result.zatca_response)
        
        to_update = {
            "status_code": zatca_result.status_code,
            "zatca_response": zatca_response,
            "invoice_hash": invoice_request.get("invoiceHash"),
            "signed_xml_base64": base64_invoice,
            "base64_qr_code": invoice_helper.extract_base64_qr_code(base64_invoice),
            "is_locked": True,
        }
        await self.sale_invoice_repository.update_invoice(invoice_id=invoice_header.id, data=to_update)
            

    async def create_invoice(self, data: SaleInvoiceCreate) -> SaleInvoiceOut:
        try:
            # Calculate invoice amounts
            invoice_dict = await self.calculate_amounts(data)
            # Add customer to invoice dict
            await self.add_customer_to_invoice_dict(invoice_dict)
            # Add additional invoice fields
            await self.add_additional_field_to_invoice_dict(invoice_dict)

            invoice_lines = invoice_dict.pop("invoice_lines")
            customer = invoice_dict.pop("customer")
            
            # Create invoice header
            invoice = await self.create_invoice_header(self.user.id, invoice_dict)
            # Create invoice lines
            await self.create_invoice_lines(invoice.id, invoice_lines)
            
            # Sign the invoice and send it to zatca
            if data.document_type == DocumentType.INVOICE:
                await self.sign_and_send_to_zatca(invoice.id)
            
            self.db.commit()
            return await self.get_invoice(invoice.id)
        
        except IntegrityError as e:
            self.db.rollback()
            raise_integrity_error(e)
        except Exception as e:
            self.db.rollback()
            raise e
    

    async def update_invoice(self, invoice_id: int, data: SaleInvoiceUpdate) -> SaleInvoiceOut:
        try:
            db_invoice = await self.get_invoice_header(invoice_id)
            if not db_invoice:
                raise InvoiceNotFoundException()
            if db_invoice.is_locked == True or db_invoice.document_type == DocumentType.INVOICE:
                raise InvoiceUpdateNotAllowed()
            
            # Calculate invoice amounts
            invoice_dict = await self.calculate_amounts(data)

            invoice_lines = invoice_dict.pop("invoice_lines")
            await self.sale_invoice_repository.update_invoice(invoice_id, invoice_dict)
            await self.sale_invoice_repository.delete_invoice_lines(invoice_id)
            await self.create_invoice_lines(invoice_id, invoice_lines)

            # Sign the invoice and send it to zatca
            if data.is_locked == True:
                await self.sign_and_send_to_zatca(invoice_id)
            self.db.commit()
            return await self.get_invoice(invoice_id)
        
        except IntegrityError as e:
            self.db.rollback()
            raise_integrity_error(e)
        except Exception as e:
            self.db.rollback()
            raise e
    

    async def delete_invoice(self, invoice_id: int) -> None:
        try:
            db_invoice = await self.get_invoice_header(invoice_id)
            if not db_invoice:
                raise InvoiceNotFoundException()
            if db_invoice.is_locked == True or db_invoice.document_type == DocumentType.INVOICE:
                raise InvoiceUpdateNotAllowed()
            await self.sale_invoice_repository.delete_invoice(invoice_id)
            return None
        
        except IntegrityError as e:
            self.db.rollback()
            raise_integrity_error(e)
        except Exception as e:
            self.db.rollback()
            raise e


    async def get_invoices(self, pagination: PagintationParams, filters: SaleInvoiceFilters) -> tuple[int, list[SaleInvoiceOut]]:
        total, invoices = await self.sale_invoice_repository.get_invoices_by_user_id(self.user.id, self.user.stage, pagination.skip, pagination.limit, filters.model_dump(exclude_none=True))
        return total, [await self.get_invoice(invoice.id) for invoice in invoices]
    