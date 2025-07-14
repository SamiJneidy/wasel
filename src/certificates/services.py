# csr_generator.py
from cryptography import x509
from cryptography.x509.oid import NameOID, ObjectIdentifier
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from src.core.config import settings
from src.users.schemas import UserInDB
import base64
import os
import re
import uuid

class CertificateService:
    def __init__(self):
        pass

    def generate_private_key(self):
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    def generate_serial_number(self) -> str:
        serial_uuid = str(uuid.uuid4())
        serial_number = "|".join(["1-Wasel", "2-v1", f"3-{serial_uuid}"])
        return serial_number

    def generate_csr(self, user: UserInDB):
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


c = CertificateService()
print(c.generate_private_key())
