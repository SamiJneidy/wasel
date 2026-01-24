from datetime import datetime
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
    ZatcaPhase2BranchDataComplete,
    ZatcaPhase2CSIDCreate,
    ZatcaPhase2CSIDResponse,
    ZatcaPhase2InvoiceResponse,
    ZatcaPhase2ComplianceCSIDRequest,
    ZatcaPhase2CSIDInDB,
    ZatcaPhase2BranchDataCreate,
    ZatcaPhase2BranchDataOut,
    ZatcaPhase2BranchDataInDB,
    ZatcaPhase2InvoiceLineDataCreate,
    ZatcaPhase2InvoiceLineDataOut,
    ZatcaPhase2InvoiceDataOut
)
from src.branches.schemas import BranchUpdate
from src.core.config import settings
from src.core.services import AsyncRequestService
from ..services import TaxAuthorityService
from src.core.enums import BranchTaxIntegrationStatus, InvoiceTaxAuthorityStatus, InvoiceType, InvoiceTypeCode, InvoicingType, ZatcaPhase2Stage, BranchStatus, TaxAuthority
from src.sale_invoices.schemas import SaleInvoiceOut
from .repositories import ZatcaRepository
from .utils.invoice_helper import invoice_helper
from src.branches.services import BranchService
from .exceptions import (
    ZatcaCSIDNotIssuedException,
    ZatcaRequestFailedException,
    ZatcaInvoiceSigningException,
    ZatcaBranchDataNotFoundException,
    ZatcaRequestFailedException,
)
from ..exceptions import IncorrectTaxAuthorityException, InvoiceNotAcceptedException
from src.items.services import ItemService
from src.customers.services import CustomerService
from src.core.consts import KSA_TZ
from src.sale_invoices.services.raw_service import SaleInvoiceServiceRaw
from src.sale_invoices.schemas import SaleInvoiceOut, SaleInvoiceCreate

