from abc import ABC, abstractmethod
from typing import Optional, Any
from src.users.schemas import UserInDB
from src.sale_invoices.schemas import SaleInvoiceOut

class TaxAuthorityService(ABC):
    @abstractmethod
    async def sign_and_submit_invoice(self, user: UserInDB, invoice: SaleInvoiceOut) -> Any:
        """Signs the invoice and submits it to the tax authority."""
        pass

    @abstractmethod
    async def get_invoice_compliance_metadata(self, user: UserInDB, invoice_id: int) -> Optional[Any]:
        """Retrieves compliance metadata for a specific invoice."""
        pass

    @abstractmethod
    async def get_line_compliance_metadata(self, user: UserInDB, invoice_line_id: int) -> Optional[Any]:
        """Retrieves compliance metadata for a specific invoice line."""
        pass

    @abstractmethod
    async def create_line_compliance_metadata(self, user: UserInDB, invoice_id: int, invoice_line_id: int, data: Any) -> Any:
        """Creates compliance metadata for an invoice line."""
        pass

    @abstractmethod
    async def create_branch_compliance_metadata(self, user: UserInDB, branch_id: int, data: Any) -> Any:
        """Creates branch compliance metadata for tax authority."""
        pass

    @abstractmethod
    async def get_branch_compliance_metadata(self, user: UserInDB, branch_id: int) -> Any:
        """Retrieves branch compliance metadata for tax authority."""
        pass

    @abstractmethod
    async def create_invoice_compliance_metadata(self, user: UserInDB, invoice_id: int, data: Any) -> Any:
        """Creates invoice compliance metadata for tax authority."""
        pass

    @abstractmethod
    async def delete_invoice_compliance_metadata(self, user: UserInDB, invoice_id: int) -> None:
        """Deletes invoice compliance metadata for tax authority."""
        pass

    @abstractmethod
    async def delete_lines_compliance_metadata(self, user: UserInDB, invoice_id: int) -> None:
        """Deletes line compliance metadata for tax authority."""
        pass

