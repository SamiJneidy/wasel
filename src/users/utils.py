from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Creates a hash from a plain password"""
    return pwd_context.hash(password)