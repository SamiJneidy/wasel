from decimal import Decimal, ROUND_HALF_UP
from math import ceil

def round_decimal(value, places=2):
    """Round a value to specified decimal places using proper financial rounding"""
    return Decimal(str(value)).quantize(
        Decimal(f'1.{"0"*places}'), 
        rounding=ROUND_HALF_UP
    )

def calc_total_pages(total_rows: int, limit: int | None = None) -> int:
    return ceil(total_rows / limit) if limit is not None else 1