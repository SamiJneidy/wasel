from datetime import datetime
from typing import Any, Dict, List, Tuple
import uuid
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from src.customers.schemas import CustomerOut
from src.core.enums import DocumentType, InvoiceType, InvoiceTypeCode, TaxAuthority
from src.core.utils.math_helper import round_decimal
from src.core.consts import TAX_RATE, KSA_TZ
from src.users.schemas import UserInDB
from src.items.services import ItemService
from src.customers.services import CustomerService
from src.tax_authorities.services import TaxAuthorityService
from ..repositories import SaleInvoiceRepository
from ..schemas import (
    PagintationParams,
    SaleInvoiceFilters,
    SaleInvoiceLineCreate,
    SaleInvoiceLineOut,
    SaleInvoiceHeaderOut,
    SaleInvoiceCreate,
    SaleInvoiceOut,
    SaleInvoiceUpdate,
)
from ..exceptions import (
    BaseAppException,
    InvoiceSendNotAllowed,
    InvoiceNotFoundException,
    InvoiceUpdateNotAllowed,
    InvoiceDeleteNotAllowed,
    raise_integrity_error,
)
class SaleInvoiceServiceRaw:
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
        customer_service: CustomerService,
        item_service: ItemService,
    ) -> None:
        self.repo = repo
        self.customer_service = customer_service
        self.item_service = item_service

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
        last_invoice = await self.repo.get_last_invoice(user.organization_id, user.default_branch_id, filters)
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
        return invoice
    
    async def _get_invoice_lines(self, user: UserInDB, invoice_id: int) -> List[SaleInvoiceLineOut]:
        invoice_lines = await self.repo.get_invoice_lines_by_invoice_id(invoice_id)
        result: List[SaleInvoiceLineOut] = []
        for line in invoice_lines:
            item = await self.item_service.get(user, line.item_id)
            line_out = SaleInvoiceLineOut.model_validate(line)
            line_out.item = item
            result.append(line_out)
        return result

    async def _get_invoice_lines(self, user: UserInDB, invoice_id: int) -> List[SaleInvoiceLineOut]:
        invoice_lines = await self.repo.get_invoice_lines_by_invoice_id(invoice_id)
        result: List[SaleInvoiceLineOut] = []
        for line in invoice_lines:
            item = await self.item_service.get(user, line.item_id)
            line_out = SaleInvoiceLineOut.model_validate(line)
            line_out.item = item
            result.append(line_out)
        return result

    async def _get_invoice_customer(self, user: UserInDB, invoice_id: int) -> CustomerOut | None:
        invoice = await self.repo.get_invoice(user.organization_id, invoice_id)
        if not invoice:
            raise InvoiceNotFoundException()
        if not invoice.customer_id:
            return None
        return await self.customer_service.get(user, invoice.customer_id)

    async def _create_invoice_header(self, user: UserInDB, data: Dict[str, Any]) -> SaleInvoiceHeaderOut:
        invoice = await self.repo.create_invoice(user.organization_id, user.id, data)
        return SaleInvoiceHeaderOut.model_validate(invoice)

    async def _create_invoice_lines(self, user: UserInDB, invoice_id: int, data: List[Dict[str, Any]]) -> None:
        for line in data:
            line["tax_rate"] = TAX_RATE[line["classified_tax_category"]]
            line_metadata = line.pop("tax_authority_data", None)
            db_line = await self.repo.create_invoice_line(invoice_id, line)

    async def _calculate_amounts(self, data: SaleInvoiceCreate) -> Dict[str, Any]:
        invoice: Dict[str, Any] = data.model_dump(exclude={"tax_authority_data"}, exclude_none=True)
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def get_invoice(self, user: UserInDB, invoice_id: int) -> SaleInvoiceOut:
        header = await self._get_invoice_header(user, invoice_id)
        lines = await self._get_invoice_lines(user, invoice_id)
        customer = await self._get_invoice_customer(user, invoice_id)
        return SaleInvoiceOut(
            invoice_lines=lines,
            customer=customer,
            **header.model_dump(),
        )

    async def create_invoice(self, user: UserInDB, data: SaleInvoiceCreate) -> SaleInvoiceOut:
        try:
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
                "is_locked": data.document_type==DocumentType.INVOICE,
                "completed_tax_integration": True,
                "invoice_number": invoice_number,
                "seq_number": seq
            })
            invoice_header = await self._create_invoice_header(user, invoice_dict)
            await self._create_invoice_lines(user, invoice_header.id, invoice_lines)
            invoice = await self.get_invoice(user, invoice_header.id)
            return invoice
        except IntegrityError as e:
            raise_integrity_error(e)
        except BaseAppException as e:
            raise e
