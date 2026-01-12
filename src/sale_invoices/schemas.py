from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import date, time, datetime
from src.items.schemas import ItemOut
from src.tax_authorities.schemas import (
    InvoiceTaxAuthorityDataCreate, 
    InvoiceTaxAuthorityDataOut, 
    InvoiceLineTaxAuthorityDataCreate, 
    InvoiceLineTaxAuthorityDataOut,
)
from src.core.schemas import AuditTimeMixin, SingleObjectResponse, SuccessfulResponse, PagintationParams, PaginatedResponse
from src.users.schemas import UserOut
from src.customers.schemas import CustomerOut
from src.core.config import settings
from src.core.enums import (
    DocumentType, 
    TaxExemptionReasonCode, 
    PartyIdentificationScheme, 
    InvoiceType, 
    InvoiceTypeCode, 
    PaymentMeansCode, 
    TaxCategory,
    InvoiceStatus,
    InvoiceTaxAuthorityStatus,
)
from src.points_of_sale.schemas import PointOfSaleOut
from typing import Optional, Annotated, Self, Union
from decimal import Decimal
import uuid

class SaleInvoiceLineCreate(BaseModel):
    item_id: int    
    item_price: Decimal = Field(..., decimal_places=2)
    price_discount: Decimal = Field(..., decimal_places=6)
    quantity: Decimal = Field(..., decimal_places=6)
    discount_amount: Decimal = Field(..., decimal_places=2)
    classified_tax_category: TaxCategory = Field(...)
    # description: Optional[str] = Field(None, min_length=1, max_length=200)
    tax_authority_data: Optional[InvoiceLineTaxAuthorityDataCreate] = None
    
    
    @field_validator("item_price", "price_discount", "discount_amount",  mode="after")
    def non_negative(cls, value):
        if value < 0:
            raise ValueError("The value must be non-negative (greater than or equal to zero)")
        return value

    @field_validator("quantity",  mode="after")
    def positive(cls, value):
        if value <= 0:
            raise ValueError("The value must be positive (strictly greater than zero)")
        return value


class SaleInvoiceLineOut(BaseModel):
    id: int
    item: Optional[ItemOut] = None
    item_price: Decimal = Field(..., decimal_places=2)
    quantity: Decimal = Field(..., decimal_places=6)
    price_discount: Decimal = Field(..., decimal_places=6)
    discount_amount: Decimal = Field(..., decimal_places=2)
    line_extension_amount: Decimal = Field(..., decimal_places=2)
    tax_amount: Decimal = Field(..., decimal_places=2)
    tax_rate: Decimal = Field(..., decimal_places=2)
    classified_tax_category: TaxCategory = Field(...)
    rounding_amount: Decimal = Field(..., decimal_places=2)
    # description: Optional[str] = Field(None, min_length=1, max_length=200)
    tax_authority_data: Optional[InvoiceLineTaxAuthorityDataOut] = None
    model_config = ConfigDict(from_attributes=True)


class SaleInvoiceHeaderBase(BaseModel):
    document_type: DocumentType = Field(...)
    invoice_type: InvoiceType = Field(...)
    invoice_type_code: InvoiceTypeCode = Field(...)
    issue_date: date = Field(..., description="Date in format YYYY-MM-DD", example="2025-01-24")
    issue_time: time = Field(..., description="Time in the format HH:MM:SS", example="14:30:00")
    document_currency_code: str = Field("SAR", description="The value must be SAR", example="SAR")
    actual_delivery_date: Optional[date] = Field(None, description="Actual date of delivery if applicable")
    payment_means_code: PaymentMeansCode = Field(..., description="Code representing the payment method")
    original_invoice_id: Optional[str] = Field(None, description="ID of the original invoice if this is a correction", example=456)
    instruction_note: Optional[str] = Field(None, max_length=4000, description="Additional instructions related to the invoice")
    prices_include_tax: bool = Field(...)
    discount_amount: Decimal = Field(..., description="Total discount amount", example=50.00)
    status: InvoiceStatus = Field(..., description="Status of the invoice. Could not be changed always.")
    note: Optional[str] = Field(None, max_length=4000, description="General notes about the invoice")

class SaleInvoiceHeaderOut(SaleInvoiceHeaderBase):
    id: int
    invoice_number: str = Field(...)
    line_extension_amount: Decimal = Field(..., description="Total amount before taxes and discounts", example=1000.00)
    taxable_amount: Decimal = Field(..., description="Amount subject to taxation", example=950.00)
    tax_amount: Decimal = Field(..., description="Total tax amount", example=142.50)
    tax_inclusive_amount: Decimal = Field(..., description="Total amount including taxes", example=1092.50)
    payable_amount: Decimal = Field(..., description="Final amount to be paid", example=1092.50)
    uuid: Optional[uuid.UUID]
    tax_authority_data: Optional[InvoiceTaxAuthorityDataOut] = None
    tax_authority_status: InvoiceTaxAuthorityStatus
    model_config = ConfigDict(from_attributes=True)

