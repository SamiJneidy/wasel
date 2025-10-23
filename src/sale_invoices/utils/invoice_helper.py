from src.core.enums import InvoiceType, InvoiceTypeCode
from .xml_generator import xml_generator

class invoice_helper:

    INVOICE_TYPE_PREFIX = {
        InvoiceType.STANDARD: "TAX",
        InvoiceType.SIMPLIFIED: "SIM",
    }

    INVOICE_TYPE_CODE_PREFIX = {
        InvoiceTypeCode.INVOICE: "INV",
        InvoiceTypeCode.CREDIT_NOTE: "CD",
        InvoiceTypeCode.DEBIT_NOTE: "DB",
    }

    @staticmethod
    def format_invoice_number(invoice_type: InvoiceType, invoice_type_code: InvoiceTypeCode, year: int, seq_number: int) -> str:
        """Returns the formatted invoice number in the format: <INVOICE TYPE>-<INVOICE TYPE CODE>-<YEAR>-<SEQUENCE NUMBER>"""
        zumber = str(seq_number).zfill(6)
        two_digit_year = str(year)[2:]
        return f"{invoice_helper.INVOICE_TYPE_PREFIX[invoice_type]}-{invoice_helper.INVOICE_TYPE_CODE_PREFIX[invoice_type_code]}-{two_digit_year}-{zumber}"
    
    @staticmethod
    def sign_and_get_request(invoice_data, private_key, x509_certificate_content) -> dict[str, str]:
        """Signs the invoice and returns the invoice request as a dictionary containing {invoice_hash, uuid, invoice}"""
        return xml_generator.sign_and_get_request(invoice_data, private_key, x509_certificate_content)
    
    @staticmethod
    def extract_base64_qr_code(invoice) -> str | None:
        return xml_generator.extract_base64_qr_code(invoice)