from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import date, time, datetime
from src.zatca.schemas import ZatcaCSIDResponse
from src.core.schemas import AuditTimeMixin, SingleObjectResponse, SuccessfulResponse, PagintationParams, PaginatedResponse
from src.users.schemas import UserOut
from src.items.schemas import ItemOut
from src.suppliers.schemas import SupplierOut
from src.core.enums import TaxExemptionReasonCode, PartyIdentificationScheme, InvoiceType, InvoiceTypeCode, PaymentMeansCode, TaxCategory
from typing import Optional, Annotated, Self, Union
from decimal import Decimal
import uuid


class BuyInvoiceLineCreate(BaseModel):
    item_id: int    
    item_price: Decimal = Field(..., decimal_places=2)
    price_includes_tax: bool = Field(...)
    price_discount: Decimal = Field(..., decimal_places=6)
    quantity: Decimal = Field(..., decimal_places=6)
    discount_amount: Decimal = Field(..., decimal_places=2)
    classified_tax_category: TaxCategory = Field(...)
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    
    
    @field_validator("price_discount", "discount_amount",  mode="after")
    def non_negative(cls, value):
        if value < 0:
            raise ValueError("The value must be non-negative (greater than or equal to zero)")
        return value

    @field_validator("quantity",  mode="after")
    def positive(cls, value):
        if value <= 0:
            raise ValueError("The value must be positive (strictly greater than zero)")
        return value


class BuyInvoiceLineOut(BaseModel):
    id: int
    item: Optional[ItemOut] = None
    item_price: Decimal = Field(..., decimal_places=2)
    quantity: Decimal = Field(..., decimal_places=6)
    price_includes_tax: bool = Field(...)
    price_discount: Decimal = Field(..., decimal_places=6)
    discount_amount: Decimal = Field(..., decimal_places=2)
    line_extension_amount: Decimal = Field(..., decimal_places=2)
    tax_amount: Decimal = Field(..., decimal_places=2)
    tax_rate: Decimal = Field(..., decimal_places=2)
    classified_tax_category: TaxCategory = Field(...)
    rounding_amount: Decimal = Field(..., decimal_places=2)
    description: Optional[str] = Field(None, min_length=1, max_length=200)

    model_config = ConfigDict(from_attributes=True)




class BuyInvoiceHeaderBase(BaseModel):
    invoice_number: str = Field(..., example="INV-000024")
    invoice_type_code: InvoiceTypeCode = Field(...)
    issue_date: date = Field(..., description="Date in format YYYY-MM-DD", example="2025-01-24")
    document_currency_code: str = Field("SAR", description="The value must be SAR", example="SAR")
    actual_delivery_date: Optional[date] = Field(None, description="Actual date of delivery if applicable")
    payment_means_code: PaymentMeansCode = Field(..., description="Code representing the payment method")
    original_invoice_id: Optional[int] = Field(None, description="ID of the original invoice if this is a correction", example=456)
    instruction_note: Optional[str] = Field(None, max_length=4000, description="Additional instructions related to the invoice")
    note: Optional[str] = Field(None, max_length=4000, description="General notes about the invoice")
    discount_amount: Decimal = Field(..., description="Total discount amount", example=50.00)

class BuyInvoiceHeaderOut(BuyInvoiceHeaderBase):
    id: int
    line_extension_amount: Decimal = Field(..., description="Total amount before taxes and discounts", example=1000.00)
    taxable_amount: Decimal = Field(..., description="Amount subject to taxation", example=950.00)
    tax_amount: Decimal = Field(..., description="Total tax amount", example=142.50)
    tax_inclusive_amount: Decimal = Field(..., description="Total amount including taxes", example=1092.50)
    invoice_number: str
    seq_number: Optional[int] = None
    uuid: Optional[uuid.UUID]
    model_config = ConfigDict(from_attributes=True)

class BuyInvoiceCreate(BuyInvoiceHeaderBase):
    supplier_id: int
    invoice_lines: list[BuyInvoiceLineCreate]
    
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

    @field_validator("discount_amount", mode="after")
    def validate_amount(cls, value):
        if value < 0:
            raise ValueError("The value must be positive")
        return value    
    
    @model_validator(mode="after")
    def validate_model(self) -> Self:
        tax_categories = set(line.classified_tax_category for line in self.invoice_lines)
        if(len(tax_categories) > 1 and self.discount_amount > 0):
            raise ValueError("Invoice level discount is forbidden when the invoice containes different tax categories.")
        return self
    
class BuyInvoiceOut(BuyInvoiceHeaderOut):
    id: int
    supplier: SupplierOut
    invoice_lines: list[BuyInvoiceLineOut]
    model_config = ConfigDict(from_attributes=True)


class BuyInvoiceFilters(BaseModel):
    customer_id: Optional[int] = Field(None)
    invoice_type_code: Optional[InvoiceTypeCode] = Field(None, description="BuyInvoice, Credit Note or Debit Note")
    issue_date_range_from: Optional[date] = Field(None, description="Date in format YYYY-MM-DD", example="2025-01-24")
    issue_date_range_to: Optional[date] = Field(None, description="Date in format YYYY-MM-DD", example="2025-01-24")
    payment_means_code: Optional[PaymentMeansCode] = Field(None, description="Code representing the payment method")

    @field_validator("issue_date_range_from", "issue_date_range_to", mode="after")
    def validate_date_format(cls, value):
        if value is None:
            return None
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()
        except Exception as e:
            raise ValueError("The input should be a valid date in the format YYYY-MM-DD")

    
