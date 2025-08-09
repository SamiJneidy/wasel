from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select, insert, update, delete
from datetime import datetime
from .models import Item
from src.users.schemas import UserOut

class ItemRepository:
    def __init__(self, db: Session, user: UserOut):
        self.db = db
        self.user = user
    
    async def get(self, id: int) -> Item | None:
        return self.db.query(Item).filter(Item.id==id, Item.user_id==self.user.id).first()
    
    async def get_items(self) -> list[Item]:
        return self.db.query(Item).filter(Item.user_id==self.user.id).all()

    async def create(self, data: dict) -> Item | None:
        item = Item(**data)
        item.user_id = self.user.id
        item.created_by = self.user.id
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    async def update(self, id: int, data: dict) -> Item | None:
        stmt = update(Item).where(Item.id==id, Item.user_id==self.user.id).values(updated_by=self.user.id, **data)
        self.db.execute(stmt)
        self.db.commit()
        return await self.get(id)
    
    async def delete(self, id: int) -> None:
        item = self.db.query(Item).filter(Item.id==id, Item.user_id==self.user.id)
        item.delete()
        self.db.commit()
        return None
