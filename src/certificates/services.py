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

class ZatcaService:
    
    @staticmethod
    def get_compliance_csid(cert_info, retries=3, backoff_factor=1):
        csr = cert_info['csr']
        OTP = cert_info['OTP']
        url = cert_info['complianceCsidUrl']

        json_payload = json.dumps({'csr': csr})
        
        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'OTP': OTP,
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }
        
        return api_helper.post_request_with_retries(url, headers, json_payload, retries=retries, backoff_factor=backoff_factor)

    @staticmethod
    def production_csid(cert_info, retries=3, backoff_factor=1):
        request_id = cert_info['ccsid_requestID']
        id_token = cert_info['ccsid_binarySecurityToken']
        secret = cert_info['ccsid_secret']
        url = cert_info['productionCsidUrl']

        json_payload = json.dumps({'compliance_request_id': request_id})

        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }

        auth = HTTPBasicAuth(id_token, secret)
        return api_helper.post_request_with_retries(url, headers, json_payload, auth=auth, retries=retries, backoff_factor=backoff_factor)

    @staticmethod
    def compliance_checks(cert_info, json_payload, retries=3, backoff_factor=1):
        id_token = cert_info['ccsid_binarySecurityToken']
        secret = cert_info['ccsid_secret']
        url = cert_info["complianceChecksUrl"]

        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }

        auth = HTTPBasicAuth(id_token, secret)
        return api_helper.post_request_with_retries(url, headers, json_payload, auth=auth, retries=retries, backoff_factor=backoff_factor)

    @staticmethod
    def invoice_reporting(cert_info, json_payload, retries=3, backoff_factor=1):
        id_token = cert_info['pcsid_binarySecurityToken']
        secret = cert_info['pcsid_secret']
        url = cert_info["reportingUrl"]

        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }

        auth = HTTPBasicAuth(id_token, secret)
        return api_helper.post_request_with_retries(url, headers, json_payload, auth=auth, retries=retries, backoff_factor=backoff_factor)

    @staticmethod
    def invoice_clearance(cert_info, json_payload, retries=3, backoff_factor=1):
        id_token = cert_info['pcsid_binarySecurityToken']
        secret = cert_info['pcsid_secret']
        url = cert_info["clearanceUrl"]

        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Clearance-Status': '1',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }

        auth = HTTPBasicAuth(id_token, secret)
        return api_helper.post_request_with_retries(url, headers, json_payload, auth=auth, retries=retries, backoff_factor=backoff_factor)

    @staticmethod
    def load_json_from_file(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing JSON: {str(e)}")

    @staticmethod
    def save_json_to_file(file_path, data):
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4, ensure_ascii=False, separators=(',', ': '))
        except Exception as e:
            raise Exception(f"Error saving JSON: {str(e)}")

    @staticmethod
    def clean_up_json(api_response, request_type, api_url):
        array_response = json.loads(api_response)
        array_response['requestType'] = request_type
        array_response['apiUrl'] = api_url

        array_response = {k: v for k, v in array_response.items() if v is not None}

        reordered_response = {
            'requestType': array_response.pop('requestType'),
            'apiUrl': array_response.pop('apiUrl'),
            **array_response
        }

        return json.dumps(reordered_response, indent=4, ensure_ascii=False, separators=(',', ': '))


class CertificateService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def generate_private_key(self):
        """Returns a private key object, not a serialized string."""
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    def generate_serial_number(self) -> str:
        """Generates a serial number for CSR generation."""
        serial_uuid = str(uuid.uuid4())
        serial_number = "|".join(["1-Wasel", "2-v1", f"3-{serial_uuid}"])
        return serial_number

    def generate_private_key_and_csr(self, user: UserInDB) -> tuple[str, str]:
        """Generates a private key and base64 CSR and returns them as a tuple of strings (private_key, csr_base64)."""
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

    async def generate_csid(self, email: str):
        user: UserOut = self.user_service.get_by_email(email)
        private_key, csr_base64 = self.generate_private_key_and_csr(user)


