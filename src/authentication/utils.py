import secrets
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Creates a hash from a plain password"""
    return pwd_context.hash(password)

def generate_random_code(length: int = 6) -> str:
    """Generates a random code with a specified length (6 by default)."""
    return "".join(secrets.choice("0123456789") for _ in range(length))