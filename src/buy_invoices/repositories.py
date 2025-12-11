from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, select, update, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from .models import BuyInvoice, BuyInvoiceLine


class BuyInvoiceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_last_invoice(self, organization_id: int) -> Optional[BuyInvoice]:
        stmt = (
            select(BuyInvoice)
            .where(BuyInvoice.organization_id == organization_id)
            .order_by(BuyInvoice.id.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_invoice(
        self,
        organization_id: int,
        id: int,
    ) -> Optional[BuyInvoice]:
        stmt = (
            select(BuyInvoice)
            .where(
                and_(
                    BuyInvoice.id == id,
                    BuyInvoice.organization_id == organization_id,
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def count_invoices(self, organization_id: int) -> int:
        # Same as get_invoice_count; keep one if you want.
        stmt = (
            select(func.count(BuyInvoice.id))
            .select_from(BuyInvoice)
            .where(BuyInvoice.organization_id == organization_id)
        )
        result = await self.db.execute(stmt)
        return int(result.scalars().first() or 0)

    async def get_invoice_line(self, id: int) -> Optional[BuyInvoiceLine]:
        stmt = select(BuyInvoiceLine).where(BuyInvoiceLine.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_invoice_lines_by_invoice_id(
        self,
        invoice_id: int,
    ) -> List[BuyInvoiceLine]:
        stmt = select(BuyInvoiceLine).where(BuyInvoiceLine.invoice_id == invoice_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_invoice_lines(self, data: List[Dict[str, Any]]) -> None:
        self.db.add_all([BuyInvoiceLine(**row) for row in data])
        await self.db.flush()

    async def get_invoices(
        self,
        organization_id: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filters: Dict[str, Any] = {},
    ) -> Tuple[int, List[BuyInvoice]]:
        stmt = select(BuyInvoice).where(
            BuyInvoice.organization_id == organization_id
        )
        count_stmt = (
            select(func.count(BuyInvoice.id))
            .select_from(BuyInvoice)
            .where(BuyInvoice.organization_id == organization_id)
        )

        simple_filters = {
            k: v
            for k, v in filters.items()
            if k not in {"issue_date_range_from", "issue_date_range_to"}
        }

        for k, v in simple_filters.items():
            column = getattr(BuyInvoice, k, None)
            if column is not None and v is not None:
                stmt = stmt.where(column == v)
                count_stmt = count_stmt.where(column == v)

        issue_date_from = filters.get("issue_date_range_from")
        issue_date_to = filters.get("issue_date_range_to")

        if issue_date_from is not None:
            stmt = stmt.where(BuyInvoice.issue_date >= issue_date_from)
            count_stmt = count_stmt.where(BuyInvoice.issue_date >= issue_date_from)

        if issue_date_to is not None:
            stmt = stmt.where(BuyInvoice.issue_date <= issue_date_to)
            count_stmt = count_stmt.where(BuyInvoice.issue_date <= issue_date_to)

        # total count
        count_result = await self.db.execute(count_stmt)
        total_rows = int(count_result.scalars().first() or 0)

        # pagination
        if skip is not None:
            stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.db.execute(stmt)
        invoices = list(result.scalars().all())

        return total_rows, invoices

    async def create_invoice(
        self,
        organization_id: int,
        user_id: int,
        data: Dict[str, Any],
    ) -> Optional[BuyInvoice]:
        invoice = BuyInvoice(**data)
        invoice.organization_id = organization_id
        invoice.created_by = user_id

        self.db.add(invoice)
        await self.db.flush()
        await self.db.refresh(invoice)
        return invoice

    async def update_invoice(
        self,
        organization_id: int,
        user_id: int,
        id: int,
        data: Dict[str, Any],
    ) -> Optional[BuyInvoice]:
        stmt = (
            update(BuyInvoice)
            .where(BuyInvoice.id == id, BuyInvoice.organization_id == organization_id)
            .values(updated_by=user_id, **data)
            .returning(BuyInvoice)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()
