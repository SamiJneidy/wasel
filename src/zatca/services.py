from decimal import Decimal
import json
import base64
from typing import Optional
from httpx import BasicAuth
from fastapi import status
import os
import re
import uuid
from cryptography import x509
from cryptography.x509.oid import NameOID, ObjectIdentifier
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from src.users.schemas import UserInDB
from src.core.utils.json_helper import ToStrEncoder
from src.core.utils.math_helper import round_decimal
from .schemas import (
    ZatcaCSIDCreate,
    ZatcaCSIDResponse, 
    ZatcaSimplifiedInvoiceResponse, 
    ZatcaStandardInvoiceResponse, 
    ZatcaComplianceInvoiceResponse, 
    ZatcaComplianceCSIDRequest, 
    ZatcaCSIDInDB,
    ZatcaBranchMetadataCreate,
    ZatcaBranchMetadataOut,
    ZatcaBranchMetadataInDB,
    ZatcaInvoiceLineMetadata,
    ZatcaInvoiceMetadata
)
from src.branches.schemas import BranchUpdate
from src.core.config import settings
from src.core.services import AsyncRequestService
from src.core.enums import InvoiceType, ZatcaStage, BranchStatus, OrganizationTaxScheme
from src.sale_invoices.schemas import SaleInvoiceOut
from .repositories import ZatcaRepository
from .exceptions import CSIDNotIssuedException, ZatcaRequestFailedException, InvoiceNotAcceptedException, InvoiceSigningException
from .utils.invoice_helper import invoice_helper
from src.branches.services import BranchService
from .exceptions import ZatcaBranchMetadataNotFoundException, ZatcaBranchMetadataNotAllowedException

