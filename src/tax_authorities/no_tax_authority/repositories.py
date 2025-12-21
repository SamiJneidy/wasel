from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, insert, select, update, delete, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import ZatcaPhase2Stage, InvoiceType

