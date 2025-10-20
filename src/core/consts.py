from .config import settings
from decimal import Decimal

TAX_RATE = {
    'S': Decimal(settings.STANDARD_TAX_RATE),
    'Z': Decimal("0"),
    'E': Decimal("0"),
    'O': Decimal("0")
}