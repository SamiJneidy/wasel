from src.core.enums import DocumentType, InvoiceType, InvoiceTypeCode
from .xml_generator import xml_generator

class invoice_helper:

    PREFIX = {
        DocumentType.INVOICE: {
            InvoiceTypeCode.INVOICE: {InvoiceType.STANDARD: "TAXINV", InvoiceType.SIMPLIFIED: "SIMINV"},
            InvoiceTypeCode.CREDIT_NOTE: {InvoiceType.STANDARD: "TAXCD", InvoiceType.SIMPLIFIED: "SIMCD"},
            InvoiceTypeCode.DEBIT_NOTE: {InvoiceType.STANDARD: "TAXDB", InvoiceType.SIMPLIFIED: "SIMDB"},  
        },
        DocumentType.QUOTATION: {
            InvoiceTypeCode.INVOICE: {InvoiceType.STANDARD: "QT", InvoiceType.SIMPLIFIED: "QT"},
            InvoiceTypeCode.CREDIT_NOTE: {InvoiceType.STANDARD: "QT", InvoiceType.SIMPLIFIED: "QT"},
            InvoiceTypeCode.DEBIT_NOTE: {InvoiceType.STANDARD: "QT", InvoiceType.SIMPLIFIED: "QT"},  
        }
    }  

    @staticmethod
    def extract_error_message_from_response(response: dict | None) -> str | None:
        try:
            errors_list: list = response.get("errors")
            error: dict = errors_list[0]
            message: str = error.get("message")
            return message
        except Exception as e:
            return None
        
    @staticmethod
    def format_invoice_number(document_type: DocumentType, invoice_type: InvoiceType, invoice_type_code: InvoiceTypeCode, year: int, seq_number: int) -> str:
        """Returns the formatted invoice number"""
        zumber = str(seq_number).zfill(6)
        two_digit_year = str(year)[2:]
        prefix = invoice_helper.PREFIX[document_type][invoice_type_code][invoice_type]
        return f"{prefix}-{two_digit_year}-{zumber}"
    
    @staticmethod
    def sign_and_get_request(invoice_data, private_key, x509_certificate_content) -> dict[str, str]:
        """Signs the invoice and returns the invoice request as a dictionary containing {invoice_hash, uuid, invoice}"""
        return xml_generator.sign_and_get_request(invoice_data, private_key, x509_certificate_content)
    
    @staticmethod
    def extract_base64_qr_code(invoice) -> str | None:
        return xml_generator.extract_base64_qr_code(invoice)