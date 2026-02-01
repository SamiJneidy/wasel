from typing import Optional
from src.core.config import settings
from src.branches.repositories import BranchRepository
from src.branches.schemas import BranchCreate, BranchOut
from .schemas import OrganizationOut, OrganizationCreate, OrganizationUpdate
from .repositories import OrganizationRepository
from .exceptions import OrganizationNotFoundException, TaxAuthorityUpdateNotAllowedException
from src.core.enums import BranchTaxIntegrationStatus, TaxAuthority
from src.core.schemas.context import RequestContext

class OrganizationService:
    def __init__(self, organization_repo: OrganizationRepository):
        self.organization_repo = organization_repo

    async def get_organization(self, id: int) -> OrganizationOut:
        organization = await self.organization_repo.get(id)
        if not organization:
            raise OrganizationNotFoundException()
        # Optional: ensure organization belongs to current_user
        # if current_user and organization.id != current_user.organization_id:
        #     raise OrganizationNotFoundException()
        return OrganizationOut.model_validate(organization)

    async def get_organizations(self) -> list[OrganizationOut]:
        organizations = await self.organization_repo.get_organizations()
        # Optional: filter by user's org if multi-tenant enforcement
        # if current_user:
        #     organizations = [o for o in organizations if o.id == current_user.organization_id]
        return [OrganizationOut.model_validate(org) for org in organizations]

    async def create_organization(self, data: OrganizationCreate) -> OrganizationOut:
        organization = await self.organization_repo.create(data.model_dump())
        return OrganizationOut.model_validate(organization)

    async def create_organization_and_main_branch(self, data: OrganizationCreate) -> tuple[OrganizationOut, BranchOut]:
        organization = await self.organization_repo.create(data.model_dump())
        branch_data = BranchCreate(**data.model_dump()).model_dump()
        branch_data.update({
            "is_main_branch": True,
            "organization_id": organization.id,
            "tax_integration_status": BranchTaxIntegrationStatus.NOT_STARTED,
        })
        branch = await self.organization_repo.create_main_branch(branch_data)
        return OrganizationOut.model_validate(organization), BranchOut.model_validate(branch)

    async def update_organization(self, ctx: RequestContext, data: OrganizationUpdate) -> OrganizationOut:
        current_tax_authority = ctx.organization.tax_authority
        new_tax_authority = data.tax_authority
        if current_tax_authority is not None and new_tax_authority is None:
            raise TaxAuthorityUpdateNotAllowedException()
        if current_tax_authority == TaxAuthority.ZATCA_PHASE2 and new_tax_authority == TaxAuthority.ZATCA_PHASE1:
            raise TaxAuthorityUpdateNotAllowedException()
        
        organization = await self.organization_repo.update(ctx.organization.id, data.model_dump())
        if current_tax_authority == TaxAuthority.ZATCA_PHASE1 and new_tax_authority == TaxAuthority.ZATCA_PHASE2:
            await self.organization_repo.change_branches_tax_integration_status(ctx.organization.id, BranchTaxIntegrationStatus.NOT_STARTED)
        return OrganizationOut.model_validate(organization)

    async def delete_organization(self, ctx: RequestContext) -> None:
        _ = await self.get_organization(ctx.organization.id)
        await self.organization_repo.delete(ctx.organization.id)
