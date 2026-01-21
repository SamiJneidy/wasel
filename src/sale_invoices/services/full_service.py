from datetime import datetime
from typing import Any, Dict, List, Tuple
import uuid
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from src.core.enums import DocumentType, InvoiceStatus, InvoiceTaxAuthorityStatus, InvoiceType, InvoiceTypeCode, TaxAuthority
from src.core.utils.math_helper import round_decimal
from src.core.consts import TAX_RATE, KSA_TZ
from src.users.schemas import UserInDB
from src.items.services import ItemService
from src.tax_authorities.services import TaxAuthorityService
from ..repositories import SaleInvoiceRepository
from ..schemas import (
    PagintationParams,
    QuotationConvert,
    SaleInvoiceFilters,
    SaleInvoiceLineCreate,
    SaleInvoiceLineOut,
    SaleInvoiceHeaderOut,
    SaleInvoiceCreate,
    SaleInvoiceOut,
    SaleInvoiceUpdate,
    SaleInvoiceUpdateStatus,
)
from ..exceptions import (
    BaseAppException,
    InvoiceSendNotAllowed,
    InvoiceNotFoundException,
    InvoiceUpdateNotAllowed,
    InvoiceDeleteNotAllowed,
    CreditDebitNoteNotAllowed,
    raise_integrity_error,
)
    
