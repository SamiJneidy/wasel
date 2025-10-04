from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select, insert, update, delete
from datetime import datetime
from .models import Supplier
from src.users.schemas import UserOut

class SupplierRepository:
    def __init__(self, db: Session, user: UserOut):
        self.db = db
        self.user = user
        

    async def get(self, id: int) -> Supplier | None:
        return self.db.query(Supplier).filter(Supplier.id==id, Supplier.user_id==self.user.id).first()
    
    async def get_suppliers(self) -> list[Supplier]:
        return self.db.query(Supplier).filter(Supplier.user_id==self.user.id).all()

    async def create(self, data: dict) -> Supplier | None:
        supplier = Supplier(**data)
        supplier.user_id = self.user.id
        supplier.created_by = self.user.id
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    async def update(self, id: int, data: dict) -> Supplier | None:
        stmt = update(Supplier).where(Supplier.id==id, Supplier.user_id==self.user.id).values(updated_by=self.user.id, **data)
        self.db.execute(stmt)
        self.db.commit()
        return await self.get(id)
    
    async def delete(self, id: int) -> None:
        supplier = self.db.query(Supplier).filter(Supplier.id==id, Supplier.user_id==self.user.id)
        supplier.delete()
        self.db.commit()
        return None
