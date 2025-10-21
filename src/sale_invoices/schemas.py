from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, constr, Field, field_validator, model_validator
from datetime import date, time, datetime
from src.items.schemas import ItemOut
from src.zatca.schemas import ZatcaCSIDResponse
from src.core.schemas import AuditTimeMixin, SingleObjectResponse, SuccessfulResponse, PagintationParams, PaginatedResponse
from src.users.schemas import UserOut
from src.customers.schemas import CustomerOut
from src.core.config import settings
from src.core.enums import TaxExemptionReasonCode, PartyIdentificationScheme, InvoiceType, InvoiceTypeCode, PaymentMeansCode, TaxCategory
from typing import Optional, Annotated, Self, Union
from decimal import Decimal
import uuid

# class PartyIdentificationBase(BaseModel):
#     registration_name: Optional[str] = Field(..., min_length=1, max_length=250, example="Wasel LLC")
#     street: Optional[str] = Field(..., min_length=1, max_length=300, example="Tahlia Stree", description="This field is free text")
#     building_number: Optional[str] = Field(..., min_length=4, max_length=4, pattern=r"^\d{4}$", example="1234")
#     division: Optional[str] = Field(..., min_length=1, max_length=200, example="Albawadi")
#     city: Optional[str] = Field(..., min_length=1, max_length=50, example="Jeddah")
#     postal_code: Optional[str] = Field(..., min_length=5, max_length=5, pattern=r"^\d{5}$")
#     vat_number: Optional[str] = Field(..., min_length=15, max_length=15, pattern=r"^3\d{13}3$")
#     party_identification_scheme: Optional[PartyIdentificationScheme]
#     party_identification_value: Optional[str] = Field(..., min_length=1, max_length=25, example="5243526715")

# class TaxExcemptionCustomer(BaseModel):
#     registration_name: Optional[str] = Field(..., min_length=1, max_length=250, example="Ahmed Ali")
#     party_identification_scheme: Optional[PartyIdentificationScheme]
#     party_identification_value: Optional[str] = Field(..., min_length=1, max_length=25, example="5243526715")    

# class TaxExcemptionCustomerOut(TaxExcemptionCustomer):
#     id: int
#     invoice_id: int
#     model_config = ConfigDict(from_attributes=True)    

# class Supplier(PartyIdentificationBase):
#     pass 


class SaleInvoiceLineCreate(BaseModel):
    item_id: int    
    item_price: Decimal = Field(..., decimal_places=2)
    price_discount: Decimal = Field(..., decimal_places=6)
    quantity: Decimal = Field(..., decimal_places=6)
    discount_amount: Decimal = Field(..., decimal_places=2)
    classified_tax_category: TaxCategory = Field(...)
    tax_exemption_reason_code: Optional[TaxExemptionReasonCode] = Field(None)
    tax_exemption_reason: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    
    
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

    @model_validator(mode="after")
    def validate_line(self) -> Self:
        # if(self.classified_tax_category == TaxCategory.S and self.tax_rate != settings.STANDARD_TAX_RATE):
        #     raise ValueError(f"Tax rate must be equal to {settings.STANDARD_TAX_RATE} when the tax category is 'S'")
        # if(self.classified_tax_category != TaxCategory.S and self.tax_rate != 0):
        #     raise ValueError("Tax rate must be equal to 0.00 when the tax category is 'Z', 'E' or 'O'")
        if(self.classified_tax_category == TaxCategory.S and (self.tax_exemption_reason_code != None or self.tax_exemption_reason != None)):
            raise ValueError("'Tax Exemption Reason' and 'Tax Exemption Reason Code' must be sent as 'null' when the tax category is 'S'")
        if(self.classified_tax_category != TaxCategory.S and (self.tax_exemption_reason_code is None or self.tax_exemption_reason is None)):
            raise ValueError("'Tax Exemption Reason' and 'Tax Exemption Reason Code' are mandatory when the tax category is 'Z', 'E' or 'O'")
        return self 

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
    tax_exemption_reason_code: Optional[TaxExemptionReasonCode] = Field(None)
    tax_exemption_reason: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    model_config = ConfigDict(from_attributes=True)


class SaleInvoiceHeaderBase(BaseModel):
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
    line_extension_amount: Decimal = Field(..., description="Total amount before taxes and discounts", example=1000.00)
    taxable_amount: Decimal = Field(..., description="Amount subject to taxation", example=950.00)
    tax_amount: Decimal = Field(..., description="Total tax amount", example=142.50)
    tax_inclusive_amount: Decimal = Field(..., description="Total amount including taxes", example=1092.50)
    payable_amount: Decimal = Field(..., description="Final amount to be paid", example=1092.50)
    pih: Optional[str] = None 
    icv: int
    base64_qr_code: Optional[str] = None
    invoice_hash: Optional[str] = None
    uuid: uuid.UUID
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
        return self
    

class SaleInvoiceOut(SaleInvoiceHeaderOut):
    id: int = Field(...)
    customer: Optional[CustomerOut] = None
    invoice_lines: list[SaleInvoiceLineOut]
    invoice_hash: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class SaleInvoiceFilters(BaseModel):
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
