import json
import uuid
from src.core.config import settings
from src.users.schemas import UserInDB, UserOut
from src.users.services import UserService
from src.items.services import ItemService
from src.suppliers.services import SupplierService
from src.core.enums import InvoicingType, Stage, TaxExemptionReasonCode, PartyIdentificationScheme, InvoiceType, InvoiceTypeCode, PaymentMeansCode, TaxCategory
from src.suppliers.schemas import SupplierOut
from .schemas import (
    PagintationParams,
    BuyInvoiceFilters,
    SuccessfulResponse,
    BuyInvoiceLineCreate, BuyInvoiceLineOut,
    BuyInvoiceHeaderOut, BuyInvoiceCreate, BuyInvoiceOut,
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .repositories import BuyInvoiceRepository
from .exceptions import BaseAppException, BuyInvoiceNotFoundException, IntegrityErrorException, raise_integrity_error
from src.core.utils.math_helper import round_decimal
from decimal import Decimal

class BuyInvoiceService:
    def __init__(self, db: Session, user: UserOut, supplier_service: SupplierService, item_service: ItemService, user_service: UserService, buy_invoice_repository: BuyInvoiceRepository):
        self.db = db
        self.user = user
        self.supplier_service = supplier_service
        self.item_service = item_service
        self.user_service = user_service
        self.buy_invoice_repository = buy_invoice_repository


    async def get_new_invoice_number(self, user_id: int, invoice_id: int) -> str:
        invoice = await self.buy_invoice_repository.get_invoice(user_id, invoice_id)
        return f"INV-{str(invoice.icv).zfill(7)}"


    async def get_invoice_lines(self, invoice_id: int) -> list[BuyInvoiceLineOut]:
        invoice_lines = await self.buy_invoice_repository.get_invoice_lines_by_invoice_id(invoice_id)
        result = []
        for line in invoice_lines:
            item = await self.item_service.get(line.item_id)
            full_line = BuyInvoiceLineOut.model_validate(line)
            full_line.item = item
            result.append(full_line)
        return result


    async def get_invoice_supplier(self, invoice_id: int) -> SupplierOut | None:
        db_invoice = await self.buy_invoice_repository.get_invoice(self.user.id, invoice_id)
        return await self.supplier_service.get(db_invoice.supplier_id)


    async def get_invoice_header(self, invoice_id: int) -> BuyInvoiceHeaderOut:
        invoice_header = await self.buy_invoice_repository.get_invoice(self.user.id, invoice_id)
        return BuyInvoiceHeaderOut.model_validate(invoice_header)


    async def get_invoice(self, invoice_id: int) -> BuyInvoiceOut:
        invoice_header = await self.get_invoice_header(invoice_id)
        invoice_lines = await self.get_invoice_lines(invoice_id)
        invoice_supplier = await self.get_invoice_supplier(invoice_id)
        return BuyInvoiceOut(invoice_lines=invoice_lines, supplier=invoice_supplier, **invoice_header.model_dump())


    async def create_invoice_header(self, data: dict) -> BuyInvoiceHeaderOut:
        invoice_header = await self.buy_invoice_repository.create_invoice(self.user.id, data)
        return BuyInvoiceHeaderOut.model_validate(invoice_header)


    async def create_invoice_lines(self, invoice_id: int, data: list[dict]) -> None:
        invoice_lines = data.copy()
        for line in invoice_lines:
            line.update({"invoice_id": invoice_id})
        await self.buy_invoice_repository.create_invoice_lines(data)


    async def calculate_amounts(self, data: BuyInvoiceCreate) -> dict:
        """Calculates amounts for invoice lines and totals. Returns a dict representing the new full invoice."""
        invoice = data.model_dump()
        # Create invoice lines
        invoice_lines = []
        for line in data.invoice_lines:

            item_price_afer_price_discount = round(line.item_price - line.price_discount, 2)
            total = round(item_price_afer_price_discount * line.quantity - line.discount_amount, 2)
            
            if(line.price_includes_tax == True):
                line_extension_amount = round_decimal((total * 100) / (line.tax_rate + 100), 2)
                tax_amount = round_decimal(total - line_extension_amount, 2)
            else:
                line_extension_amount = total
                tax_amount = round_decimal(line_extension_amount * line.tax_rate / 100, 2)
                
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
        tax_categories = set(line["tax_rate"] for line in invoice_lines)
        if(len(tax_categories) == 1):
            tax_rate = tax_categories.pop()
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
        })

        return invoice


    async def create_buy_invoice(self, data: BuyInvoiceCreate) -> BuyInvoiceOut:
        try:
            invoice_dict = await self.calculate_amounts(data)
            invoice_lines = invoice_dict.pop("invoice_lines")
            invoice = await self.create_invoice_header(invoice_dict)
            
            # Create invoice lines
            await self.create_invoice_lines(invoice.id, invoice_lines)
        
            # Add additional invoice fields
            invoice_dict.update({
                "uuid": uuid.uuid4(),
            })

            self.db.commit()
            return await self.get_invoice(invoice.id)
        except IntegrityError as e:
            print(e)
            self.db.rollback()
            raise_integrity_error(e)
        except BaseAppException as e:
            self.db.rollback()
            raise e
    

    async def get_invoices(self, pagination: PagintationParams, filters: BuyInvoiceFilters) -> tuple[int, list[BuyInvoiceOut]]:
        total, invoices = await self.buy_invoice_repository.get_invoices_by_user_id(self.user.id, self.user.stage, pagination.skip, pagination.limit, filters.model_dump(exclude_none=True))
        return total, [await self.get_invoice(invoice.id) for invoice in invoices]