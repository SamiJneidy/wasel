from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select, insert, update, delete
from datetime import datetime
from .models import Organization, Branch
from src.users.schemas import UserOut

class OrganizationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def get(self, id: int) -> Organization | None:
        return self.db.query(Organization).filter(Organization.id==id).first()
    
    async def get_organizations(self) -> list[Organization]:
        return self.db.query(Organization).all()

    async def create(self, data: dict) -> Organization | None:
        organization = Organization(**data)
        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)
        return organization
    
    async def update(self, id: int, data: dict) -> Organization | None:
        stmt = update(Organization).where(Organization.id==id).values(**data)
        self.db.execute(stmt)
        self.db.commit()
        return await self.get(id)
    
    async def delete(self, id: int) -> None:
        organization = self.db.query(Organization).filter(Organization.id==id)
        organization.delete()
        self.db.commit()
        return None