class SaleInvoiceService:
    INVOICE_NUMBER_PREFIX = {
        DocumentType.INVOICE: {
            InvoiceTypeCode.INVOICE: {InvoiceType.STANDARD: "TAXINV", InvoiceType.SIMPLIFIED: "SIMINV"},
            InvoiceTypeCode.CREDIT_NOTE: {InvoiceType.STANDARD: "TAXCD", InvoiceType.SIMPLIFIED: "SIMCD"},
            InvoiceTypeCode.DEBIT_NOTE: {InvoiceType.STANDARD: "TAXDB", InvoiceType.SIMPLIFIED: "SIMDB"},  
        },
        DocumentType.QUOTATION: {
            InvoiceTypeCode.INVOICE: {InvoiceType.STANDARD: "QT", InvoiceType.SIMPLIFIED: "QT"},
            InvoiceTypeCode.CREDIT_NOTE: {InvoiceType.STANDARD: "QT", InvoiceType.SIMPLIFIED: "QT"},
            InvoiceTypeCode.DEBIT_NOTE: {InvoiceType.STANDARD: "QT", InvoiceType.SIMPLIFIED: "QT"},  
        }
    }

    def __init__(
        self,
        repo: SaleInvoiceRepository,
        item_service: ItemService,
        tax_authority_service: TaxAuthorityService,
    ) -> None:
        self.repo = repo
        self.item_service = item_service
        self.tax_authority_service = tax_authority_service

    async def generate_invoice_number(self, user: UserInDB, document_type: DocumentType, invoice_type: InvoiceType, invoice_type_code: InvoiceTypeCode) -> tuple[int, str]:
        """Returns the sequence number along with the formatted invoice number."""
        year = datetime.now().year
        if document_type == DocumentType.INVOICE:
            filters = {
                "document_type": document_type,
                "invoice_type": invoice_type,
                "invoice_type_code": invoice_type_code,
                "year": year
            }
        if document_type == DocumentType.QUOTATION:
            filters = {
                "document_type": document_type,
                "year": year
            }
        last_invoice = await self.repo.get_last_invoice(user.organization_id, user.branch_id, filters)
        seq_number = (last_invoice.seq_number if last_invoice else 0) + 1
        number = str(seq_number).zfill(6)
        two_digit_year = str(year)[2:]
        prefix = self.INVOICE_NUMBER_PREFIX[document_type][invoice_type_code][invoice_type]
        return seq_number, f"{prefix}-{two_digit_year}-{number}"

    async def _get_invoice_header(self, user: UserInDB, invoice_id: int) -> SaleInvoiceHeaderOut:
        invoice = await self.repo.get_invoice(user.organization_id, invoice_id)
        if not invoice:
            raise InvoiceNotFoundException()
        invoice = SaleInvoiceHeaderOut.model_validate(invoice)
        if user.organization.tax_authority == TaxAuthority.ZATCA_PHASE2:
            invoice.tax_authority_data = await self.tax_authority_service.get_invoice_tax_authority_data(user, invoice_id)
        return invoice
    
    async def _get_invoice_lines(self, user: UserInDB, invoice_id: int) -> List[SaleInvoiceLineOut]:
        invoice_lines = await self.repo.get_invoice_lines_by_invoice_id(invoice_id)
        result: List[SaleInvoiceLineOut] = []
        for line in invoice_lines:
            item = await self.item_service.get(user, line.item_id)
            line_out = SaleInvoiceLineOut.model_validate(line)
            line_out.item = item
            if user.organization.tax_authority == TaxAuthority.ZATCA_PHASE2:
                line_out.tax_authority_data = await self.tax_authority_service.get_line_tax_authority_data(line.id)
            result.append(line_out)
        return result

    async def _get_invoice_lines(self, user: UserInDB, invoice_id: int) -> List[SaleInvoiceLineOut]:
        invoice_lines = await self.repo.get_invoice_lines_by_invoice_id(invoice_id)
        result: List[SaleInvoiceLineOut] = []
        for line in invoice_lines:
            item = await self.item_service.get(user, line.item_id)
            line_out = SaleInvoiceLineOut.model_validate(line)
            line_out.item = item
            if user.organization.tax_authority == TaxAuthority.ZATCA_PHASE2:
                line_out.tax_authority_data = await self.tax_authority_service.get_line_tax_authority_data(user, line.id)
            result.append(line_out)
        return result

    async def _create_invoice_header(self, user: UserInDB, data: Dict[str, Any]) -> SaleInvoiceHeaderOut:
        invoice = await self.repo.create_invoice(user.organization_id, user.id, data)
        return SaleInvoiceHeaderOut.model_validate(invoice)

    async def _create_invoice_lines(self, user: UserInDB, invoice_id: int, data: List[Dict[str, Any]]) -> None:
        for line in data:
            line["tax_rate"] = TAX_RATE[line["classified_tax_category"]]
            line_metadata = line.pop("tax_authority_data", None)
            db_line = await self.repo.create_invoice_line(invoice_id, line)
            if user.organization.tax_authority == TaxAuthority.ZATCA_PHASE2 and line_metadata is not None:
                await self.tax_authority_service.create_line_tax_authority_data(user, invoice_id, db_line.id, line_metadata)

    async def _calculate_amounts(self, data: SaleInvoiceCreate) -> Dict[str, Any]:
        invoice: Dict[str, Any] = data.model_dump(exclude={"tax_authority_data", "send_to_tax_authority"}, exclude_none=True)
        invoice_lines: List[Dict[str, Any]] = []

        for line in data.invoice_lines:
            tax_rate = TAX_RATE[line.classified_tax_category]
            item_price_after_price_discount = round(line.item_price - line.price_discount, 2)
            total = round(item_price_after_price_discount * line.quantity - line.discount_amount, 2)

            if data.prices_include_tax:
                line_extension_amount = round_decimal((total * Decimal("100")) / (tax_rate + Decimal("100")), 2)
                tax_amount = round_decimal(total - line_extension_amount, 2)
            else:
                line_extension_amount = Decimal(str(total))
                tax_amount = round_decimal(line_extension_amount * tax_rate / Decimal("100"), 2)

            rounding_amount = round_decimal(line_extension_amount + tax_amount, 2)

            line_dict = line.model_dump(exclude={"tax_authority_data"})
            line_dict.update({
                "line_extension_amount": line_extension_amount,
                "tax_amount": tax_amount,
                "rounding_amount": rounding_amount,
            })
            invoice_lines.append(line_dict)

        invoice["invoice_lines"] = invoice_lines

        invoice_line_extension_amount = round_decimal(sum(line["line_extension_amount"] for line in invoice_lines), 2)
        tax_categories = {line["classified_tax_category"] for line in invoice_lines}

        if len(tax_categories) == 1:
            tax_rate = TAX_RATE[tax_categories.pop()]
            invoice_taxable_amount = round_decimal(invoice_line_extension_amount - data.discount_amount, 2)
            invoice_tax_amount = round_decimal(invoice_taxable_amount * tax_rate / Decimal("100"), 2)
        else:
            invoice_taxable_amount = invoice_line_extension_amount
            invoice_tax_amount = round_decimal(sum(line["tax_amount"] for line in invoice_lines), 2)

        invoice_tax_inclusive_amount = round_decimal(invoice_taxable_amount + invoice_tax_amount, 2)

        invoice.update({
            "line_extension_amount": invoice_line_extension_amount,
            "taxable_amount": invoice_taxable_amount,
            "tax_amount": invoice_tax_amount,
            "tax_inclusive_amount": invoice_tax_inclusive_amount,
            "payable_amount": invoice_tax_inclusive_amount,
        })

        return invoice

    async def _validate_before_creation(self, user: UserInDB, data: SaleInvoiceCreate) -> None:
        # Validate original_invoice_id for credit notes
        is_note = data.invoice_type_code in {InvoiceTypeCode.CREDIT_NOTE, InvoiceTypeCode.DEBIT_NOTE}
        if is_note:
            original_invoice_header = await self._get_invoice_header(user, data.original_invoice_id)
            if original_invoice_header.status != InvoiceStatus.ISSUED:
                raise CreditDebitNoteNotAllowed()
            if original_invoice_header.document_type == DocumentType.QUOTATION:
                raise CreditDebitNoteNotAllowed(detail="Can not create credit or debit note for a QUOTATION")
            if original_invoice_header.invoice_type_code == InvoiceTypeCode.INVOICE:
                raise CreditDebitNoteNotAllowed(detail="Can not create credit or debit note for a credit or debit note")
            
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def get_invoice(self, user: UserInDB, invoice_id: int) -> SaleInvoiceOut:
        header = await self._get_invoice_header(user, invoice_id)
        lines = await self._get_invoice_lines(user, invoice_id)
        return SaleInvoiceOut(
            invoice_lines=lines,
            **header.model_dump(),
        )

    async def create_invoice(self, user: UserInDB, data: SaleInvoiceCreate) -> SaleInvoiceOut:
        try:
            self._validate_before_creation(user, data)
            invoice_dict = await self._calculate_amounts(data)
            seq, invoice_number = await self.generate_invoice_number(
                user, 
                data.document_type, 
                data.invoice_type, 
                data.invoice_type_code,
            )
            invoice_lines = invoice_dict.pop("invoice_lines")
            invoice_dict.update({
                "uuid": uuid.uuid4(), 
                "invoice_number": invoice_number,
                "seq_number": seq,
                "tax_authority_status": InvoiceTaxAuthorityStatus.NOT_SENT,

            })
            invoice_header = await self._create_invoice_header(user, invoice_dict)
            await self._create_invoice_lines(user, invoice_header.id, invoice_lines)
            if data.document_type==DocumentType.INVOICE and data.send_to_tax_authority:
                await self.submit_invoice_to_tax_authority(user, invoice_header.id)
            return await self.get_invoice(user, invoice_header.id)
        except IntegrityError as e:
            raise_integrity_error(e)
        except BaseAppException as e:
            raise e

    async def update_invoice(self, user: UserInDB, invoice_id: int, data: SaleInvoiceUpdate) -> SaleInvoiceOut:
        try:
            invoice_header = await self._get_invoice_header(user, invoice_id)
            if not invoice_header:
                raise InvoiceNotFoundException()
            if invoice_header.status == InvoiceStatus.ISSUED or invoice_header.tax_authority_status == InvoiceTaxAuthorityStatus.ACCEPTED:
                raise InvoiceUpdateNotAllowed(detail="Cannot update an invoice that has been issued or accepted by the tax authority")
            # Calculate invoice amounts
            invoice_dict = await self._calculate_amounts(data)
            invoice_lines = invoice_dict.pop("invoice_lines")
            await self.repo.update_invoice(user.organization_id, user.id, invoice_id, invoice_dict)
            await self.repo.delete_invoice_lines(invoice_id)
            await self._create_invoice_lines(user, invoice_id, invoice_lines)
            if data.document_type==DocumentType.INVOICE and data.send_to_tax_authority:
                await self.submit_invoice_to_tax_authority(user, invoice_id)
            return await self.get_invoice(user, invoice_header.id)
        except IntegrityError as e:
            raise_integrity_error(e)
        except Exception as e:
            raise e

    async def update_invoice_status(self, user: UserInDB, invoice_id: int, data: SaleInvoiceUpdateStatus) -> SaleInvoiceOut:
        try:
            invoice_header = await self._get_invoice_header(user, invoice_id)
            if not invoice_header:
                raise InvoiceNotFoundException()
            if invoice_header.status != InvoiceStatus.DRAFT:
                raise InvoiceUpdateNotAllowed(detail="Only draft invoices can have their status updated")
            await self.repo.update_invoice(user.organization_id, user.id, invoice_id, {"status": data.status})
            if invoice_header.document_type==DocumentType.INVOICE and data.status == InvoiceStatus.ISSUED and data.send_to_tax_authority:
                await self.submit_invoice_to_tax_authority(user, invoice_id)
            return await self.get_invoice(user, invoice_header.id)
        except IntegrityError as e:
            raise_integrity_error(e)
        except Exception as e:
            raise e

    async def submit_invoice_to_tax_authority(self, user: UserInDB, invoice_id: int) -> SaleInvoiceOut:
        try:
            invoice = await self.get_invoice(user, invoice_id)
            if not invoice:
                raise InvoiceNotFoundException()
            if invoice.document_type != DocumentType.INVOICE:
                raise InvoiceSendNotAllowed(detail="Quotations can not be sent to tax authority")
            if invoice.status != InvoiceStatus.ISSUED:
                raise  InvoiceSendNotAllowed(detail="Only issued invoices can be sent to the tax authority")
            if invoice.tax_authority_status in {InvoiceTaxAuthorityStatus.ACCEPTED, InvoiceTaxAuthorityStatus.ACCEPTED_WITH_WARNINGS}:
                raise InvoiceUpdateNotAllowed(detail="Invoice has already been sent to the tax authority successfully")
            metadata = {}
            try:
                original_invoice = await self._get_invoice_header(user, invoice.original_invoice_id)
                metadata["original_invoice_number"] = original_invoice.invoice_number
            except InvoiceNotFoundException:
                metadata["original_invoice_number"] = None

            tax_authority_result = await self.tax_authority_service.sign_and_submit_invoice(user, invoice, metadata)
            await self.repo.update_invoice(
                user.organization_id, 
                user.id, 
                invoice.id, 
                {"tax_authority_status": tax_authority_result.status}
            )
            return await self.get_invoice(user, invoice.id)
        except IntegrityError as e:
            raise_integrity_error(e)
        except Exception as e:
            raise e

    async def convert_quotation_to_invoice(self, user: UserInDB, invoice_id: int, convert_data: QuotationConvert) -> SaleInvoiceOut:
        try:
            invoice_header = await self._get_invoice_header(user, invoice_id)
            if not invoice_header:
                raise InvoiceNotFoundException()
            if invoice_header.status == InvoiceStatus.ISSUED or invoice_header.document_type == DocumentType.INVOICE:
                raise InvoiceUpdateNotAllowed(detail="Only quotations with status DRAFT can be converted to invoices")
            # Duplicate the invoice
            db_invoice = await self.repo.get_invoice(user.organization_id, invoice_id)
            invoice_dict = invoice_header.model_dump()
            invoice_lines = await self._get_invoice_lines(user, invoice_id)
            invoice_lines_dict = []
            for line in invoice_lines:
                line_dict = line.model_dump()
                line_dict.update({"item_id": line.item.id})
                invoice_lines_dict.append(line_dict)
            invoice_dict.update({
                "document_type": DocumentType.INVOICE, 
                "customer_id": db_invoice.customer_id, 
                "invoice_lines": invoice_lines_dict,
                "status": convert_data.status,
                "send_to_tax_authority": convert_data.send_to_tax_authority,
            })
            data = SaleInvoiceCreate(**invoice_dict)
            await self.repo.update_invoice(user.organization_id, user.id, invoice_id, {"status": InvoiceStatus.ISSUED})
            return await self.create_invoice(user, data)
        except IntegrityError as e:
            raise_integrity_error(e)
        except Exception as e:
            raise e
        
    async def delete_invoice(self, user: UserInDB, invoice_id: int) -> None:
        try:
            db_invoice = await self._get_invoice_header(user, invoice_id)
            if not db_invoice:
                raise InvoiceNotFoundException()
            if db_invoice.status == InvoiceStatus.ISSUED or db_invoice.tax_authority_status == InvoiceTaxAuthorityStatus.ACCEPTED:
                raise InvoiceDeleteNotAllowed()
            await self.repo.delete_invoice(user.organization_id, invoice_id)
            return None
        except IntegrityError as e:
            raise_integrity_error(e)
        except Exception as e:
            raise e
    
    async def get_invoices(
        self,
        user: UserInDB,
        pagination: PagintationParams,
        filters: SaleInvoiceFilters,
    ) -> Tuple[int, List[SaleInvoiceOut]]:
        total, invoices = await self.repo.get_invoices_by_organization_id(
            user.organization_id,
            pagination.skip,
            pagination.limit,
            filters.model_dump(exclude_none=True),
        )
        result: List[SaleInvoiceOut] = []
        for invoice in invoices:
            result.append(await self.get_invoice(user, invoice.id))
        return total, result
