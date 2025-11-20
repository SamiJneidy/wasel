from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, select, insert, update, delete

class TokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
