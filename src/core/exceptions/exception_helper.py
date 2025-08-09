from .exceptions import ForeignKeyViolationException, UniqueConstraintViolationException, NotNullConstraintViolationException, IntegrityErrorException

def raise_integrity_error(e: Exception):
    msg = str(e.orig).lower()
    if "foreign key" in msg:
        raise ForeignKeyViolationException()
    elif "unique constraint" in msg or "duplicate" in msg:
        raise UniqueConstraintViolationException()
    elif "not null" in msg:
        raise NotNullConstraintViolationException()
    else:
        raise IntegrityErrorException()