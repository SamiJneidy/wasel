import base64
import os
import re
import uuid
import json
import time
import requests
from cryptography import x509
from cryptography.x509.oid import NameOID, ObjectIdentifier
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import status
from requests.auth import HTTPBasicAuth
from src.core.config import settings
from src.users.schemas import UserInDB, UserOut
from src.users.services import UserService
from src.zatca.services import ZatcaService
from src.core.enums import CSIDType
from .schemas import ComplianceCSIDRequest, ComplianceCSIDResponse, CSIDCreate
from .repositories import CSIDRepository
from .exceptions import UserNotCompleteException


class CSIDService:
    def __init__(self, csid_repo: CSIDRepository, user_service: UserService, zatca_service: ZatcaService):
        self.user_service = user_service
        self.zatca_service = zatca_service
        self.csid_repo = csid_repo

    def generate_private_key(self):
        """Returns a private key object, not a serialized string."""
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    def generate_serial_number(self) -> str:
        """Generates a serial number for CSR generation."""
        serial_uuid = str(uuid.uuid4())
        serial_number = "|".join(["1-Wasel", "2-v1", f"3-{serial_uuid}"])
        return serial_number

    def generate_private_key_and_csr(self, user: UserInDB) -> tuple[str, str]:
        """Generates a private key and CSR in base64 and returns them as a tuple of strings (private_key, csr_base64)."""
        private_key = self.generate_private_key()
        
        # Build the CSR
        csr_builder = x509.CertificateSigningRequestBuilder()
        csr_builder = csr_builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, user.country_code),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, user.organization_unit_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, user.organization_name),
            x509.NameAttribute(NameOID.COMMON_NAME, user.common_name)
        ]))
        
        # Add ASN.1 extension
        csr_builder = csr_builder.add_extension(
            x509.UnrecognizedExtension(
                ObjectIdentifier("1.3.6.1.4.1.311.20.2"), 
                settings.ZATCA_ASN_TEMPLATE.encode()
            ),
            critical=False
        )
        
        # Add SAN extension
        csr_builder = csr_builder.add_extension(
            x509.SubjectAlternativeName([
                x509.DirectoryName(x509.Name([
                    x509.NameAttribute(ObjectIdentifier("2.5.4.4"), self.generate_serial_number()),
                    x509.NameAttribute(ObjectIdentifier("0.9.2342.19200300.100.1.1"), user.vat_number),
                    x509.NameAttribute(ObjectIdentifier("2.5.4.12"), user.invoicing_type),
                    x509.NameAttribute(ObjectIdentifier("2.5.4.26"), user.address),
                    x509.NameAttribute(ObjectIdentifier("2.5.4.15"), user.business_category)
                ]))
            ]),
            critical=False
        )

        # Sign the CSR with the private key
        csr = csr_builder.sign(private_key, hashes.SHA256(), default_backend())

        # Serialize private key and CSR
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        csr_pem = csr.public_bytes(serialization.Encoding.PEM)

        # Strip header/footer from private key
        private_key_content = re.sub(
            r'-----BEGIN .* PRIVATE KEY-----|-----END .* PRIVATE KEY-----|\n', '', 
            private_key_pem.decode('utf-8')
        )

        # Encode CSR in Base64
        csr_base64 = base64.b64encode(csr_pem).decode('utf-8')

        return private_key_content, csr_base64

    async def generate_compliance_csid(self, email: str, data: ComplianceCSIDRequest) -> ComplianceCSIDResponse:
        
        user: UserInDB = await self.user_service.get_user_in_db(email)
        if not user.is_completed:
            raise UserNotCompleteException()
        
        private_key, csr_base64 = self.generate_private_key_and_csr(user)
        zatca_csid = await self.zatca_service.get_compliance_csid(csr_base64, data.code)
        
        certificate = base64.b64decode(zatca_csid.binary_security_token).decode('utf-8')
        authorization = zatca_csid.binary_security_token + ':' + zatca_csid.secret
        authorization_base64 = base64.b64encode(authorization.encode('utf-8')).decode('utf-8')

        csid_data = CSIDCreate(
            user_id=user.id, 
            type=CSIDType.COMPLIANCE,
            private_key=private_key, 
            csr_base64=csr_base64, 
            certificate=certificate,
            authorization=authorization_base64,
            request_id=zatca_csid.request_id,
            disposition_message=zatca_csid.disposition_message,
            binary_security_token=zatca_csid.binary_security_token,
            secret=zatca_csid.secret
        )

        await self.csid_repo.create(csid_data.model_dump())
        return ComplianceCSIDResponse(email=user.email)

