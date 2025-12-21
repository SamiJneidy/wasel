from typing import Optional, Any
from src.users.schemas import UserInDB
from src.sale_invoices.schemas import SaleInvoiceOut
from ..services import TaxAuthorityService

class NoTaxAuthorityService(TaxAuthorityService):
    """
    A no-op TaxAuthorityService for organizations or countries
    that do not have a specific tax authority.
    All methods are implemented safely and return None or skipped metadata.
    """

    async def sign_and_submit_invoice(self, user: UserInDB, invoice: SaleInvoiceOut) -> None:
        """
        No tax authority: invoice is not signed/submitted.
        Returns skipped metadata.
        """
        return None
    async def get_invoice_compliance_metadata(self, user: UserInDB, invoice_id: int) -> None:
        """
        Returns None as no compliance metadata exists.
        """
        return None

    async def get_line_compliance_metadata(self, user: UserInDB, invoice_line_id: int) -> None:
        return None

    async def create_line_compliance_metadata(self, user: UserInDB, invoice_id: int, invoice_line_id: int, data: Any) -> None:
        return None

    async def create_branch_compliance_metadata(self, user: UserInDB, branch_id: int, data: Any) -> None:
        return None

    async def get_branch_compliance_metadata(self, user: UserInDB, branch_id: int) -> None:
        return None

    async def create_invoice_compliance_metadata(self, user: UserInDB, invoice_id: int, data: Any) -> None:
        return None

    async def delete_invoice_compliance_metadata(self, user: UserInDB, invoice_id: int) -> None:
        return None

    async def delete_lines_compliance_metadata(self, user: UserInDB, invoice_id: int) -> None:
        return None
