from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class Country(str, Enum):
    SYRIA = "Syria"
    USA = "USA"

class MartialStatus(str, Enum):
    Single = "single"
    Married = "married"

class EmployeeStatus(str, Enum):
    WORKING = "working"
    RETIRED = "retired"

class UserRole(str, Enum):
    JOB_SEEKER = "job_seeker"                # Regular user (default)
    RECRUITER = "recruiter"      # Manages content (e.g., delete posts)
    ADMIN = "admin"              # Manages users, settings, etc.
    SUPER_ADMIN = "super_admin"  # Full system access (rarely used)

class UserStatus(str, Enum):
    PENDING = "pending"          # Awaiting email/phone verification
    ACTIVE = "active"            # Verified and fully accessible
    BLOCKED = "blocked"          # Temporary suspension (e.g., too many failed logins)
    DISABLED = "disabled"        # Manual deactivation by admin (reversible)
    DELETED = "deleted"          # Soft-deleted (GDPR compliance; irreversible)

class OTPStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    EXPIRED = "expired"

class OTPUsage(str, Enum):
    LOGIN = "login"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"

class PartyIdentificationScheme(str, Enum):
    CRN = "CRN"
    MOMRAH = "MOMRAH"
    MHRSD = "MHRSD"
    THE700 = "700"
    MISA = "MISA"