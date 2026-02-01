from typing import Optional, Dict, Any
from sqlalchemy import select, update, delete
from src.core.database import AsyncSession
from .models import Organization
from src.branches.models import Branch
from src.core.enums import BranchTaxIntegrationStatus

class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Optional[Organization]:
        stmt = select(Organization).where(Organization.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_organizations(self) -> list[Organization]:
        stmt = select(Organization).order_by(Organization.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, data: Dict[str, Any]) -> Organization:
        organization = Organization(**data)
        self.db.add(organization)
        await self.db.flush()
        await self.db.refresh(organization)
        return organization
    
    async def create_main_branch(self, data: Dict[str, Any]) -> Branch:
        branch = Branch(**data)
        self.db.add(branch)
        await self.db.flush()
        await self.db.refresh(branch)
        return branch
    
    async def change_branches_tax_integration_status(self, organization_id: int, new_status: BranchTaxIntegrationStatus) -> None:
        stmt = (
            update(Branch)
            .where(Branch.organization_id == organization_id)
            .values(tax_integration_status=new_status)
        )
        await self.db.execute(stmt)
        await self.db.flush()
        
    async def update(self, id: int, data: Dict[str, Any]) -> Optional[Organization]:
        stmt = (
            update(Organization)
            .where(Organization.id == id)
            .values(**data)
            .returning(Organization)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        row = result.fetchone()
        return row[0] if row else None

    async def delete(self, id: int) -> None:
        stmt = delete(Organization).where(Organization.id == id)
        await self.db.execute(stmt)
        return None
