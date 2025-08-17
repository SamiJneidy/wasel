from decimal import Decimal, ROUND_HALF_UP

def round_decimal(value, places=2):
    """Round a value to specified decimal places using proper financial rounding"""
    return Decimal(str(value)).quantize(
        Decimal(f'1.{"0"*places}'), 
        rounding=ROUND_HALF_UP
    )