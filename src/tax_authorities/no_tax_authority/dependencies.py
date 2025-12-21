from fastapi import Depends
from typing import Annotated
from .services import NoTaxAuthorityService

def get_no_tax_authority_service() -> NoTaxAuthorityService:
    return NoTaxAuthorityService()