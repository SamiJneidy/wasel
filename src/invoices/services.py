import json
import uuid
from src.core.config import settings
from src.users.schemas import UserInDB, UserOut
from src.users.services import UserService
from src.zatca.services import ZatcaService
from src.csid.services import CSIDService
from src.customers.services import CustomerService
from src.items.services import ItemService
from src.core.enums import InvoicingType, Stage, TaxExemptionReasonCode, PartyIdentificationScheme, InvoiceType, InvoiceTypeCode, PaymentMeansCode, TaxCategory
from .schemas import (
    PagintationParams,
    InvoiceFilters,
    SuccessfulResponse,
    InvoiceLineCreate, InvoiceLineOut,
    InvoiceHeaderOut, InvoiceCreate, InvoiceOut,
    Supplier, CustomerSnapshotCreate, CustomerSnapshotOut, TaxExcemptionCustomer, TaxExcemptionCustomerOut
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .repositories import InvoiceRepository
from .exceptions import BaseAppException, InvoiceNotFoundException, InvoiceSigningError, IntegrityErrorException, raise_integrity_error
from .utils.invoice_helper import invoice_helper
from src.core.utils.math_helper import round_decimal
from decimal import Decimal

class InvoiceService:
    def __init__(self, db: Session, user: UserOut, csid_service: CSIDService, customer_service: CustomerService, item_service: ItemService, zatca_service: ZatcaService, user_service: UserService, invoice_repository: InvoiceRepository):
        self.db = db
        self.user = user
        self.csid_service = csid_service
        self.customer_service = customer_service
        self.item_service = item_service
        self.zatca_service = zatca_service
        self.user_service = user_service
        self.invoice_repository = invoice_repository


    async def get_new_pih(self, user_id: int, stage: Stage) -> str:
        invoice = await self.invoice_repository.get_last_invoice(user_id, stage)
        if invoice is None:
            return "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ=="
        return invoice.invoice_hash


    async def get_new_icv(self, user_id: int, stage: Stage) -> str:
        icv = await self.invoice_repository.get_invoice_count(user_id, stage)
        return icv+1


    async def get_invoice_lines(self, invoice_id: int) -> list[InvoiceLineOut]:
        invoice_lines = await self.invoice_repository.get_invoice_lines_by_invoice_id(invoice_id)
        return [InvoiceLineOut.model_validate(line) for line in invoice_lines]


    async def get_invoice_customer(self, invoice_id: int) -> CustomerSnapshotOut | None:
        customer = await self.invoice_repository.get_invoice_customer_by_invoice_id(invoice_id)
        if not customer:
            return None
        return CustomerSnapshotOut.model_validate(customer)


    async def get_invoice_header(self, invoice_id: int) -> InvoiceHeaderOut:
        invoice_header = await self.invoice_repository.get_invoice(self.user.id, invoice_id)
        return InvoiceHeaderOut.model_validate(invoice_header)


    async def get_invoice(self, invoice_id: int) -> InvoiceOut:
        invoice_header = await self.get_invoice_header(invoice_id)
        invoice_lines = await self.get_invoice_lines(invoice_id)
        invoice_customer = await self.get_invoice_customer(invoice_id)
        return InvoiceOut(invoice_lines=invoice_lines, customer=invoice_customer, **invoice_header.model_dump())


    async def create_invoice_header(self, data: dict) -> InvoiceHeaderOut:
        invoice = await self.invoice_repository.create_invoice(self.user.id, data)
        return InvoiceHeaderOut.model_validate(invoice)


    async def create_invoice_customer(self, invoice_id: int, data: dict) -> None:
        customer = data.copy()
        customer.update({"invoice_id": invoice_id})
        await self.invoice_repository.create_invoice_customer(customer)


    async def create_invoice_lines(self, invoice_id: int, data: list[dict]) -> None:
        invoice_lines = data.copy()
        for line in invoice_lines:
            line.update({"invoice_id": invoice_id})
        await self.invoice_repository.create_invoice_lines(data)


    async def prepare_invoice_for_creation(self, data: InvoiceCreate) -> dict:
        invoice = data.model_dump()

        # Create invoice lines
        invoice_lines = []
        for line in data.invoice_lines:
            item = await self.item_service.get(line.item_id)
            line_extension_amount = round_decimal(item.price * line.quantity - line.discount_amount, 2)
            tax_amount = round_decimal(line_extension_amount * data.tax_rate / 100, 2)
            rounding_amount = round_decimal(line_extension_amount + tax_amount, 2)
            line_dict = {
                "item_name": item.name,
                "item_price": item.price,
                "item_unit_code": item.unit_code,
                "quantity": line.quantity,
                "discount_amount": line.discount_amount,
                "line_extension_amount": line_extension_amount,
                "tax_amount": tax_amount,
                "rounding_amount": rounding_amount,
                "tax_exemption_reason_code": line.tax_exemption_reason_code,
                "tax_exemption_reason": line.tax_exemption_reason
            }
            invoice_lines.append(line_dict)
        invoice.update({"invoice_lines": invoice_lines})

        # Create invoice customer
        if data.customer is not None:
            if isinstance(data.customer, int):
                customer = await self.customer_service.get(data.customer)
                customer_snapshot = CustomerSnapshotCreate(**customer.model_dump(exclude_none=True, exclude_unset=True))
                customer_snapshot.customer_id = data.customer
                customer_dict = customer_snapshot.model_dump()
            else:
                customer_dict = data.customer.model_dump()
            invoice.update({"customer": customer_dict})

        # Add invoice totals
        invoice_line_extension_amount = round_decimal(sum(line["line_extension_amount"] for line in invoice_lines), 2)
        invoice_taxable_amount = round_decimal(invoice_line_extension_amount - data.discount_amount, 2)
        invoice_tax_amount = round_decimal(invoice_taxable_amount * data.tax_rate / 100, 2)
        invoice_tax_inclusive_amount = round_decimal(invoice_taxable_amount + invoice_tax_amount, 2)
        payable_amount = invoice_tax_inclusive_amount
        invoice.update({
            "line_extension_amount": invoice_line_extension_amount,
            "taxable_amount": invoice_taxable_amount,
            "tax_amount": invoice_tax_amount,
            "tax_inclusive_amount": invoice_tax_inclusive_amount,
            "payable_amount": payable_amount
        })
        
        # Add additional invoice fields
        pih = await self.get_new_pih(self.user.id, self.user.stage)
        icv = await self.get_new_icv(self.user.id, self.user.stage)
        invoice.update({
            "pih": pih,
            "icv": icv,
            "uuid": uuid.uuid4(),
            "stage": self.user.stage
        })
        return invoice


    async def prepare_invoice_for_signing(self, invoice_id: int) -> dict[str, str]:
        """Create a dictionary representing the invoice"""
        invoice = await self.get_invoice(invoice_id)
        invoice_json = invoice.model_dump_json(exclude_none=True, exclude_unset=True)
        invoice_dict = json.loads(invoice_json)
        supplier = Supplier(**self.user.model_dump()).model_dump()
        invoice_dict.update({
            "supplier": supplier
        })
        invoice_json = json.dumps(invoice_dict)
        invoice_dict = json.loads(invoice_json, parse_int=lambda x : str(x))
        return invoice_dict


    async def create_compliance_invoice(self, data: InvoiceCreate) -> InvoiceOut:
        try:

            # Prepare invoice for creation and create invoice header
            invoice_dict = await self.prepare_invoice_for_creation(data)
            customer = invoice_dict.pop("customer")
            invoice_lines = invoice_dict.pop("invoice_lines")
            invoice = await self.create_invoice_header(invoice_dict)

            # Create invoice customer
            if customer is not None:
                await self.create_invoice_customer(invoice.id, customer) 

            # Create invoice lines
            await self.create_invoice_lines(invoice.id, invoice_lines)

            # Sign the invoice
            invoice_data = await self.prepare_invoice_for_signing(invoice.id)
            csid = await self.csid_service.get_compliance_csid(self.user.id)
            try:
                invoice_request = invoice_helper.sign_invoice(invoice_data, csid.private_key, csid.certificate)
            except Exception as e:
                print(e)
                raise InvoiceSigningError()
            # Send invoice to zatca and update the related fields
            zatca_result = await self.zatca_service.send_compliance_invoice(invoice_request, data.invoice_type, csid.binary_security_token, csid.secret)
            invoice_request: dict = json.loads(invoice_request)
            base64_invoice = invoice_request.get("invoice")
            updated_data = {
                "status_code": zatca_result.status_code,
                "zatca_response": json.dumps(zatca_result.zatca_response),
                "invoice_hash": invoice_request.get("invoiceHash"),
                "signed_xml_base64": base64_invoice,
                "base64_qr_code": invoice_helper.extract_base64_qr_code(base64_invoice)
            }
            await self.invoice_repository.update_invoice(invoice_id=invoice.id, data=updated_data)
            self.db.commit()
            return await self.get_invoice(invoice.id)
        except IntegrityError as e:
            print(e)
            self.db.rollback()
            raise_integrity_error(e)
        except BaseAppException as e:
            self.db.rollback()
            raise e
    
 
    async def create_standard_invoice(self, data: InvoiceCreate) -> InvoiceOut:
        try:

            # Prepare invoice for creation and create invoice header
            invoice_dict = await self.prepare_invoice_for_creation(data)
            customer = invoice_dict.pop("customer")
            invoice_lines = invoice_dict.pop("invoice_lines")
            invoice = await self.create_invoice_header(invoice_dict)

            # Create invoice customer
            if customer is not None:
                await self.create_invoice_customer(invoice.id, customer) 

            # Create invoice lines
            await self.create_invoice_lines(invoice.id, invoice_lines)

            # Sign the invoice
            invoice_data = await self.prepare_invoice_for_signing(invoice.id)
            csid = await self.csid_service.get_production_csid(self.user.id)
            try:
                invoice_request = invoice_helper.sign_invoice(invoice_data, csid.private_key, csid.certificate)
            except Exception as e:
                raise InvoiceSigningError()
            # Send invoice to zatca and update the related fields
            zatca_result = await self.zatca_service.send_standard_invoice(invoice_request, csid.binary_security_token, csid.secret)
            base64_invoice = zatca_result.zatca_response.get("clearedInvoice")
            updated_data = {
                "status_code": zatca_result.status_code,
                "zatca_response": json.dumps(zatca_result.zatca_response.pop("clearedInvoice")),
                "invoice_hash": invoice_helper.extract_invoice_hash(base64_invoice),
                "signed_xml_base64": base64_invoice,
                "base64_qr_code": invoice_helper.extract_base64_qr_code(base64_invoice)
            }
            await self.invoice_repository.update_invoice(invoice_id=invoice.id, data=updated_data)
            self.db.commit()
            return await self.get_invoice(invoice.id)
        except IntegrityError as e:
            print(e)
            self.db.rollback()
            raise_integrity_error(e)
        except BaseAppException as e:
            self.db.rollback()
            raise e
    

    async def create_simplified_invoice(self, data: InvoiceCreate) -> InvoiceOut:
        try:
            # Prepare invoice for creation and create invoice header
            invoice_dict = await self.prepare_invoice_for_creation(data)
            customer = invoice_dict.pop("customer")
            invoice_lines = invoice_dict.pop("invoice_lines")
            invoice = await self.create_invoice_header(invoice_dict)

            # Create invoice customer
            if customer is not None:
                await self.create_invoice_customer(invoice.id, customer) 

            # Create invoice lines
            await self.create_invoice_lines(invoice.id, invoice_lines)
            
            # Sign the invoice
            invoice_data = await self.prepare_invoice_for_signing(invoice.id)
            csid = await self.csid_service.get_production_csid(self.user.id)
            try:
                invoice_request = invoice_helper.sign_invoice(invoice_data, csid.private_key, csid.certificate)
            except Exception as e:
                raise InvoiceSigningError()
            # Send invoice to zatca and update the related fields
            zatca_result = await self.zatca_service.send_simplified_invoice(invoice_request, csid.binary_security_token, csid.secret)
            invoice_request: dict = json.loads(invoice_request)
            base64_invoice = invoice_request.get("invoice")
            updated_data = {
                "status_code": zatca_result.status_code,
                "zatca_response": json.dumps(zatca_result.zatca_response),
                "invoice_hash": invoice_request.get("invoiceHash"),
                "signed_xml_base64": base64_invoice,
                "base64_qr_code": invoice_helper.extract_base64_qr_code(base64_invoice)
            }
            await self.invoice_repository.update_invoice(invoice_id=invoice.id, data=updated_data)
            self.db.commit()
            return await self.get_invoice(invoice.id)
        except IntegrityError as e:
            print(e)
            self.db.rollback()
            raise_integrity_error(e)
        except BaseAppException as e:
            self.db.rollback()
            raise e
    

    async def get_invoices(self, pagination: PagintationParams, filters: InvoiceFilters) -> tuple[int, list[InvoiceOut]]:
        total, invoices = await self.invoice_repository.get_invoices_by_user_id(self.user.id, self.user.stage, pagination.skip, pagination.limit, filters.model_dump(exclude_none=True))
        return total, [await self.get_invoice(invoice.id) for invoice in invoices]