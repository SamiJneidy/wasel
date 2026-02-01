from typing import Optional, Any
from src.core.enums import BranchTaxIntegrationStatus
from src.core.schemas.context import RequestContext
from src.sale_invoices.schemas import SaleInvoiceOut
from ..services import TaxAuthorityService

class ZatcaPhase1Service(TaxAuthorityService):
    """
    A no-op TaxAuthorityService for organizations or countries
    that do not have a specific tax authority.
    All methods are implemented safely and return None or skipped metadata.
    """

    async def sign_and_submit_invoice(self, ctx: RequestContext, invoice: SaleInvoiceOut, metadata: dict = {}) -> None:
        """
        No tax authority: invoice is not signed/submitted.
        Returns skipped metadata.
        """
        return None
    async def get_invoice_tax_authority_data(self, ctx: RequestContext, invoice_id: int) -> None:
        """
        Returns None as no compliance metadata exists.
        """
        return None

    async def get_line_tax_authority_data(self, ctx: RequestContext, invoice_line_id: int) -> None:
        return None

    async def create_line_tax_authority_data(self, ctx: RequestContext, invoice_id: int, invoice_line_id: int, data: Any) -> None:
        return None

    async def create_branch_tax_authority_data(self, ctx: RequestContext, branch_id: int, data: Any) -> None:
        return None
    
    async def update_branch_tax_authority_data(self, ctx: RequestContext, branch_id: int, data: Any) -> None:
        return None
    
    async def complete_branch_tax_authority_data(self, ctx: RequestContext, branch_id: int, data: Any) -> None:
        return None

    async def get_branch_tax_authority_data(self, ctx: RequestContext, branch_id: int, tax_integration_status: BranchTaxIntegrationStatus) -> None:
        return None

    async def create_invoice_tax_authority_data(self, ctx: RequestContext, invoice_id: int, data: Any) -> None:
        return None

    async def delete_invoice_tax_authority_data(self, ctx: RequestContext, invoice_id: int) -> None:
        return None

    async def delete_lines_tax_authority_data(self, ctx: RequestContext, invoice_id: int) -> None:
        return None
