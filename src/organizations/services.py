from src.core.config import settings
from .schemas import OrganizationOut, OrganizationCreate, OrganizationUpdate
from .repositories import OrganizationRepository
from .exceptions import OrganizationNotFoundException

class OrganizationService:
    def __init__(self, organization_repo: OrganizationRepository):
        self.organization_repo = organization_repo


    async def get(self, id: int) -> OrganizationOut:
        organization = await self.organization_repo.get(id)
        if not organization:
            raise OrganizationNotFoundException()
        return OrganizationOut.model_validate(organization)
    
    async def get_organizations_for_user(self) -> list[OrganizationOut]:
        query_set = await self.organization_repo.get_organizations()
        result = [
            OrganizationOut.model_validate(organization) for organization in query_set
        ]
        return result
    
    async def create(self, data: OrganizationCreate) -> OrganizationOut:
        organization = await self.organization_repo.create(data.model_dump())
        return OrganizationOut.model_validate(organization)
    
    async def update(self, id: int, data: OrganizationUpdate) -> OrganizationOut:
        organization = await self.organization_repo.update(id, data.model_dump())
        if not organization:
            raise OrganizationNotFoundException()
        return OrganizationOut.model_validate(organization)
    
    async def delete(self, id: int) -> None:
        organization = await self.get(id)
        await self.organization_repo.delete(id)
        return None
    