class ZatcaPhase2Service(TaxAuthorityService):
    def __init__(self,
        zatca_repo: ZatcaRepository,
        request_service: AsyncRequestService,
        item_service: ItemService,
        customer_service: CustomerService,
        sale_invoice_service: SaleInvoiceServiceRaw,
    ):
        self.request_service = request_service
        self.zatca_repo = zatca_repo
        self.customer_service = customer_service
        self.item_service = item_service
        self.sale_invoice_service = sale_invoice_service

    def _convert_dict_to_str(self, data: dict) -> dict[str, str]:
        data_json = json.dumps(data, cls=ToStrEncoder)
        return json.loads(data_json, parse_int=lambda x: str(x))

    def _generate_private_key(self):
        """Returns a private key object, not a serialized string."""
        return ec.generate_private_key(ec.SECP256K1(), default_backend())

    def _generate_serial_number(self) -> str:
        """Generates a serial number for CSR generation."""
        serial_uuid = str(uuid.uuid4())
        serial_number = "|".join(["1-Wasel", "2-v1", f"3-{serial_uuid}"])
        return serial_number

    def _generate_private_key_and_csr(self, branch: ZatcaPhase2BranchDataInDB) -> tuple[str, str]:
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
    
    async def _get_new_pih(self, organization_id: int, branch_id: int, stage: ZatcaPhase2Stage) -> str:
        pih = await self.zatca_repo.get_pih(organization_id, branch_id, stage)
        if pih is None:
            return "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ=="
        return pih

    async def _get_new_icv(self, organization_id: int, branch_id: int, stage: ZatcaPhase2Stage) -> str:
        icv = await self.zatca_repo.get_icv(organization_id, branch_id, stage)
        if icv is None:
            return 1
        return icv+1

    async def _send_compliance_csid_request(self, csr_base64: str, otp: str) -> ZatcaPhase2CSIDResponse:
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

            raise ZatcaCSIDNotIssuedException(
                detail=zatca_error_message,
                status_code=response.status_code,
            )
        response_json: dict = response.json()
        return ZatcaPhase2CSIDResponse(
            request_id=response_json.get("requestID"),
            disposition_message=response_json.get("dispositionMessage"),
            binary_security_token=response_json.get("binarySecurityToken"),
            secret=response_json.get("secret")
        )

    async def _send_production_csid_request(self, request_id: str, binary_security_token: str, secret: str) -> ZatcaPhase2CSIDResponse:
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
            raise ZatcaCSIDNotIssuedException(
                detail=zatca_error_message,
                status_code=response.status_code,
                zatca_response=response_json
            )
        response_json: dict = response.json()
        return ZatcaPhase2CSIDResponse(
            request_id=response_json.get("requestID"),
            disposition_message=response_json.get("dispositionMessage"),
            binary_security_token=response_json.get("binarySecurityToken"),
            secret=response_json.get("secret")
        )

    async def _generate_compliance_csid(self, branch_tax_authority_data: ZatcaPhase2BranchDataInDB, zatca_otp: str) -> ZatcaPhase2CSIDInDB:
        private_key, csr_base64 = self._generate_private_key_and_csr(branch_tax_authority_data)
        zatca_csid = await self._send_compliance_csid_request(csr_base64, zatca_otp)
        certificate = base64.b64decode(zatca_csid.binary_security_token).decode('utf-8')
        authorization = zatca_csid.binary_security_token + ':' + zatca_csid.secret
        authorization_base64 = base64.b64encode(authorization.encode('utf-8')).decode('utf-8')
        csid_data = ZatcaPhase2CSIDCreate(
            private_key=private_key, 
            csr_base64=csr_base64, 
            certificate=certificate,
            authorization=authorization_base64,
            request_id=zatca_csid.request_id,
            disposition_message=zatca_csid.disposition_message,
            binary_security_token=zatca_csid.binary_security_token,
            secret=zatca_csid.secret
        )
        data = csid_data.model_dump()
        data.update({"stage": ZatcaPhase2Stage.COMPLIANCE})
        csid = await self.zatca_repo.create_csid(branch_tax_authority_data.organization_id, branch_tax_authority_data.branch_id, data)
        return ZatcaPhase2CSIDInDB.model_validate(csid)
    
    async def _generate_production_csid(self, branch_tax_authority_data: ZatcaPhase2BranchDataInDB) -> ZatcaPhase2CSIDInDB:
        compliance_csid = await self.zatca_repo.get_csid_by_branch(
            branch_tax_authority_data.organization_id, 
            branch_tax_authority_data.branch_id, 
            ZatcaPhase2Stage.COMPLIANCE
        )
        zatca_csid = await self._send_production_csid_request(
            compliance_csid.request_id, 
            compliance_csid.binary_security_token, 
            compliance_csid.secret
        )
        certificate = base64.b64decode(zatca_csid.binary_security_token).decode('utf-8')
        authorization = zatca_csid.binary_security_token + ':' + zatca_csid.secret
        authorization_base64 = base64.b64encode(authorization.encode('utf-8')).decode('utf-8')
        csid_data = ZatcaPhase2CSIDCreate(
            private_key=compliance_csid.private_key, 
            csr_base64=compliance_csid.csr_base64, 
            certificate=certificate,
            authorization=authorization_base64,
            request_id=zatca_csid.request_id,
            disposition_message=zatca_csid.disposition_message,
            binary_security_token=zatca_csid.binary_security_token,
            secret=zatca_csid.secret
        )
        data = csid_data.model_dump()
        data.update({"stage": ZatcaPhase2Stage.PRODUCTION})
        csid = await self.zatca_repo.create_csid(branch_tax_authority_data.organization_id, branch_tax_authority_data.branch_id, data)
        return ZatcaPhase2CSIDInDB.model_validate(csid)

    async def _get_csid(self, organization_id: int, branch_id: int, stage: ZatcaPhase2Stage) -> ZatcaPhase2CSIDInDB | None:
        csid = await self.zatca_repo.get_csid_by_branch(organization_id, branch_id, stage)
        if csid is None:
            return None
        return ZatcaPhase2CSIDInDB.model_validate(csid)

    async def _send_compliance_invoice(self, invoice_request: dict, invoice_type: InvoiceType, binary_security_token: str, secret: str) -> ZatcaPhase2InvoiceResponse:
        json_payload = json.dumps(invoice_request)
        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }
        auth = BasicAuth(binary_security_token, secret)
        response = await self.request_service.post(settings.ZATCA_COMPLIANCE_INVOICE_URL, headers, json_payload, auth)
        if response.status_code == status.HTTP_200_OK:
            zatca_status = InvoiceTaxAuthorityStatus.ACCEPTED
        elif response.status_code == status.HTTP_201_CREATED or response.status_code == status.HTTP_202_ACCEPTED:
            zatca_status = InvoiceTaxAuthorityStatus.ACCEPTED_WITH_WARNINGS
        else:
            zatca_status = InvoiceTaxAuthorityStatus.REJECTED
        try:
            response_json: dict = response.json()
        except Exception:
            zatca_status = InvoiceTaxAuthorityStatus.NOT_SENT
        return ZatcaPhase2InvoiceResponse(
            tax_authority=TaxAuthority.ZATCA_PHASE2,
            status=zatca_status,
            status_code=response.status_code,
            response=response_json, 
        )

    async def _send_standard_invoice(self, invoice_request: dict, binary_security_token: str, secret: str) -> ZatcaPhase2InvoiceResponse:
        json_payload = json.dumps(invoice_request)
        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }
        auth = BasicAuth(binary_security_token, secret)

        response = await self.request_service.post(settings.ZATCA_STANDARD_INVOICE_URL, headers, json_payload, auth)
        if response.status_code == status.HTTP_200_OK:
            zatca_status = InvoiceTaxAuthorityStatus.ACCEPTED
        elif response.status_code == status.HTTP_201_CREATED or response.status_code == status.HTTP_202_ACCEPTED:
            zatca_status = InvoiceTaxAuthorityStatus.ACCEPTED_WITH_WARNINGS
        else:
            zatca_status = InvoiceTaxAuthorityStatus.REJECTED
        try:
            response_json: dict = response.json()
        except Exception:
            zatca_status = InvoiceTaxAuthorityStatus.NOT_SENT
        return ZatcaPhase2InvoiceResponse(
            tax_authority=TaxAuthority.ZATCA_PHASE2,
            status=zatca_status,
            status_code=response.status_code,
            signed_xml_base64=response_json.get("clearedInvoice"),
            response=response_json
        )

    async def _send_simplified_invoice(self, invoice_request: dict, binary_security_token: str, secret: str) -> ZatcaPhase2InvoiceResponse:
        json_payload = json.dumps(invoice_request)
        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'Accept-Version': 'V2',
            'Content-Type': 'application/json',
        }
        auth = BasicAuth(binary_security_token, secret)
        response = await self.request_service.post(settings.ZATCA_SIMPLIFIED_INVOICE_URL, headers, json_payload, auth)
        if response.status_code == status.HTTP_200_OK:
            zatca_status = InvoiceTaxAuthorityStatus.ACCEPTED
        elif response.status_code == status.HTTP_201_CREATED or response.status_code == status.HTTP_202_ACCEPTED:
            zatca_status = InvoiceTaxAuthorityStatus.ACCEPTED_WITH_WARNINGS
        else:
            zatca_status = InvoiceTaxAuthorityStatus.REJECTED
        try:
            response_json: dict = response.json()
        except Exception:
            zatca_status = InvoiceTaxAuthorityStatus.NOT_SENT
        return ZatcaPhase2InvoiceResponse(
            tax_authority=TaxAuthority.ZATCA_PHASE2,
            status=zatca_status,
            status_code=response.status_code,
            response=response_json
        )

    async def _prepare_invoice_for_signing(self, user: UserInDB, branch_tax_authority_data: ZatcaPhase2BranchDataInDB, invoice: SaleInvoiceOut) -> dict[str, str]:
        """Create a dictionary representing the invoice and transform all numeric values into strings."""
        invoice_lines = invoice.invoice_lines
        invoice_dict = invoice.model_dump(exclude_none=True, exclude_unset=True)
        pih = await self._get_new_pih(branch_tax_authority_data.organization_id, branch_tax_authority_data.branch_id, branch_tax_authority_data.stage)
        icv = await self._get_new_icv(branch_tax_authority_data.organization_id, branch_tax_authority_data.branch_id, branch_tax_authority_data.stage)
        invoice_dict.update({
            "pih": pih,
            "icv": icv,
            "stage": branch_tax_authority_data.stage
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
            line_tax_authority_data = await self.get_line_tax_authority_data(user, invoice_lines[0].id)
            tax_exemption_reason_code = line_tax_authority_data.tax_exemption_reason_code if line_tax_authority_data else None
            tax_exemption_reason = line_tax_authority_data.tax_exemption_reason if line_tax_authority_data else None
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
                line_tax_authority_data = await self.get_line_tax_authority_data(user, line.id)
                tax_exemption_reason_code = line_tax_authority_data.tax_exemption_reason_code if line_tax_authority_data else None
                tax_exemption_reason = line_tax_authority_data.tax_exemption_reason if line_tax_authority_data else None
                tax_category = line.classified_tax_category
                tax_categories[tax_category]['taxable_amount'] += line.line_extension_amount
                tax_categories[tax_category]['tax_amount'] += line.tax_amount
                tax_categories[tax_category]['tax_exemption_reason_code'] = tax_exemption_reason_code
                tax_categories[tax_category]['tax_exemption_reason'] = tax_exemption_reason_code
                tax_categories[tax_category]['used'] = True
        tax_categories = {k: v for k, v in tax_categories.items() if v['used'] == True}

        invoice_dict.update({
            "has_total_discount": has_total_discount,
            "supplier": branch_tax_authority_data.model_dump(),
            "tax_categories": tax_categories
        })
        return self._convert_dict_to_str(invoice_dict)

    async def _send_compliance_invoices(self, user: UserInDB, invoicing_type: InvoicingType) -> None:
        invoice_types = []
        if invoicing_type == InvoicingType.STANDARD:
            invoice_types = [InvoiceType.STANDARD]
        elif invoicing_type == InvoicingType.SIMPLIFIED:
            invoice_types = [InvoiceType.SIMPLIFIED]
        else:
            invoice_types = [InvoiceType.STANDARD, InvoiceType.SIMPLIFIED]
        invoice_type_codes = [InvoiceTypeCode.INVOICE, InvoiceTypeCode.CREDIT_NOTE, InvoiceTypeCode.DEBIT_NOTE]
        from .utils.templates.invoice_data import invoice_data_template
        last_invoice_number = ""
        pih = "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ=="
        icv = 1
        branch_tax_authority_data = await self._get_branch_tax_authority_data_by_stage(user, user.branch_id, ZatcaPhase2Stage.COMPLIANCE)
        csid = await self._get_csid(user.organization_id, user.branch_id, ZatcaPhase2Stage.COMPLIANCE)
        for type in invoice_types:
            for code in invoice_type_codes:
                invoice_data = invoice_data_template.copy()
                invoice_data["supplier"] = branch_tax_authority_data.model_dump()
                invoice_data["invoice_number"] = f"wasel-test-inv-000{icv}"
                invoice_data["uuid"] = str(uuid.uuid4())
                invoice_data["icv"] = icv
                invoice_data["pih"] = pih
                invoice_data["invoice_type"] = type
                invoice_data["invoice_type_code"] = code
                invoice_data["issue_date"] = datetime.now(KSA_TZ).date().isoformat()
                invoice_data["issue_time"] = datetime.now(KSA_TZ).time().isoformat(timespec='seconds')
                invoice_data["actual_delivery_date"] = datetime.now(KSA_TZ).date().isoformat()
                if code != InvoiceTypeCode.INVOICE:
                    invoice_data["original_invoice_number"] = last_invoice_number
                    invoice_data["instruction_note"] = "Correction of invoice"
                invoice_data = self._convert_dict_to_str(invoice_data)
                try:
                    invoice_request = invoice_helper.sign_and_get_request(invoice_data, csid.private_key, csid.certificate)
                    with open(f"invoice-{icv}.xml", "w") as f:
                        f.write(base64.b64decode(invoice_request["invoice"]).decode())    
                except Exception as e:
                    raise ZatcaCSIDNotIssuedException(detail="Could not create invoice for compliance submission")
                zatca_response = await self._send_compliance_invoice(invoice_request, type, csid.binary_security_token, csid.secret)
                if zatca_response.status_code not in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_202_ACCEPTED, status.HTTP_409_CONFLICT]:
                    raise ZatcaCSIDNotIssuedException(detail="One or more of the compliance invoices were not accepted by Zatca")
                icv += 1
                pih = invoice_request["invoiceHash"]
                if code == InvoiceTypeCode.INVOICE:
                    last_invoice_number = invoice_data["invoice_number"]
        return None
        
    async def create_branch_tax_authority_data(self, user: UserInDB, branch_id: int, data: ZatcaPhase2BranchDataCreate) -> ZatcaPhase2BranchDataInDB:
        if user.organization.tax_authority != TaxAuthority.ZATCA_PHASE2:
            raise IncorrectTaxAuthorityException()
        
        payload = data.model_dump()
        payload.update({
            "icv": 1,
            "stage": ZatcaPhase2Stage.COMPLIANCE,
            "pih": "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ==",
        })
        branch_tax_authority_data = await self.zatca_repo.create_branch_tax_authority_data(user.id, user.organization_id, branch_id, payload)
        return ZatcaPhase2BranchDataInDB.model_validate(branch_tax_authority_data)   
    
    async def complete_branch_tax_authority_data(self, user: UserInDB, branch_id: int, data: ZatcaPhase2BranchDataComplete) -> ZatcaPhase2BranchDataInDB:
        if user.organization.tax_authority != TaxAuthority.ZATCA_PHASE2:
            raise IncorrectTaxAuthorityException()
        branch_tax_authority_data = await self._get_branch_tax_authority_data_by_stage(user, branch_id, ZatcaPhase2Stage.COMPLIANCE)
        await self._generate_compliance_csid(branch_tax_authority_data, data.otp)
        await self._send_compliance_invoices(user, branch_tax_authority_data.invoicing_type)
        await self._generate_production_csid(branch_tax_authority_data)
        payload = ZatcaPhase2BranchDataCreate.model_validate(branch_tax_authority_data).model_dump()
        payload.update({
            "icv": 1,
            "pih": "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ==",
            "stage": ZatcaPhase2Stage.PRODUCTION,
        })
        branch_tax_authority_data = await self.zatca_repo.create_branch_tax_authority_data(user.id, user.organization_id, branch_id, payload)
        return ZatcaPhase2BranchDataInDB.model_validate(branch_tax_authority_data)   
    
    async def _get_branch_tax_authority_data_by_stage(self, user: UserInDB, branch_id: int, stage: ZatcaPhase2Stage) -> Optional[ZatcaPhase2BranchDataInDB]:
        tax_authority_data = await self.zatca_repo.get_branch_tax_authority_data_by_branch(branch_id, stage)
        if tax_authority_data is None:
            return None
            # raise ZatcaBranchDataNotFoundException()
        return ZatcaPhase2BranchDataInDB.model_validate(tax_authority_data)

    async def get_branch_tax_authority_data(self, user: UserInDB, branch_id: int, tax_integration_status: BranchTaxIntegrationStatus) -> Optional[ZatcaPhase2BranchDataInDB]:
        if tax_integration_status == BranchTaxIntegrationStatus.COMPLETED:
            tax_authority_data = await self.zatca_repo.get_branch_tax_authority_data_by_branch(branch_id, ZatcaPhase2Stage.PRODUCTION)
        else:
            tax_authority_data = await self.zatca_repo.get_branch_tax_authority_data_by_branch(branch_id, ZatcaPhase2Stage.COMPLIANCE)
        if tax_authority_data is None:
            return None
        return ZatcaPhase2BranchDataInDB.model_validate(tax_authority_data)

    async def create_invoice_tax_authority_data(self, user: UserInDB, invoice_id: int, data: ZatcaPhase2InvoiceDataOut) -> ZatcaPhase2InvoiceDataOut:
        tax_authority_data = await self.zatca_repo.create_invoice_tax_authority_data(invoice_id, data.model_dump())
        return ZatcaPhase2InvoiceDataOut.model_validate(tax_authority_data)

    async def create_line_tax_authority_data(self, user: UserInDB, invoice_id: int, invoice_line_id: int, data: ZatcaPhase2InvoiceLineDataCreate) -> ZatcaPhase2InvoiceLineDataOut:
        tax_authority_data = await self.zatca_repo.create_line_tax_authority_data(invoice_id, invoice_line_id, data.model_dump())
        return ZatcaPhase2InvoiceLineDataOut.model_validate(tax_authority_data)
    
    async def get_invoice_tax_authority_data(self, user: UserInDB, invoice_id: int) -> Optional[ZatcaPhase2InvoiceDataOut]:
        tax_authority_data = await self.zatca_repo.get_invoice_tax_authority_data(invoice_id)
        if tax_authority_data is None:
            return None
        return ZatcaPhase2InvoiceDataOut.model_validate(tax_authority_data)

    async def get_line_tax_authority_data(self, user: UserInDB, invoice_line_id: int) -> Optional[ZatcaPhase2InvoiceLineDataOut]:
        tax_authority_data = await self.zatca_repo.get_line_tax_authority_data(invoice_line_id)
        if tax_authority_data is None:
            return None
        return ZatcaPhase2InvoiceLineDataOut.model_validate(tax_authority_data)
    
    async def delete_invoice_tax_authority_data(self, user: UserInDB, invoice_id: int) -> None:
        await self.zatca_repo.delete_invoice_tax_authority_data(invoice_id)
        return None
    
    async def delete_lines_tax_authority_data(self, user: UserInDB, invoice_id: int) -> None:
        await self.zatca_repo.delete_lines_tax_authority_data(invoice_id)
        return None
        
    async def sign_and_submit_invoice(self, user: UserInDB, invoice: SaleInvoiceOut, metadata: dict = {}) -> ZatcaPhase2InvoiceDataOut:
        """Signs the invoice and send it to the relevant tax authority."""

        if user.branch.tax_integration_status == BranchTaxIntegrationStatus.COMPLETED:
            branch_tax_authority_data = await self._get_branch_tax_authority_data_by_stage(user, user.branch_id, ZatcaPhase2Stage.PRODUCTION)
        else:
            branch_tax_authority_data = await self._get_branch_tax_authority_data_by_stage(user, user.branch_id, ZatcaPhase2Stage.COMPLIANCE)
         
        if branch_tax_authority_data is None:
            raise ZatcaBranchDataNotFoundException()
        csid = await self._get_csid(user.organization_id, user.branch_id, branch_tax_authority_data.stage)
        invoice_data = await self._prepare_invoice_for_signing(user, branch_tax_authority_data, invoice)
        try:
            invoice_request = invoice_helper.sign_and_get_request(invoice_data, csid.private_key, csid.certificate)
        except Exception as e:
            raise ZatcaInvoiceSigningException()
        # with open('inv.xml', "w") as f:
        #     f.write(base64.b64decode(invoice_request["invoice"]).decode())
        if (branch_tax_authority_data.stage == ZatcaPhase2Stage.COMPLIANCE):
            zatca_result = await self._send_compliance_invoice(invoice_request, invoice.invoice_type, csid.binary_security_token, csid.secret)
        elif (branch_tax_authority_data.stage== ZatcaPhase2Stage.PRODUCTION and invoice.invoice_type == InvoiceType.STANDARD):
            zatca_result = await self._send_standard_invoice(invoice_request, csid.binary_security_token, csid.secret)
        elif (branch_tax_authority_data.stage == ZatcaPhase2Stage.PRODUCTION and invoice.invoice_type == InvoiceType.SIMPLIFIED):
            zatca_result = await self._send_simplified_invoice(invoice_request, csid.binary_security_token, csid.secret)
        else:
            raise ZatcaRequestFailedException()

        qr_code = invoice_helper.extract_base64_qr_code(zatca_result.signed_xml_base64)
        tax_authority_data = ZatcaPhase2InvoiceDataOut(
            **zatca_result.model_dump(),
            pih = invoice_data["pih"], 
            icv = invoice_data["icv"],
            base64_qr_code = qr_code,
            invoice_hash = invoice_request["invoiceHash"],
            stage = branch_tax_authority_data.stage,
        )
        tax_authority_data = await self.create_invoice_tax_authority_data(user, invoice_id=invoice.id, data=tax_authority_data)
        await self.zatca_repo.update_pih_and_icv(branch_tax_authority_data.branch_id, invoice_request["invoiceHash"])
        return tax_authority_data







    # async def _send_compliance_invoices(self, user: UserInDB, invoicing_type: InvoicingType) -> None:
    #     invoice_types = []
    #     if invoicing_type == InvoicingType.STANDARD:
    #         invoice_types = [InvoiceType.STANDARD]
    #     elif invoicing_type == InvoicingType.SIMPLIFIED:
    #         invoice_types = [InvoiceType.SIMPLIFIED]
    #     else:
    #         invoice_types = [InvoiceType.STANDARD, InvoiceType.SIMPLIFIED]
     
    #     invoice_type_codes = [InvoiceTypeCode.INVOICE, InvoiceTypeCode.CREDIT_NOTE, InvoiceTypeCode.DEBIT_NOTE]
        
    #     items_count, items = await self.item_service.item_repo.get_items(user.organization_id)
    #     if len(items) == 0:
    #         raise NoItemFoundException()
    #     item_id = items[0].id
        
    #     if InvoiceType.STANDARD in invoice_types:
    #         customers_count, customers = await self.customer_service.customer_repo.get_customers(user.organization_id)
    #         if len(customers) == 0:
    #             raise NoCustomerFoundException()
    #         customer_id = customers[0].id
    #     else:
    #         customer_id = None

    #     invoice_data = {
    #         "document_type": "INVOICE",
    #         "invoice_type": None,
    #         "invoice_type_code": None,
    #         "issue_date": "yyyy-mm-dd",
    #         "issue_time": "hh:mm:ss",
    #         "document_currency_code": "SAR",
    #         "actual_delivery_date": None,
    #         "payment_means_code": "10",
    #         "original_invoice_id": None,
    #         "instruction_note": None,
    #         "prices_include_tax": False,
    #         "discount_amount": 0,
    #         "note": None,
    #         "customer_id": None,
    #         "invoice_lines": [
    #             {
    #             "item_id": None,
    #             "item_price": 100,
    #             "price_discount": 0,
    #             "quantity": 1,
    #             "discount_amount": 0,
    #             "classified_tax_category": "S",
    #             "tax_authority_tax_authority_data": None
    #             }
    #         ]
    #     }
    #     for type in invoice_types:
    #         last_invoice = None
    #         for code in invoice_type_codes:
    #             req = invoice_data.copy()
    #             req["invoice_type"] = type
    #             req["invoice_type_code"] = code
    #             req["issue_date"] = datetime.now(KSA_TZ).date().isoformat()
    #             req["issue_time"] = datetime.now(KSA_TZ).time().isoformat(timespec='seconds')
    #             req["customer_id"] = customer_id
    #             req["invoice_lines"][0]["item_id"] = item_id
    #             if type == InvoiceType.STANDARD:
    #                 req["actual_delivery_date"] = datetime.now(KSA_TZ).date().isoformat()
    #             if code != InvoiceTypeCode.INVOICE:
    #                 req["original_invoice_id"] = last_invoice.invoice_number
    #                 req["instruction_note"] = "Correction of invoice"
    #             data = SaleInvoiceCreate.model_validate(req)
    #             try:
    #                 invoice = await self.sale_invoice_service.create_invoice(user, data)
    #                 await self.sign_and_submit_invoice(user, invoice)
    #             except BaseException as e:
    #                 raise CSIDNotIssuedException(detail="Could not create invoice for compliance submission")
    #             if code == InvoiceTypeCode.INVOICE:
    #                 last_invoice = invoice
    #     return None