from src.users.schemas import UserInDB

from .schemas import (
    ProjectOut,
    ProjectCreate,
    ProjectUpdate,
    ProjectFilters,
)
from src.core.schemas import PagintationParams
from .repositories import ProjectRepository
from .exceptions import ProjectNotFoundException


class ProjectService:
    def __init__(self, project_repo: ProjectRepository):
        self.project_repo = project_repo

    async def get(self, user: UserInDB, id: int) -> ProjectOut:
        project = await self.project_repo.get(user.organization_id, user.branch_id, id)
        if not project:
            raise ProjectNotFoundException()
        return ProjectOut.model_validate(project)

    async def get_projects(
        self,
        user: UserInDB,
        pagination_params: PagintationParams,
        filters: ProjectFilters,
    ) -> tuple[int, list[ProjectOut]]:
        total, query_set = await self.project_repo.get_projects(
            user.organization_id,
            user.branch_id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [ProjectOut.model_validate(project) for project in query_set]

    async def create(self, user: UserInDB, data: ProjectCreate) -> ProjectOut:
        project = await self.project_repo.create(
            user.organization_id,
            user.branch_id,
            user.id,
            data.model_dump(),
        )
        return ProjectOut.model_validate(project)

    async def update(
        self,
        user: UserInDB,
        id: int,
        data: ProjectUpdate,
    ) -> ProjectOut:
        project = await self.project_repo.update(
            user.organization_id,
            user.branch_id,
            user.id,
            id,
            data.model_dump(exclude_unset=True),
        )
        if not project:
            raise ProjectNotFoundException()
        return ProjectOut.model_validate(project)

    async def delete(self, user: UserInDB, id: int) -> None:
        await self.get(user, id)
        await self.project_repo.delete(user.organization_id, user.branch_id, id)
        return None
