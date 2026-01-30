from .schemas import ProjectOut, ProjectCreate, ProjectUpdate, ProjectFilters
from src.core.schemas import PagintationParams
from .repositories import ProjectRepository
from .exceptions import ProjectNotFoundException
from src.core.schemas.context import RequestContext


class ProjectService:
    def __init__(self, project_repo: ProjectRepository):
        self.project_repo = project_repo

    async def get_project(self, ctx: RequestContext, id: int) -> ProjectOut:
        project = await self.project_repo.get_project(ctx.organization.id, ctx.branch.id, id)
        if not project:
            raise ProjectNotFoundException()
        return ProjectOut.model_validate(project)

    async def get_projects(self, ctx: RequestContext, pagination_params: PagintationParams, filters: ProjectFilters) -> tuple[int, list[ProjectOut]]:
        total, query_set = await self.project_repo.get_projects(
            ctx.organization.id,
            ctx.branch.id,
            pagination_params.skip,
            pagination_params.limit,
            filters.model_dump(exclude_none=True),
        )
        return total, [ProjectOut.model_validate(project) for project in query_set]

    async def create_project(self, ctx: RequestContext, data: ProjectCreate) -> ProjectOut:
        project = await self.project_repo.create_project(ctx.organization.id, ctx.branch.id, ctx.user.id, data.model_dump())
        return ProjectOut.model_validate(project)

    async def update_project(self, ctx: RequestContext, id: int, data: ProjectUpdate) -> ProjectOut:
        project = await self.project_repo.update_project(
            ctx.organization.id,
            ctx.branch.id,
            ctx.user.id,
            id,
            data.model_dump(exclude_unset=True),
        )
        if not project:
            raise ProjectNotFoundException()
        return ProjectOut.model_validate(project)

    async def delete_project(self, ctx: RequestContext, id: int) -> None:
        await self.get_project(ctx, id)
        await self.project_repo.delete_project(ctx.organization.id, ctx.branch.id, id)
        return None
