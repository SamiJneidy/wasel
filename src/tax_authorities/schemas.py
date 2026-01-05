from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Annotated, Optional, Union
from src.core.enums import TaxExemptionReasonCode, ZatcaPhase2Stage, TaxAuthority
from .zatca_phase2.schemas import (
    ZatcaPhase2InvoiceLineDataCreate,
    ZatcaPhase2InvoiceLineDataOut,
    ZatcaPhase2InvoiceDataOut,
    ZatcaPhase2InvoiceDataCreate,
    ZatcaPhase2BranchDataCreate,
    ZatcaPhase2BranchDataComplete,
    ZatcaPhase2BranchDataOut,
)

InvoiceTaxAuthorityDataCreate = Annotated[
    Union[ZatcaPhase2InvoiceDataCreate],
    Field(discriminator="tax_authority")
]
InvoiceTaxAuthorityDataOut = Annotated[
    Union[ZatcaPhase2InvoiceDataOut],
    Field(discriminator="tax_authority")
]

InvoiceLineTaxAuthorityDataCreate = Annotated[
    Union[ZatcaPhase2InvoiceLineDataCreate],
    Field(discriminator="tax_authority")
]
InvoiceLineTaxAuthorityDataOut = Annotated[
    Union[ZatcaPhase2InvoiceLineDataOut],
    Field(discriminator="tax_authority")
]

BranchTaxAuthorityDataOut = Annotated[
    Union[ZatcaPhase2BranchDataOut],
    Field(discriminator="tax_authority")
]

BranchTaxAuthorityDataCreate = Annotated[
    Union[ZatcaPhase2BranchDataCreate],
    Field(discriminator="tax_authority")
]

BranchTaxAuthorityDataComplete = Annotated[
    Union[ZatcaPhase2BranchDataComplete],
    Field(discriminator="tax_authority")
]
# class BranchTaxAuthorityDataCreate(TaxAuthorityDiscriminator):
#     pass

# class BranchTaxAuthorityDataOut(TaxAuthorityDiscriminator):
#     pass
