import uuid
from decimal import Decimal
from typing import Any, Dict, List, Tuple

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.enums import (
    InvoicingType,
    ZatcaPhase2Stage,
    TaxExemptionReasonCode,
    PartyIdentificationScheme,
    InvoiceType,
    InvoiceTypeCode,
    PaymentMeansCode,
    TaxCategory,
)
from src.core.utils.math_helper import round_decimal
from src.users.schemas import UserInDB
from src.items.services import ItemService
from src.suppliers.services import SupplierService
from src.suppliers.schemas import SupplierOut

from .repositories import BuyInvoiceRepository
from .exceptions import (
    BaseAppException,
    BuyInvoiceNotFoundException,
    raise_integrity_error,
)
from .schemas import (
    BuyInvoiceUpdate,
    PagintationParams,
    BuyInvoiceFilters,
    BuyInvoiceLineCreate,
    BuyInvoiceLineOut,
    BuyInvoiceHeaderOut,
    BuyInvoiceCreate,
    BuyInvoiceOut,
)
from src.core.consts import TAX_RATE

class BuyInvoiceService:
    def __init__(
        self,
        repo: BuyInvoiceRepository,
        supplier_service: SupplierService,
        item_service: ItemService,
    ) -> None:
        self.repo = repo
        self.supplier_service = supplier_service
        self.item_service = item_service

    # -------------------------------------------------------------------------
    # Private methods
    # -------------------------------------------------------------------------

    async def _get_invoice_header(self, user: UserInDB, invoice_id: int) -> BuyInvoiceHeaderOut:
        invoice = await self.repo.get_invoice(user.organization_id, invoice_id)
        if not invoice:
            raise BuyInvoiceNotFoundException()
        return BuyInvoiceHeaderOut.model_validate(invoice)

    async def _get_invoice_lines(self, user: UserInDB, invoice_id: int) -> List[BuyInvoiceLineOut]:
        invoice_lines = await self.repo.get_invoice_lines_by_invoice_id(invoice_id)
        result: List[BuyInvoiceLineOut] = []
        for line in invoice_lines:
            item = await self.item_service.get(user, line.item_id)
            line_out = BuyInvoiceLineOut.model_validate(line)
            line_out.item = item
            result.append(line_out)
        return result

    async def _get_invoice_supplier(self, user: UserInDB, invoice_id: int) -> SupplierOut | None:
        invoice = await self.repo.get_invoice(user.organization_id,invoice_id,)
        if not invoice:
            raise BuyInvoiceNotFoundException()
        return await self.supplier_service.get(user, invoice.supplier_id)
    
    async def _create_invoice_header(self, user: UserInDB, data: Dict[str, Any]) -> BuyInvoiceHeaderOut:
        invoice = await self.repo.create_invoice(
            user.organization_id,
            user.id,
            data,
        )
        return BuyInvoiceHeaderOut.model_validate(invoice)

    async def _create_invoice_lines(self, invoice_id: int, data: List[Dict[str, Any]]) -> None:
        invoice_lines = []
        for line in data:
            full_line = dict(line)
            full_line["invoice_id"] = invoice_id
            full_line["tax_rate"] = TAX_RATE[line["classified_tax_category"]]
            invoice_lines.append(full_line)
        await self.repo.create_invoice_lines(invoice_lines)

    async def _calculate_amounts(self, data: BuyInvoiceCreate) -> Dict[str, Any]:
        """
        Calculates amounts for invoice lines and totals.
        Returns a dict representing the new full invoice payload.
        """
        invoice: Dict[str, Any] = data.model_dump()
        # Line-level calculations
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

            line_dict = line.model_dump()
            line_dict.update(
                {
                    "line_extension_amount": line_extension_amount,
                    "tax_amount": tax_amount,
                    "rounding_amount": rounding_amount,
                }
            )
            invoice_lines.append(line_dict)

        invoice["invoice_lines"] = invoice_lines

        # Invoice totals
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

        invoice.update(
            {
                "line_extension_amount": invoice_line_extension_amount,
                "taxable_amount": invoice_taxable_amount,
                "tax_amount": invoice_tax_amount,
                "tax_inclusive_amount": invoice_tax_inclusive_amount,
            }
        )

        return invoice

    # -------------------------------------------------------------------------
    # Public methods
    # -------------------------------------------------------------------------
    async def get_new_invoice_number(self, user: UserInDB, invoice_id: int) -> str:
        invoice = await self.repo.get_invoice(
            user.organization_id,
            invoice_id,
        )
        if not invoice:
            raise BuyInvoiceNotFoundException()
        return f"INV-{str(invoice.icv).zfill(7)}"

    async def get_invoice(self, user: UserInDB, invoice_id: int) -> BuyInvoiceOut:
        header = await self._get_invoice_header(user, invoice_id)
        lines = await self._get_invoice_lines(user, invoice_id)
        supplier = await self._get_invoice_supplier(user, invoice_id)
        return BuyInvoiceOut(
            invoice_lines=lines,
            supplier=supplier,
            **header.model_dump(),
        )

    async def create_buy_invoice(self, user: UserInDB, data: BuyInvoiceCreate) -> BuyInvoiceOut:
        try:
            invoice_dict = await self._calculate_amounts(data)
            invoice_lines = invoice_dict.pop("invoice_lines")
            # Additional fields
            last_invoice = await self.repo.get_last_invoice(user.organization_id, user.branch_id, {})
            seq_number = (last_invoice.seq_number if last_invoice else 0) + 1
            header_uuid = uuid.uuid4()
            invoice_dict.update({
                "uuid": header_uuid,
                "seq_number": seq_number,
            })
            # Create header
            header = await self._create_invoice_header(user, invoice_dict)
            # Create lines
            await self._create_invoice_lines(header.id, invoice_lines)
            # Return full invoice
            return await self.get_invoice(user, header.id)
        except IntegrityError as e:
            raise_integrity_error(e)
        except BaseAppException as e:
            raise e
    
    async def update_invoice(self, user: UserInDB, invoice_id: int, data: BuyInvoiceUpdate) -> BuyInvoiceOut:
        try:
            invoice_header = await self._get_invoice_header(user, invoice_id)
            if not invoice_header:
                raise BuyInvoiceNotFoundException()
            # Calculate invoice amounts
            invoice_dict = await self._calculate_amounts(data)
            invoice_lines = invoice_dict.pop("invoice_lines")
            await self.repo.update_invoice(user.organization_id, user.id, invoice_id, invoice_dict)
            await self.repo.delete_invoice_lines(invoice_id)
            await self._create_invoice_lines(user, invoice_id, invoice_lines)
            invoice = await self.get_invoice(user, invoice_id)
            return invoice
        except IntegrityError as e:
            raise_integrity_error(e)
        except Exception as e:
            raise e
        
    async def delete_invoice(self, user: UserInDB, invoice_id: int) -> None:
        try:
            db_invoice = await self._get_invoice_header(user, invoice_id)
            if not db_invoice:
                raise BuyInvoiceNotFoundException()
            await self.repo.delete_invoice(user.organization_id, user.id, invoice_id)
            return None
        except IntegrityError as e:
            raise_integrity_error(e)
        except Exception as e:
            raise e
        
    async def get_invoices(
        self,
        user: UserInDB,
        pagination: PagintationParams,
        filters: BuyInvoiceFilters,
    ) -> Tuple[int, List[BuyInvoiceOut]]:
        total, invoices = await self.repo.get_invoices(
            user.organization_id,
            pagination.skip,
            pagination.limit,
            filters.model_dump(exclude_none=True),
        )

        # N+1, but consistent with how you’re composing full invoices now.
        # You can optimize later with joins if needed.
        result: List[BuyInvoiceOut] = []
        for invoice in invoices:
            result.append(await self.get_invoice(user, invoice.id))
        return total, result
