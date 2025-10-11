from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select, insert, update, delete
from datetime import datetime
from .models import Customer
from src.users.schemas import UserOut

class CustomerRepository:
    def __init__(self, db: Session, user: UserOut):
        self.db = db
        self.user = user
        

    async def get(self, id: int) -> Customer | None:
        return self.db.query(Customer).filter(Customer.id==id, Customer.user_id==self.user.id).first()
    
    async def get_customers(self, skip: int = None, limit: int = None, filters: dict = {}) -> list[Customer]:
        query = self.db.query(Customer).filter(Customer.user_id==self.user.id)
        for k, v in filters.items():
            column = getattr(Customer, k, None)
            if column is not None:
                print(k, v)
                query = query.filter(func.lower(column).like(f"%{v.lower()}%"))
        total_rows = query.count()
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        return total_rows, query.all()

    async def create(self, data: dict) -> Customer | None:
        customer = Customer(**data)
        customer.user_id = self.user.id
        customer.created_by = self.user.id
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    async def update(self, id: int, data: dict) -> Customer | None:
        stmt = update(Customer).where(Customer.id==id, Customer.user_id==self.user.id).values(updated_by=self.user.id, **data)
        self.db.execute(stmt)
        self.db.commit()
        return await self.get(id)
    
    async def delete(self, id: int) -> None:
        customer = self.db.query(Customer).filter(Customer.id==id, Customer.user_id==self.user.id)
        customer.delete()
        self.db.commit()
        return None
