from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import date, time, datetime
from src.items.schemas import ItemOut
from src.zatca.schemas import ZatcaCSIDResponse
from src.core.schemas import AuditTimeMixin, SingleObjectResponse, SuccessfulResponse, PagintationParams, PaginatedResponse
from src.users.schemas import UserOut
from src.customers.schemas import CustomerOut
from src.core.config import settings
from src.zatca.schemas import ZatcaInvoiceLineMetadata, ZatcaInvoiceMetadata
from src.core.enums import DocumentType, TaxExemptionReasonCode, PartyIdentificationScheme, InvoiceType, InvoiceTypeCode, PaymentMeansCode, TaxCategory
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
    tax_authority_metadata: Optional[ZatcaInvoiceLineMetadata] = None
    
    
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
    tax_authority_metadata: Optional[ZatcaInvoiceLineMetadata] = None
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
    original_invoice_id: Optional[int] = Field(None, description="ID of the original invoice if this is a correction", example=456)
    instruction_note: Optional[str] = Field(None, max_length=4000, description="Additional instructions related to the invoice")
    prices_include_tax: bool = Field(...)
    discount_amount: Decimal = Field(..., description="Total discount amount", example=50.00)
    note: Optional[str] = Field(None, max_length=4000, description="General notes about the invoice")

class SaleInvoiceHeaderOut(SaleInvoiceHeaderBase):
    id: int
    invoice_number: str = Field(...)
    is_locked: bool = Field(...)
    line_extension_amount: Decimal = Field(..., description="Total amount before taxes and discounts", example=1000.00)
    taxable_amount: Decimal = Field(..., description="Amount subject to taxation", example=950.00)
    tax_amount: Decimal = Field(..., description="Total tax amount", example=142.50)
    tax_inclusive_amount: Decimal = Field(..., description="Total amount including taxes", example=1092.50)
    payable_amount: Decimal = Field(..., description="Final amount to be paid", example=1092.50)
    uuid: Optional[uuid.UUID]
    tax_authority_metadata: Optional[ZatcaInvoiceMetadata] = None
    completed_tax_authority: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)

class SaleInvoiceCreate(SaleInvoiceHeaderBase):
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
        if self.invoice_type == InvoiceType.STANDARD and self.customer_id is None:
            raise ValueError("The customer is mandatory for standard invoices")
        if self.document_type == DocumentType.QUOTATION and self.invoice_type_code != InvoiceTypeCode.INVOICE:
            raise ValueError("Credit notes and debit notes can only be issued for invoices not for quotations") 
        return self
    

class SaleInvoiceOut(SaleInvoiceHeaderOut):
    id: int = Field(...)
    customer: Optional[CustomerOut] = None
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
    classified_tax_category: Optional[TaxCategory] = Field(None, description="Tax category classification")

    @field_validator("issue_date_range_from", "issue_date_range_to", mode="after")
    def validate_date_format(cls, value):
        if value is None:
            return None
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except Exception as e:
            raise ValueError("The input should be a valid date in the format YYYY-MM-DD") 


class SaleInvoiceUpdate(SaleInvoiceCreate):
    is_locked: bool

class GetInvoiceNumberRequest(BaseModel):
    document_type: DocumentType
    invoice_type: InvoiceType
    invoice_type_code: InvoiceTypeCode


class GetInvoiceNumberResponse(BaseModel):
    invoice_number: str
