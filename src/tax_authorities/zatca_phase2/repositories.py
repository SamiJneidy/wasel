from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, insert, select, update, delete, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ZatcaBranchMetadata, ZatcaCSID, ZatcaSaleInvoiceLineMetadata, ZatcaPhase2SaleInvoiceMetadata
from src.core.enums import ZatcaPhase2Stage, InvoiceType


class ZatcaRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_csid(self, id: int, stage: ZatcaPhase2Stage) -> ZatcaCSID | None:
        stmt = (
            select(ZatcaCSID)
            .where(ZatcaCSID.id == id, ZatcaCSID.stage == stage)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_csid_by_branch(self, organization_id: int, branch_id: int, stage: ZatcaPhase2Stage) -> ZatcaCSID | None:
        stmt = (
            select(ZatcaCSID)
            .where(ZatcaCSID.organization_id == organization_id, ZatcaCSID.branch_id == branch_id, ZatcaCSID.stage == stage)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_csid(self, organizaion_id: int, branch_id: int, data: dict) -> ZatcaCSID | None:
        csid = ZatcaCSID(**data)
        csid.organization_id = organizaion_id
        csid.branch_id = branch_id
        self.db.add(csid)
        await self.db.flush()
        await self.db.refresh(csid)
        return csid

    async def update_csid(self, user_id: int, id: int, data: dict) -> ZatcaCSID | None:
        stmt = (
            update(ZatcaCSID)
            .where(ZatcaCSID.id == id)
            .values(user_id=user_id, **data)
            .returning(ZatcaCSID)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()

    async def delete_csid(self, id: int) -> None:
        stmt = delete(ZatcaCSID).where(ZatcaCSID.id == id)
        await self.db.execute(stmt)
        await self.db.flush()
        return None

    async def create_branch_metadata(self, user_id: int, organization_id: int, branch_id: int, data: dict) -> ZatcaBranchMetadata:
        branch = ZatcaBranchMetadata(**data)
        branch.created_by = user_id
        branch.organization_id = organization_id
        branch.branch_id = branch_id
        self.db.add(branch)
        await self.db.flush()
        await self.db.refresh(branch)
        return branch

    async def update_pih_and_icv(self, branch_id: int, pih: str) -> ZatcaBranchMetadata | None:
        stmt = (
            update(ZatcaBranchMetadata)
            .where(ZatcaBranchMetadata.branch_id == branch_id)
            .values(pih=pih, icv=ZatcaBranchMetadata.icv+1)
            .returning(ZatcaBranchMetadata)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()
    
    async def get_branch_metadata(self, id: int) -> ZatcaBranchMetadata | None:
        stmt = select(ZatcaBranchMetadata).where(ZatcaBranchMetadata.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_branch_metadata_by_branch(self, branch_id: int) -> ZatcaBranchMetadata | None:
        stmt = (select(ZatcaBranchMetadata).where(ZatcaBranchMetadata.branch_id == branch_id))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_branch_stage(self, organization_id: int, branch_id: int) -> Optional[str]:
        stmt = select(ZatcaBranchMetadata.stage).where(
            and_(ZatcaBranchMetadata.organization_id == organization_id, ZatcaBranchMetadata.branch_id == branch_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_pih(self, organization_id: int, branch_id: int, stage: ZatcaPhase2Stage) -> Optional[str]:
        stmt = select(ZatcaBranchMetadata.pih).where(
            and_(ZatcaBranchMetadata.organization_id == organization_id, ZatcaBranchMetadata.branch_id == branch_id, ZatcaBranchMetadata.stage == stage)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_icv(self, organization_id: int, branch_id: int, stage: ZatcaPhase2Stage) -> Optional[int]:
        stmt = select(ZatcaBranchMetadata.icv).where(
            and_(ZatcaBranchMetadata.organization_id == organization_id, ZatcaBranchMetadata.branch_id == branch_id, ZatcaBranchMetadata.stage == stage)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_invoice_metadata(self, invoice_id: int, data: dict) -> ZatcaPhase2SaleInvoiceMetadata:
        stmt = insert(ZatcaPhase2SaleInvoiceMetadata).values(invoice_id=invoice_id, **data).returning(ZatcaPhase2SaleInvoiceMetadata)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()

    async def create_line_metadata(self, invoice_id: int, invoice_line_id: int, data: dict) -> ZatcaSaleInvoiceLineMetadata:
        stmt = insert(ZatcaSaleInvoiceLineMetadata).values(invoice_id=invoice_id, invoice_line_id=invoice_line_id, **data).returning(ZatcaSaleInvoiceLineMetadata)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.scalars().first()
    
    async def get_invoice_metadata(self, invoice_id: int) -> Optional[ZatcaPhase2SaleInvoiceMetadata]:
        stmt = select(ZatcaPhase2SaleInvoiceMetadata).where(ZatcaPhase2SaleInvoiceMetadata.invoice_id==invoice_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def get_line_metadata(self, invoice_line_id: int) -> Optional[ZatcaSaleInvoiceLineMetadata]:
        stmt = select(ZatcaSaleInvoiceLineMetadata).where(ZatcaSaleInvoiceLineMetadata.invoice_line_id==invoice_line_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def delete_invoice_metadata(self, invoice_id: int) -> None:
        stmt = delete(ZatcaPhase2SaleInvoiceMetadata).where(ZatcaPhase2SaleInvoiceMetadata.invoice_id==invoice_id)
        await self.db.execute(stmt)
        await self.db.flush()
        return None
    
    async def delete_lines_metadata(self, invoice_id: int) -> None:
        stmt = delete(ZatcaSaleInvoiceLineMetadata).where(ZatcaSaleInvoiceLineMetadata.invoice_id==invoice_id)
        await self.db.execute(stmt)
        await self.db.flush()
        return None
    

    # async def get_invoice_stage_code_distinct_count(self, organization_id: int, invoice_stage: InvoiceType) -> int:
    #     stmt = select(func.count(distinct(SaleInvoice.invoice_stage_code))).where(
    #         and_(SaleInvoice.invoice_stage == invoice_stage, SaleInvoice.organization_id == organization_id)
    #     )
    #     result = await self.db.execute(stmt)
    #     return int(result.scalars().first() or 0)

    # async def get_invoice_line(self, id: int) -> Optional[SaleInvoiceLine]:
    #     stmt = select(SaleInvoiceLine).where(SaleInvoiceLine.id == id)
    #     result = await self.db.execute(stmt)
    #     return result.scalars().first()

    # async def get_invoice_lines_by_invoice_id(self, invoice_id: int) -> List[SaleInvoiceLine]:
    #     stmt = select(SaleInvoiceLine).where(SaleInvoiceLine.invoice_id == invoice_id)
    #     result = await self.db.execute(stmt)
    #     return list(result.scalars().all())

    # async def get_invoice(self, organization_id: int, id: int) -> Optional[SaleInvoice]:
    #     stmt = select(SaleInvoice).where(
    #         and_(SaleInvoice.organization_id == organization_id, SaleInvoice.id == id)
    #     )
    #     result = await self.db.execute(stmt)
    #     return result.scalars().first()

    # async def get_invoices_by_organization_id(
    #     self,
    #     organization_id: int,
    #     skip: Optional[int] = None,
    #     limit: Optional[int] = None,
    #     filters: Dict[str, Any] = {},
    # ) -> Tuple[int, List[SaleInvoice]]:
    #     stmt = select(SaleInvoice).where(SaleInvoice.user_id == organization_id)
    #     count_stmt = select(func.count(SaleInvoice.id)).where(SaleInvoice.user_id == organization_id)

    #     simple_filters = {
    #         k: v for k, v in filters.items() if k not in {"issue_date_range_from", "issue_date_range_to"}
    #     }

    #     for k, v in simple_filters.items():
    #         col = getattr(SaleInvoice, k, None)
    #         if col is not None and v is not None:
    #             stmt = stmt.where(col == v)
    #             count_stmt = count_stmt.where(col == v)

    #     issue_date_from = filters.get("issue_date_range_from")
    #     issue_date_to = filters.get("issue_date_range_to")

    #     if issue_date_from is not None:
    #         stmt = stmt.where(SaleInvoice.issue_date >= issue_date_from)
    #         count_stmt = count_stmt.where(SaleInvoice.issue_date >= issue_date_from)

    #     if issue_date_to is not None:
    #         stmt = stmt.where(SaleInvoice.issue_date <= issue_date_to)
    #         count_stmt = count_stmt.where(SaleInvoice.issue_date <= issue_date_to)

    #     count_result = await self.db.execute(count_stmt)
    #     total_rows = int(count_result.scalars().first() or 0)

    #     if skip is not None:
    #         stmt = stmt.offset(skip)
    #     if limit is not None:
    #         stmt = stmt.limit(limit)

    #     result = await self.db.execute(stmt)
    #     return total_rows, list(result.scalars().all())

    # async def create_invoice_lines(self, data: List[Dict[str, Any]]) -> None:
    #     self.db.add_all([SaleInvoiceLine(**row) for row in data])
    #     await self.db.flush()

    # async def create_invoice(self, organization_id: int, user_id: int, data: Dict[str, Any]) -> Optional[SaleInvoice]:
    #     invoice = SaleInvoice(**data)
    #     invoice.user_id = user_id
    #     invoice.organization_id = organization_id
    #     invoice.created_by = user_id
    #     self.db.add(invoice)
    #     await self.db.flush()
    #     await self.db.refresh(invoice)
    #     return invoice

    # async def update_invoice(self, organization_id: int, invoice_id: int, data: Dict[str, Any]) -> Optional[SaleInvoice]:
    #     stmt = (
    #         update(SaleInvoice)
    #         .where(SaleInvoice.organization_id == organization_id, SaleInvoice.id == invoice_id)
    #         .values(**data)
    #         .returning(SaleInvoice)
    #     )
    #     result = await self.db.execute(stmt)
    #     await self.db.flush()
    #     return result.scalars().first()

    # async def delete_invoice(self, organization_id: int, invoice_id: int) -> None:
    #     stmt = delete(SaleInvoice).where(SaleInvoice.organization_id == organization_id, SaleInvoice.id == invoice_id)
    #     await self.db.execute(stmt)

    # async def delete_invoice_lines(self, invoice_id: int) -> None:
    #     stmt = delete(SaleInvoiceLine).where(SaleInvoiceLine.invoice_id == invoice_id)
    #     await self.db.execute(stmt)

    # async def count_invoices(self, organization_id: int, filters: Dict[str, Any] = {},) -> int:
    #     stmt = select(func.count(SaleInvoice.id)).where(SaleInvoice.organization_id == organization_id)
    #     for k, v in filters.items():
    #         col = getattr(SaleInvoice, k, None)
    #         if col is not None and v is not None:
    #             stmt = stmt.where(col == v)

    #     result = await self.db.execute(stmt)
    #     return int(result.scalars().first() or 0)
