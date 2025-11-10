from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select, insert, update, delete
from datetime import datetime
from .models import Branch
from src.users.schemas import UserOut

class BranchRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def get(self, id: int) -> Branch | None:
        return self.db.query(Branch).filter(Branch.id==id).first()
    
    async def get_branches_for_organization(self, organization_id: int) -> list[Branch]:
        return self.db.query(Branch).filter(Branch.organization_id==organization_id).all()

    async def create(self, data: dict) -> Branch | None:
        branch = Branch(**data)
        self.db.add(branch)
        self.db.commit()
        self.db.refresh(branch)
        return branch

    async def update(self, id: int, data: dict) -> Branch | None:
        stmt = update(Branch).where(Branch.id==id).values(**data)
        self.db.execute(stmt)
        self.db.commit()
        return await self.get(id)
    
    async def delete(self, id: int) -> None:
        branch = self.db.query(Branch).filter(Branch.id==id)
        branch.delete()
        self.db.commit()
        return None
