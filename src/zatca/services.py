import json
from fastapi import status
from .schemas import ZatcaCSIDResponse
from src.core.config import settings
from src.core.utils import AsyncRequestService
from .exceptions import ComplianceCSIDNotIssuedException, ZatcaRequestFailedException
from .utils import extract_error_message_from_response


class ZatcaService:
    
    def __init__(self, request_service: AsyncRequestService):
        self.request_service = request_service
        

    async def get_compliance_csid(self, csr_base64: str, otp: str):

        json_payload = {'csr': csr_base64}
        
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
        
        response_json: dict = response.json()

        if response.status_code != status.HTTP_200_OK:
            raise ComplianceCSIDNotIssuedException(
                detail=extract_error_message_from_response(response_json),
                status_code=response.status_code,
                zatca_response=response_json
            )

        return ZatcaCSIDResponse(
            request_id=response_json.get("requestID"),
            disposition_message=response_json.get("dispositionMessage"),
            binary_security_token=response_json.get("binarySecurityToken"),
            secret=response_json.get("secret")
        )


    # @staticmethod
    # def production_csid(cert_info, retries=3, backoff_factor=1):
    #     request_id = cert_info['ccsid_requestID']
    #     id_token = cert_info['ccsid_binarySecurityToken']
    #     secret = cert_info['ccsid_secret']
    #     url = cert_info['productionCsidUrl']

    #     json_payload = json.dumps({'compliance_request_id': request_id})

    #     headers = {
    #         'accept': 'application/json',
    #         'accept-language': 'en',
    #         'Accept-Version': 'V2',
    #         'Content-Type': 'application/json',
    #     }

    #     auth = HTTPBasicAuth(id_token, secret)
    #     return api_helper.post_request_with_retries(url, headers, json_payload, auth=auth, retries=retries, backoff_factor=backoff_factor)

    # @staticmethod
    # def compliance_checks(cert_info, json_payload, retries=3, backoff_factor=1):
    #     id_token = cert_info['ccsid_binarySecurityToken']
    #     secret = cert_info['ccsid_secret']
    #     url = cert_info["complianceChecksUrl"]

    #     headers = {
    #         'accept': 'application/json',
    #         'accept-language': 'en',
    #         'Accept-Version': 'V2',
    #         'Content-Type': 'application/json',
    #     }

    #     auth = HTTPBasicAuth(id_token, secret)
    #     return api_helper.post_request_with_retries(url, headers, json_payload, auth=auth, retries=retries, backoff_factor=backoff_factor)

    # @staticmethod
    # def invoice_reporting(cert_info, json_payload, retries=3, backoff_factor=1):
    #     id_token = cert_info['pcsid_binarySecurityToken']
    #     secret = cert_info['pcsid_secret']
    #     url = cert_info["reportingUrl"]

    #     headers = {
    #         'accept': 'application/json',
    #         'accept-language': 'en',
    #         'Accept-Version': 'V2',
    #         'Content-Type': 'application/json',
    #     }

    #     auth = HTTPBasicAuth(id_token, secret)
    #     return api_helper.post_request_with_retries(url, headers, json_payload, auth=auth, retries=retries, backoff_factor=backoff_factor)

    # @staticmethod
    # def invoice_clearance(cert_info, json_payload, retries=3, backoff_factor=1):
    #     id_token = cert_info['pcsid_binarySecurityToken']
    #     secret = cert_info['pcsid_secret']
    #     url = cert_info["clearanceUrl"]

    #     headers = {
    #         'accept': 'application/json',
    #         'accept-language': 'en',
    #         'Clearance-Status': '1',
    #         'Accept-Version': 'V2',
    #         'Content-Type': 'application/json',
    #     }

    #     auth = HTTPBasicAuth(id_token, secret)
    #     return api_helper.post_request_with_retries(url, headers, json_payload, auth=auth, retries=retries, backoff_factor=backoff_factor)

    # @staticmethod
    # def load_json_from_file(file_path):
    #     try:
    #         with open(file_path, 'r') as file:
    #             return json.load(file)
    #     except FileNotFoundError:
    #         raise Exception(f"File not found: {file_path}")
    #     except json.JSONDecodeError as e:
    #         raise Exception(f"Error parsing JSON: {str(e)}")

    # @staticmethod
    # def save_json_to_file(file_path, data):
    #     try:
    #         with open(file_path, 'w') as file:
    #             json.dump(data, file, indent=4, ensure_ascii=False, separators=(',', ': '))
    #     except Exception as e:
    #         raise Exception(f"Error saving JSON: {str(e)}")

    # @staticmethod
    # def clean_up_json(api_response, request_type, api_url):
    #     array_response = json.loads(api_response)
    #     array_response['requestType'] = request_type
    #     array_response['apiUrl'] = api_url

    #     array_response = {k: v for k, v in array_response.items() if v is not None}

    #     reordered_response = {
    #         'requestType': array_response.pop('requestType'),
    #         'apiUrl': array_response.pop('apiUrl'),
    #         **array_response
    #     }

    #     return json.dumps(reordered_response, indent=4, ensure_ascii=False, separators=(',', ': '))
