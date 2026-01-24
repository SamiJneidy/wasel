from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import and_, func, select, update, delete, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from .models import SaleInvoice, SaleInvoiceLine
from src.core.enums import ZatcaPhase2Stage, InvoiceType


class SaleInvoiceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_last_invoice(self, organization_id: int, branch_id: int, filters: dict = {}) -> SaleInvoice | None:
        stmt = select(SaleInvoice).where(SaleInvoice.organization_id == organization_id, SaleInvoice.branch_id == branch_id)
        for column, value in filters.items():
            c = getattr(SaleInvoice, column, None)
            if c is not None:
                stmt = stmt.where(c == value)
        stmt = stmt.order_by(SaleInvoice.id.desc()).limit(1)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_invoice_type_code_distinct_count(self, organization_id: int, invoice_type: InvoiceType) -> int:
        stmt = select(func.count(distinct(SaleInvoice.invoice_type_code))).where(
            and_(SaleInvoice.invoice_type == invoice_type, SaleInvoice.organization_id == organization_id)
        )
        result = await self.db.execute(stmt)
        return int(result.scalars().first() or 0)

    async def get_invoice_line(self, id: int) -> Optional[SaleInvoiceLine]:
        stmt = select(SaleInvoiceLine).where(SaleInvoiceLine.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_invoice_lines_by_invoice_id(self, invoice_id: int) -> List[SaleInvoiceLine]:
        stmt = select(SaleInvoiceLine).where(SaleInvoiceLine.invoice_id == invoice_id).order_by(SaleInvoiceLine.id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_invoice(self, organization_id: int, id: int) -> Optional[SaleInvoice]:
        stmt = select(SaleInvoice).where(
            and_(SaleInvoice.organization_id == organization_id, SaleInvoice.id == id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_invoices_by_organization_id(
        self,
        organization_id: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filters: Dict[str, Any] = {},
    ) -> Tuple[int, List[SaleInvoice]]:
        stmt = select(SaleInvoice).where(SaleInvoice.organization_id == organization_id)
        count_stmt = select(func.count(SaleInvoice.id)).where(SaleInvoice.organization_id == organization_id)

        simple_filters = {k: v for k, v in filters.items() if k not in {"issue_date_range_from", "issue_date_range_to", "invoice_number", "original_invoice_number"}}
        for k, v in simple_filters.items():
            col = getattr(SaleInvoice, k, None)
            if col is not None and v is not None:
                stmt = stmt.where(col == v)
                count_stmt = count_stmt.where(col == v)

        invoice_number = filters.get("invoice_number")
        if invoice_number:
            stmt = stmt.where(SaleInvoice.invoice_number.ilike(f"%{invoice_number}%"))
            count_stmt = count_stmt.where(SaleInvoice.invoice_number.ilike(f"%{invoice_number}%"))

        original_invoice_number = filters.get("original_invoice_number")
        if original_invoice_number:
            OriginalInvoice = aliased(SaleInvoice)
            stmt = stmt.join(
                OriginalInvoice,
                SaleInvoice.original_invoice_id == OriginalInvoice.id
            ).where(OriginalInvoice.invoice_number.ilike(f"%{original_invoice_number}%"))
            count_stmt = count_stmt.join(
                OriginalInvoice,
                SaleInvoice.original_invoice_id == OriginalInvoice.id
            ).where(OriginalInvoice.invoice_number.ilike(f"%{original_invoice_number}%"))

        issue_date_from = filters.get("issue_date_range_from")
        issue_date_to = filters.get("issue_date_range_to")
        if issue_date_from:
            stmt = stmt.where(SaleInvoice.issue_date >= issue_date_from)
            count_stmt = count_stmt.where(SaleInvoice.issue_date >= issue_date_from)
        if issue_date_to:
            stmt = stmt.where(SaleInvoice.issue_date <= issue_date_to)
            count_stmt = count_stmt.where(SaleInvoice.issue_date <= issue_date_to)

        count_result = await self.db.execute(count_stmt)
        total_rows = int(count_result.scalars().first() or 0)

        if skip is not None:
            stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)

        stmt = stmt.order_by(SaleInvoice.created_at.desc())
        result = await self.db.execute(stmt)
        return total_rows, list(result.scalars().all())

    async def create_invoice_lines(self, data: List[Dict[str, Any]]) -> None:
        self.db.add_all([SaleInvoiceLine(**row) for row in data])
        await self.db.flush()

    async def create_invoice_line(self, invoice_id: int, data: Dict[str, Any]) -> Optional[SaleInvoiceLine]:
        line = SaleInvoiceLine(**data)
        line.invoice_id = invoice_id
        self.db.add(line)
        await self.db.flush()
        await self.db.refresh(line)
        return line

    async def create_invoice(self, organization_id: int, user_id: int, data: Dict[str, Any]) -> Optional[SaleInvoice]:
        invoice = SaleInvoice(**data)
        invoice.user_id = user_id
        invoice.organization_id = organization_id
        invoice.created_by = user_id
        self.db.add(invoice)
        await self.db.flush()
        await self.db.refresh(invoice)
        return invoice

    async def update_invoice(self, organization_id: int, user_id: int, invoice_id: int, data: Dict[str, Any]) -> Optional[SaleInvoice]:
        stmt = (
            update(SaleInvoice)
            .where(SaleInvoice.organization_id == organization_id, SaleInvoice.id == invoice_id)
            .values(**data, updated_by=user_id)
            .returning(SaleInvoice)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()

    async def delete_invoice(self, organization_id: int, invoice_id: int) -> None:
        stmt = delete(SaleInvoice).where(SaleInvoice.organization_id == organization_id, SaleInvoice.id == invoice_id)
        await self.db.execute(stmt)

    async def delete_invoice_lines(self, invoice_id: int) -> None:
        stmt = delete(SaleInvoiceLine).where(SaleInvoiceLine.invoice_id == invoice_id)
        await self.db.execute(stmt)

    async def count_invoices(self, organization_id: int, filters: Dict[str, Any] = {}) -> int:
        stmt = select(func.count(SaleInvoice.id)).where(SaleInvoice.organization_id == organization_id)
        for k, v in filters.items():
            col = getattr(SaleInvoice, k, None)
            if col is not None and v is not None:
                stmt = stmt.where(col == v)

        result = await self.db.execute(stmt)
        return int(result.scalars().first() or 0)
