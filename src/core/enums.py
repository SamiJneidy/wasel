from enum import Enum

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class TokenScope(str, Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"
    INVITE = "INVITE"
    RESET_PASSWORD = "RESET_PASSWORD"

class CSIDType(str, Enum):
    PRODUCTION = "PRODUCTION"
    COMPLIANCE = "COMPLIANCE"

class InvoicingType(str, Enum):
    STANDARD = "1000"
    SIMPLIFIED = "0100"
    BOTH = "1100"

class InvoiceType(str, Enum):
    STANDARD = "0100000"
    SIMPLIFIED = "0200000"

class InvoiceTypeCode(str, Enum):
    CREDIT_NOTE = "381"
    DEBIT_NOTE = "383"
    INVOICE = "388"

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"  # Full system access (rarely used)
    ADMIN = "ADMIN"              # Manages users, settings, etc.
    SALESMAN = "SALESMAN"
    ACCOUNTANT = "ACCOUNTANT"

class UserType(str, Enum):
    CLIENT = "CLIENT"
    DEVELOPR = "DEVELOPER"

class UserStatus(str, Enum):
    PENDING = "PENDING"          # Awaiting email/phone verification
    ACTIVE = "ACTIVE"            # Verified and fully accessible
    BLOCKED = "BLOCKED"          # Temporary suspension (e.g., too many failed logins)
    DISABLED = "DISABLED"        # Manual deactivation by admin (reversible)
    DELETED = "DELETED"          # Soft-deleted (GDPR compliance; irreversible)

class OTPStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"

class OTPUsage(str, Enum):
    LOGIN = "LOGIN"
    PASSWORD_RESET = "PASSWORD_RESET"
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"

class PartyIdentificationScheme(str, Enum):
    CRN = "CRN"
    NAT = "NAT"
    MOMRAH = "MOMRAH"
    MHRSD = "MHRSD"
    THE700 = "700"
    MISA = "MISA"

class UnitCodes(str, Enum):
    PCE = "PCE"

class PaymentMeansCode(str, Enum):
    CASH = "10"
    CHEQUE = "20"
    CREDIT_TRANSFER = "30"
    DEBIT_TRANSFER = "31"
    PAYMENT_TO_BANK_ACCOUNT = "42"
    BANK_CARD = "48"

class TaxExemptionReasonCode(str, Enum):
    VATEX_SA_29 = "VATEX-SA-29"
    VATEX_SA_29_7 = "VATEX-SA-29-7"
    VATEX_SA_30 = "VATEX-SA-30"
    VATEX_SA_32 = "VATEX-SA-32"
    VATEX_SA_33 = "VATEX-SA-33"
    VATEX_SA_34_1 = "VATEX-SA-34-1"
    VATEX_SA_34_2 = "VATEX-SA-34-2"
    VATEX_SA_34_3 = "VATEX-SA-34-3"
    VATEX_SA_34_4 = "VATEX-SA-34-4"
    VATEX_SA_34_5 = "VATEX-SA-34-5"
    VATEX_SA_35 = "VATEX-SA-35"
    VATEX_SA_36 = "VATEX-SA-36"
    VATEX_SA_EDU = "VATEX-SA-EDU"
    VATEX_SA_HEA = "VATEX-SA-HEA"
    VATEX_SA_MLTRY = "VATEX-SA-MLTRY"
    VATEX_SA_OOS = "VATEX-SA-OOS"

class TaxCategory(str, Enum):
    S = "S"
    Z = "Z"
    E = "E"
    O = "O"

class DocumentType(str, Enum):
    INVOICE = "INVOICE"
    QUOTATION = "QUOTATION"

class Stage(str, Enum):
    PRODUCTION = "PRODUCTION"
    COMPLIANCE = "COMPLIANCE"

class TaxScheme(str, Enum):
    NONE = "NONE"
    ZATCA_PHASE1 = "ZATCA_PHASE1"
    ZATCA_PHASE2 = "ZATCA_PHASE2"