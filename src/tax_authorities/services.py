from abc import ABC, abstractmethod
from typing import Optional, Any
from src.core.enums import BranchTaxIntegrationStatus
from src.sale_invoices.schemas import SaleInvoiceOut
from .schemas import InvoiceTaxAuthorityDataOut, InvoiceLineTaxAuthorityDataOut, BranchTaxAuthorityDataOut
from src.core.schemas.context import RequestContext

class TaxAuthorityService(ABC):
    @abstractmethod
    async def sign_and_submit_invoice(self, request_context: RequestContext, invoice: SaleInvoiceOut, metadata: dict = {}) -> Optional[InvoiceTaxAuthorityDataOut]:
        """Signs the invoice and submits it to the tax authority."""
        pass

    @abstractmethod
    async def get_invoice_tax_authority_data(self, request_context: RequestContext, invoice_id: int) -> Optional[InvoiceTaxAuthorityDataOut]:
        """Retrieves compliance data for a specific invoice."""
        pass

    @abstractmethod
    async def create_line_tax_authority_data(self, request_context: RequestContext, invoice_id: int, invoice_line_id: int, data: Any) -> Optional[InvoiceLineTaxAuthorityDataOut]:
        """Creates compliance data for an invoice line."""
        pass

    @abstractmethod
    async def get_line_tax_authority_data(self, request_context: RequestContext, invoice_line_id: int) -> Optional[InvoiceLineTaxAuthorityDataOut]:
        """Retrieves compliance data for a specific invoice line."""
        pass

    @abstractmethod
    async def create_branch_tax_authority_data(self, request_context: RequestContext, branch_id: int, data: Any) -> Optional[BranchTaxAuthorityDataOut]:
        """Creates branch compliance data for tax authority."""
        pass

    @abstractmethod
    async def complete_branch_tax_authority_data(self, request_context: RequestContext, branch_id: int, data: Any) -> Optional[BranchTaxAuthorityDataOut]:
        """Completes branch compliance data for tax authority."""
        pass

    @abstractmethod
    async def get_branch_tax_authority_data(self, request_context: RequestContext, branch_id: int, tax_integration_status: BranchTaxIntegrationStatus) -> Optional[BranchTaxAuthorityDataOut]:
        """Retrieves branch compliance data for tax authority."""
        pass

    @abstractmethod
    async def create_invoice_tax_authority_data(self, request_context: RequestContext, invoice_id: int, data: Any) -> Optional[InvoiceTaxAuthorityDataOut]:
        """Creates invoice compliance data for tax authority."""
        pass

    @abstractmethod
    async def delete_invoice_tax_authority_data(self, request_context: RequestContext, invoice_id: int) -> None:
        """Deletes invoice compliance data for tax authority."""
        pass

    @abstractmethod
    async def delete_lines_tax_authority_data(self, request_context: RequestContext, invoice_id: int) -> None:
        """Deletes line compliance data for tax authority."""
        pass