class ZatcaService:
    def __init__(self, zatca_repo: ZatcaRepository, request_service: AsyncRequestService, branch_service: BranchService):
        self.request_service = request_service
        self.zatca_repo = zatca_repo
        self.branch_service = branch_service

    def _generate_private_key(self):
        """Returns a private key object, not a serialized string."""
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    def _generate_serial_number(self) -> str:
        """Generates a serial number for CSR generation."""
        serial_uuid = str(uuid.uuid4())
        serial_number = "|".join(["1-Wasel", "2-v1", f"3-{serial_uuid}"])
        return serial_number

    def _generate_private_key_and_csr(self, branch: ZatcaBranchMetadataInDB) -> tuple[str, str]:
        """Generates a private key and CSR in base64 and returns them as a tuple of strings (private_key, csr_base64)."""
        private_key = self._generate_private_key()
        # Build the CSR
        csr_builder = x509.CertificateSigningRequestBuilder()
        csr_builder = csr_builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, branch.country_code),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, branch.organization_unit_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, branch.organization_name),
            x509.NameAttribute(NameOID.COMMON_NAME, branch.common_name)
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
                    x509.NameAttribute(ObjectIdentifier("2.5.4.4"), self._generate_serial_number()),
                    x509.NameAttribute(ObjectIdentifier("0.9.2342.19200300.100.1.1"), branch.vat_number),
                    x509.NameAttribute(ObjectIdentifier("2.5.4.12"), branch.invoicing_type),
                    x509.NameAttribute(ObjectIdentifier("2.5.4.26"), branch.address),
                    x509.NameAttribute(ObjectIdentifier("2.5.4.15"), branch.business_category)
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
    
    async def _send_compliance_csid_request(self, csr_base64: str, otp: str) -> ZatcaCSIDResponse:
        json_payload = json.dumps({'csr': csr_base64})
        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'OTP': otp,
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }
        response = await self.request_service.post(settings.ZATCA_COMPLIANCE_CSID_URL, headers, json_payload)
        if not response:
            raise ZatcaRequestFailedException()
        if response.status_code != status.HTTP_200_OK:
            try:
                response_json: dict = response.json()
                zatca_error_message = invoice_helper.extract_error_message_from_response(response_json)
            except Exception:
                zatca_error_message = "Zatca could not process the request"
                response_json = None

            raise CSIDNotIssuedException(
                detail=zatca_error_message,
                status_code=response.status_code,
            )
        response_json: dict = response.json()
        return ZatcaCSIDResponse(
            request_id=response_json.get("requestID"),
            disposition_message=response_json.get("dispositionMessage"),
            binary_security_token=response_json.get("binarySecurityToken"),
            secret=response_json.get("secret")
        )

    async def _send_production_csid_request(self, request_id: str, binary_security_token: str, secret: str) -> ZatcaCSIDResponse:
        json_payload = json.dumps({'compliance_request_id': request_id})
        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }
        auth = BasicAuth(binary_security_token, secret)
        response = await self.request_service.post(settings.ZATCA_PRODUCTION_CSID_URL, headers, json_payload, auth)
        if not response:
            raise ZatcaRequestFailedException()
        if response.status_code != status.HTTP_200_OK:
            try:
                response_json: dict = response.json()
                zatca_error_message = invoice_helper.extract_error_message_from_response(response_json)
            except Exception:
                zatca_error_message = "Zatca could not process the request"
                response_json = None
            raise CSIDNotIssuedException(
                detail=zatca_error_message,
                status_code=response.status_code,
                zatca_response=response_json
            )
        response_json: dict = response.json()
        return ZatcaCSIDResponse(
            request_id=response_json.get("requestID"),
            disposition_message=response_json.get("dispositionMessage"),
            binary_security_token=response_json.get("binarySecurityToken"),
            secret=response_json.get("secret")
        )

    async def _generate_compliance_csid(self, branch_metadata: ZatcaBranchMetadataInDB, zatca_otp: str) -> ZatcaCSIDInDB:
        private_key, csr_base64 = self._generate_private_key_and_csr(branch_metadata)
        zatca_csid = await self._send_compliance_csid_request(csr_base64, zatca_otp)
        certificate = base64.b64decode(zatca_csid.binary_security_token).decode('utf-8')
        authorization = zatca_csid.binary_security_token + ':' + zatca_csid.secret
        authorization_base64 = base64.b64encode(authorization.encode('utf-8')).decode('utf-8')
        csid_data = ZatcaCSIDCreate(
            stage=ZatcaStage.COMPLIANCE,
            private_key=private_key, 
            csr_base64=csr_base64, 
            certificate=certificate,
            authorization=authorization_base64,
            request_id=zatca_csid.request_id,
            disposition_message=zatca_csid.disposition_message,
            binary_security_token=zatca_csid.binary_security_token,
            secret=zatca_csid.secret
        )
        csid = await self.zatca_repo.create_csid(branch_metadata.organization_id, branch_metadata.branch_id, csid_data.model_dump())
        return ZatcaCSIDInDB.model_validate(csid)
    
    async def _generate_production_csid(self, branch_metadata: ZatcaBranchMetadataInDB) -> ZatcaCSIDInDB:
        # TO BE ADDED
        # Validations on branch if it's completed
        compliance_csid = await self.zatca_repo.get_csid_by_branch(
            branch_metadata.organization_id, 
            branch_metadata.branch_id, 
            ZatcaStage.PRODUCTION
        )
        zatca_csid = await self._send_production_csid_request(
            compliance_csid.request_id, 
            compliance_csid.binary_security_token, 
            compliance_csid.secret
        )
        certificate = base64.b64decode(zatca_csid.binary_security_token).decode('utf-8')
        authorization = zatca_csid.binary_security_token + ':' + zatca_csid.secret
        authorization_base64 = base64.b64encode(authorization.encode('utf-8')).decode('utf-8')
        csid_data = ZatcaCSIDCreate(
            stage=ZatcaStage.PRODUCTION,
            private_key=compliance_csid.private_key, 
            csr_base64=compliance_csid.csr_base64, 
            certificate=certificate,
            authorization=authorization_base64,
            request_id=zatca_csid.request_id,
            disposition_message=zatca_csid.disposition_message,
            binary_security_token=zatca_csid.binary_security_token,
            secret=zatca_csid.secret
        )
        csid = await self.zatca_repo.create_csid(branch_metadata.organization_id, branch_metadata.branch_id, csid_data.model_dump())
        return ZatcaCSIDInDB.model_validate(csid)

    async def get_csid(self, organization_id: int, branch_id: int, stage: ZatcaStage) -> ZatcaCSIDInDB | None:
        csid = await self.zatca_repo.get_csid_by_branch(organization_id, branch_id, stage)
        if csid is None:
            return None
        return ZatcaCSIDInDB.model_validate(csid)

    async def _send_compliance_invoice(self, invoice_request: dict, invoice_type: InvoiceType, binary_security_token: str, secret: str) -> ZatcaComplianceInvoiceResponse:
        json_payload = json.dumps(invoice_request)
        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }
        auth = BasicAuth(binary_security_token, secret)
        response = await self.request_service.post(settings.ZATCA_COMPLIANCE_INVOICE_URL, headers, json_payload, auth)
        try:
            response_json: dict = response.json()
        except Exception:
            raise ZatcaRequestFailedException()
        if invoice_type == InvoiceType.STANDARD and response_json.get("clearanceStatus") != "CLEARED":
            raise InvoiceNotAcceptedException(zatca_response=response_json)
        elif invoice_type == InvoiceType.SIMPLIFIED and response_json.get("reportingStatus") != "REPORTED":
            raise InvoiceNotAcceptedException(zatca_response=response_json)
        return ZatcaComplianceInvoiceResponse(
            status_code=response.status_code,
            zatca_response=response_json
        )

    async def _send_standard_invoice(self, invoice_request: dict, binary_security_token: str, secret: str) -> ZatcaStandardInvoiceResponse:
        json_payload = json.dumps(invoice_request)
        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }
        auth = BasicAuth(binary_security_token, secret)
        response = await self.request_service.post(settings.ZATCA_STANDARD_INVOICE_URL, headers, json_payload, auth)
        try:
            response_json: dict = response.json()
        except Exception:
            raise ZatcaRequestFailedException()
        if response_json.get("clearanceStatus") != "CLEARED":
            raise InvoiceNotAcceptedException(zatca_response=response_json)
        return ZatcaStandardInvoiceResponse(
            status=response_json.get("clearanceStatus"),
            status_code=response.status_code,
            invoice=response_json.get("clearedInvoice"),
            zatca_response=response_json
        )

    async def _send_simplified_invoice(self, invoice_request: dict, binary_security_token: str, secret: str) -> ZatcaSimplifiedInvoiceResponse:
        json_payload = json.dumps(invoice_request)
        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }
        auth = BasicAuth(binary_security_token, secret)
        response = await self.request_service.post(settings.ZATCA_SIMPLIFIED_INVOICE_URL, headers, json_payload, auth)
        try:
            response_json: dict = response.json()
        except Exception:
            raise ZatcaRequestFailedException()
        if response_json.get("reportingStatus") != "REPORTED":
            raise InvoiceNotAcceptedException(zatca_response=response_json)
        return ZatcaSimplifiedInvoiceResponse(
            status=response_json.get("reportingStatus"),
            status_code=response.status_code,
            zatca_response=response_json
        )

    async def create_branch_metadata(self, user: UserInDB, branch_id: int, data: ZatcaBranchMetadataCreate) -> ZatcaBranchMetadataInDB:
        if user.organization.tax_scheme != OrganizationTaxScheme.ZATCA_PHASE2:
            raise ZatcaBranchMetadataNotAllowedException()
        branch = await self.branch_service.get_branch(user, branch_id)
        payload = data.model_dump(exclude={"zatca_otp"})
        payload.update({
            "icv": 1,
            "stage": ZatcaStage.COMPLIANCE,
        })
        branch_metadata = await self.zatca_repo.create_branch_metadata(user.id, user.organization_id, branch_id, payload)
        await self._generate_compliance_csid(branch_metadata, data.zatca_otp)
        await self.branch_service.update_branch_status(user, branch_id, BranchStatus.COMPLETED)
        return ZatcaBranchMetadataInDB.model_validate(branch_metadata)   
    
    async def get_branch_metadata(self, user: UserInDB, branch_id: int) -> ZatcaBranchMetadataInDB:
        branch = await self.zatca_repo.get_branch_metadata_by_branch(branch_id)
        if branch is None:
            raise ZatcaBranchMetadataNotFoundException()
        return ZatcaBranchMetadataInDB.model_validate(branch)

    async def _get_new_pih(self, organization_id: int, branch_id: int, stage: ZatcaStage) -> str:
        pih = await self.zatca_repo.get_pih(organization_id, branch_id, stage)
        if pih is None:
            return "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ=="
        return pih

    async def _get_new_icv(self, organization_id: int, branch_id: int, stage: ZatcaStage) -> str:
        icv = await self.zatca_repo.get_icv(organization_id, branch_id, stage)
        if icv is None:
            return 1
        return icv+1

    async def create_invoice_metadata(self, invoice_id: int, data: ZatcaInvoiceMetadata) -> ZatcaInvoiceMetadata:
        metadata = await self.zatca_repo.create_invoice_metadata(invoice_id, data.model_dump())
        return ZatcaInvoiceMetadata.model_validate(metadata)

    async def create_line_metadata(self, invoice_id: int, invoice_line_id: int, data: ZatcaInvoiceLineMetadata) -> ZatcaInvoiceLineMetadata:
        metadata = await self.zatca_repo.create_line_metadata(invoice_id, invoice_line_id, data.model_dump())
        return ZatcaInvoiceLineMetadata.model_validate(metadata)
    
    async def get_invoice_metadata(self, invoice_id: int) -> Optional[ZatcaInvoiceMetadata]:
        metadata = await self.zatca_repo.get_invoice_metadata(invoice_id)
        if metadata is None:
            return None
        return ZatcaInvoiceMetadata.model_validate(metadata)

    async def get_line_metadata(self, invoice_line_id: int) -> Optional[ZatcaInvoiceLineMetadata]:
        metadata = await self.zatca_repo.get_line_metadata(invoice_line_id)
        if metadata is None:
            return None
        return ZatcaInvoiceLineMetadata.model_validate(metadata)
    
    async def delete_invoice_metadata(self, invoice_id: int) -> None:
        await self.zatca_repo.delete_invoice_metadata(invoice_id)
        return None
    
    async def delete_lines_metadata(self, invoice_id: int) -> None:
        await self.zatca_repo.delete_lines_metadata(invoice_id)
        return None

    async def _prepare_invoice_for_signing(self, branch_metadata: ZatcaBranchMetadataInDB, invoice: SaleInvoiceOut) -> dict[str, str]:
        """Create a dictionary representing the invoice and transform all numeric values into strings."""
        invoice_lines = invoice.invoice_lines
        invoice_dict = invoice.model_dump(exclude_none=True, exclude_unset=True)
        pih = await self._get_new_pih(branch_metadata.organization_id, branch_metadata.branch_id, branch_metadata.stage)
        icv = await self._get_new_icv(branch_metadata.organization_id, branch_metadata.branch_id, branch_metadata.stage)
        invoice_dict.update({
            "pih": pih,
            "icv": icv,
            "stage": branch_metadata.stage
        })
        # Add item price before discount
        for line in invoice_dict["invoice_lines"]:
            line.update({
                "item_price_before_discount": line["item_price"],
                "item_price_after_discount": round_decimal(line["item_price"] - line["price_discount"], 2),
            })

        tax_categories = {
            'S': {"taxable_amount": Decimal("0"), "tax_amount": Decimal("0"), "classified_tax_category": 'S', "tax_rate": Decimal(settings.STANDARD_TAX_RATE), "tax_exemption_reason_code": None, "tax_exemption_reason": None, "used": False},
            'Z': {"taxable_amount": Decimal("0"), "tax_amount": Decimal("0"), "classified_tax_category": 'Z', "tax_rate": Decimal("0"), "tax_exemption_reason_code": None, "tax_exemption_reason": None, "used": False},
            'E': {"taxable_amount": Decimal("0"), "tax_amount": Decimal("0"), "classified_tax_category": 'E', "tax_rate": Decimal("0"), "tax_exemption_reason_code": None, "tax_exemption_reason": None, "used": False},
            'O': {"taxable_amount": Decimal("0"), "tax_amount": Decimal("0"), "classified_tax_category": 'O', "tax_rate": Decimal("0"), "tax_exemption_reason_code": None, "tax_exemption_reason": None, "used": False},
        }

        # Invoice can have document level discount amount only if all lines have the same VAT category
        if invoice.discount_amount > 0:
            line_metadata = await self.get_line_metadata(invoice_lines[0].id)
            tax_exemption_reason_code = line_metadata.tax_exemption_reason_code if line_metadata else None
            tax_exemption_reason = line_metadata.tax_exemption_reason if line_metadata else None
            has_total_discount = True
            tax_category = invoice_lines[0].classified_tax_category
            tax_categories[tax_category]['used'] = True
            tax_categories[tax_category]['taxable_amount'] = invoice.taxable_amount
            tax_categories[tax_category]['tax_amount'] = invoice.tax_amount
            tax_categories[tax_category]['tax_exemption_reason_code'] = tax_exemption_reason_code
            tax_categories[tax_category]['tax_exemption_reason'] = tax_exemption_reason
        else:
            has_total_discount = False
            for line in invoice_lines:
                line_metadata = await self.get_line_metadata(line.id)
                tax_exemption_reason_code = line_metadata.tax_exemption_reason_code if line_metadata else None
                tax_exemption_reason = line_metadata.tax_exemption_reason if line_metadata else None
                tax_category = line.classified_tax_category
                tax_categories[tax_category]['taxable_amount'] += line.line_extension_amount
                tax_categories[tax_category]['tax_amount'] += line.tax_amount
                tax_categories[tax_category]['tax_exemption_reason_code'] = tax_exemption_reason_code
                tax_categories[tax_category]['tax_exemption_reason'] = tax_exemption_reason_code
                tax_categories[tax_category]['used'] = True
        tax_categories = {k: v for k, v in tax_categories.items() if v['used'] == True}

        invoice_dict.update({
            "has_total_discount": has_total_discount,
            "supplier": branch_metadata.model_dump(),
            "tax_categories": tax_categories
        })
        invoice_json = json.dumps(invoice_dict, cls=ToStrEncoder)
        invoice_dict: dict = json.loads(invoice_json, parse_int=lambda x: str(x))
        return invoice_dict    

    async def sign_and_send_to_zatca(self, user: UserInDB, invoice: SaleInvoiceOut) -> ZatcaInvoiceMetadata:
        """Signs the invoice and send it to zatca."""
        branch_metadata = await self.get_branch_metadata(user, user.branch_id)
        csid = await self.get_csid(user.organization_id, user.branch_id, branch_metadata.stage)
        invoice_data = await self._prepare_invoice_for_signing(branch_metadata, invoice)
        try:
            invoice_request = invoice_helper.sign_and_get_request(invoice_data, csid.private_key, csid.certificate)
        except Exception as e:
            raise InvoiceSigningException()
        # with open('inv.xml', "w") as f:
        #     f.write(base64.b64decode(invoice_request["invoice"]).decode())
        if (branch_metadata.stage == ZatcaStage.COMPLIANCE):
            zatca_result = await self._send_compliance_invoice(invoice_request, invoice.invoice_type, csid.binary_security_token, csid.secret)
        elif (branch_metadata.stage== ZatcaStage.PRODUCTION and invoice.invoice_type == InvoiceType.STANDARD):
            zatca_result = await self._send_standard_invoice(invoice_request, csid.binary_security_token, csid.secret)
        elif (branch_metadata.stage == ZatcaStage.PRODUCTION and invoice.invoice_type == InvoiceType.SIMPLIFIED):
            zatca_result = await self._send_simplified_invoice(invoice_request, csid.binary_security_token, csid.secret)
        else:
            raise ZatcaRequestFailedException()
        
        if invoice.invoice_type == InvoiceType.SIMPLIFIED:
            base64_invoice = invoice_request.get("invoice", None)
            zatca_response = json.dumps(zatca_result.zatca_response)
        elif invoice.invoice_type == InvoiceType.STANDARD:
            base64_invoice = zatca_result.zatca_response.get("clearedInvoice", None)
            zatca_result.zatca_response.pop("clearedInvoice", None)
            zatca_response = json.dumps(zatca_result.zatca_response)

        metadata = ZatcaInvoiceMetadata(
            pih = invoice_data["pih"], 
            icv = invoice_data["icv"],
            signed_xml_base64 = base64_invoice,
            base64_qr_code = invoice_helper.extract_base64_qr_code(base64_invoice),
            invoice_hash = invoice_request["invoiceHash"],
            stage = branch_metadata.stage,
            status_code = zatca_result.status_code,
            response = zatca_response,
        )

        metadata = await self.create_invoice_metadata(invoice_id=invoice.id, data=metadata)
        await self.zatca_repo.update_pih_and_icv(branch_metadata.branch_id, invoice_request["invoiceHash"])
        return metadata
