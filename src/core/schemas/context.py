from pydantic import BaseModel
from src.users.schemas import UserOut
from src.branches.schemas import BranchOut
from src.organizations.schemas import OrganizationOut
from typing import Optional

class RequestContext(BaseModel):
    """Holds the context for a request, including the current user, organization, and branch."""
    user: UserOut
    organization: Optional[OrganizationOut] = None
    branch: Optional[BranchOut] = None