class SaleInvoiceCreate(SaleInvoiceHeaderBase):
    point_of_sale_id: Optional[int] = None
    tax_authority_data: Optional[InvoiceTaxAuthorityDataCreate] = None
    send_to_tax_authority: bool = Field(False, description="Indicates whether to send the invoice to the tax authority upon creation")
    customer_id: Optional[int] = None
    invoice_lines: list[SaleInvoiceLineCreate]
    
    @field_validator("invoice_lines", mode="after")
    def validate_invoice_lines(cls, value):
        if len(value) == 0:
            raise ValueError("The invoice must have at least 1 invoice line")
        return value
    
    @field_validator("issue_date", "actual_delivery_date", mode="after")
    def validate_date_format(cls, value):
        if value is None:
            return None
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except Exception as e:
            raise ValueError("The input should be a valid date in the format YYYY-MM-DD")
    
    @field_validator("issue_time", mode="after")
    def valiedate_time_formate(cls, value):
        try:
            return datetime.strptime(str(value), "%H:%M:%S").time()
        except Exception:
            raise ValueError("The input should be a valid time in the format HH:MM:SS")

    @field_validator("discount_amount", mode="after")
    def validate_amount(cls, value):
        if value < 0:
            raise ValueError("The value must be positive")
        return value    

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        is_invoice = self.document_type == DocumentType.INVOICE
        is_quotation = self.document_type == DocumentType.QUOTATION
        is_note = self.invoice_type_code in {InvoiceTypeCode.CREDIT_NOTE, InvoiceTypeCode.DEBIT_NOTE}

        # 1. Status validation
        if self.status not in {InvoiceStatus.ISSUED, InvoiceStatus.DRAFT}:
            raise ValueError("Invoice can only be created with status ISSUED or DRAFT")

        # 2. Quotation rules
        if is_quotation:
            if is_note:
                raise ValueError("Credit and debit notes cannot be created as quotations")
            if self.status != InvoiceStatus.DRAFT:
                raise ValueError("Quotations must always be created in DRAFT status")
            if self.send_to_tax_authority:
                raise ValueError("Quotations cannot be sent to the tax authority")
            return self

        # 3. Invoice rules
        if is_invoice:
            if self.invoice_type == InvoiceType.STANDARD and self.customer_id is None:
                raise ValueError("Customer is required for standard invoices")
            if is_note:
                if self.original_invoice_id is None:
                    raise ValueError("Original invoice is required for credit and debit notes")
                if self.status == InvoiceStatus.DRAFT:
                    raise ValueError("Credit and debit notes must be issued immediately")
        return self


class SaleInvoiceUpdate(SaleInvoiceCreate):
    pass    

class SaleInvoiceOut(SaleInvoiceHeaderOut):
    id: int = Field(...)
    customer: Optional[CustomerOut] = None
    point_of_sale: Optional[PointOfSaleOut] = None
    invoice_lines: list[SaleInvoiceLineOut]
    model_config = ConfigDict(from_attributes=True)


class SaleInvoiceFilters(BaseModel):
    document_type: Optional[DocumentType] = None
    customer_id: Optional[int] = Field(None)
    invoice_type: Optional[InvoiceType] = Field(None, description="Standard or Simplified")
    invoice_type_code: Optional[InvoiceTypeCode] = Field(None, description="Invoice, Credit Note or Debit Note")
    issue_date_range_from: Optional[date] = Field(None, description="Date in format YYYY-MM-DD", example="2025-01-24")
    issue_date_range_to: Optional[date] = Field(None, description="Date in format YYYY-MM-DD", example="2025-01-24")
    payment_means_code: Optional[PaymentMeansCode] = Field(None, description="Code representing the payment method")
    stauts: Optional[InvoiceStatus] = Field(None)
    tax_authority_status: Optional[InvoiceTaxAuthorityStatus] = Field(None)

    @field_validator("issue_date_range_from", "issue_date_range_to", mode="after")
    def validate_date_format(cls, value):
        if value is None:
            return None
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except Exception as e:
            raise ValueError("The input should be a valid date in the format YYYY-MM-DD") 


class GetInvoiceNumberRequest(BaseModel):
    document_type: DocumentType
    invoice_type: InvoiceType
    invoice_type_code: InvoiceTypeCode


class GetInvoiceNumberResponse(BaseModel):
    invoice_number: str
