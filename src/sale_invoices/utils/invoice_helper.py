import base64
from lxml import etree 
import uuid
import json
import xml.dom.minidom as minidom
import os
from pathlib import Path
from .einvoice_signer import einvoice_signer


current_dir = os.path.dirname(os.path.abspath(__file__))

class invoice_helper:
    
    namespaces = {
        'ext': "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        'ds': "http://www.w3.org/2000/09/xmldsig#",
        'cbc': "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        'cac': "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    }


    @staticmethod
    def sign_and_get_request(invoice_data, private_key, x509_certificate_content) -> dict[str, str]:
        """Signs the invoice and returns the invoice request as a dictionary containing {invoice_hash, uuid, invoice}"""
        xml_string = invoice_helper.generate_xml_invoice(invoice_data)
        base_document = etree.fromstring(xml_string)
        # Sign the invoice, and return the invoice request {invoice_hash, uuid, invoice} 
        invoice_request_json = einvoice_signer.get_request_api(base_document, x509_certificate_content, private_key)
        invoice_request_dict: dict = json.loads(invoice_request_json)
        return invoice_request_dict
        

    @staticmethod
    def is_parent_in_xml_tree(parent, child):   
        """"Check if one the parent tag is on the path from root to child"""
        while child is not None:
            if parent in child.tag:
                return True
            child = child.getparent()
        return False


    @staticmethod
    def set_tag_value(root, tag, value):   
        element = root.xpath(f'.//*{{tag}}', namespaces=invoice_helper.namespaces)
        if element is not None:
            element.text = value


    @staticmethod
    def insert_tag_after(root, tag, target):
        """Insert a tag after a target tag"""
        parent = target.getparent()
        index = parent.index(target)
        parent.insert(index + 1, tag)


    @staticmethod
    def insert_tag_inside(root, tag, target):
        """Insert a tag inside a target tag"""
        parent = root.xpath(target, namespaces=invoice_helper.namespaces)[0]
        parent.append(tag)


    @staticmethod
    def clear_empty_tags(node):
        # If a tag has cbc namespace, then it contains data
        if node.tag.startswith(f'{{{invoice_helper.namespaces['cbc']}}}'):
            if node.text is None or node.text[:2] == '{{' or node.text.strip() == "":
                node.getparent().remove(node)
            return
        # If a tag has cac namespace, then it may have child tags
        for child in node:
            invoice_helper.clear_empty_tags(child)
        
        # Don't remove customer party even it was empty because it is required for allowance and other tags
        if node.tag == f'{{{invoice_helper.namespaces['cac']}}}AccountingCustomerParty':
            return

        # If the tag doesn't have child tags, then remove it, the second condition in the if statement is not necessary
        if len(node) == 0 and (node.text is None or node.text.strip() == ""):
            node.getparent().remove(node)


    @staticmethod
    def add_supplier_or_customer(root, data: dict, type: str):
        
        # Read supplier/customer info xml template file
        info_xml_root = etree.parse(os.path.abspath(os.path.join(current_dir, "templates", "supplier_customer.xml"))).getroot()

        # Set PartyIdentification
        element = info_xml_root.xpath(".//*[text()='{{party_identification_value}}']", namespaces=invoice_helper.namespaces)[0]
        element.set("schemeID", data["party_identification_scheme"])

        # Update supplier/customer info
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"  # e.g., "{{IssueDate}}"
            elements = info_xml_root.xpath(f".//*[text()='{placeholder}']", namespaces=invoice_helper.namespaces)
            for elem in elements:
                elem.text = value  # Replace with the value from the JSON

        # Add the supplier/customer info into the AccountingSupplierParty/AccountingCustomerParty tag
        if type == "supplier":
            target = './/cac:AccountingSupplierParty'
        else:
            target = './/cac:AccountingCustomerParty'
        
        invoice_helper.insert_tag_inside(root, info_xml_root, target)


    @staticmethod
    def add_invoice_line(invoice_line, root):
        
        # Read invoice line xml template file
        invoice_line_root = etree.parse(os.path.abspath(os.path.join(current_dir, "templates", "invoice_line.xml"))).getroot()
        
        # Add invoiced quantity
        element = invoice_line_root.xpath(".//*[text()='{{quantity}}']", namespaces=invoice_helper.namespaces)[0]
        element.set("unitCode", invoice_line["item"]["unit_code"])
        element.text = invoice_line["quantity"]

        # Add item name
        element = invoice_line_root.xpath(".//*[text()='{{item_name}}']", namespaces=invoice_helper.namespaces)[0]
        element.text = invoice_line["item"]["name"]

        # Add item price before discount
        element = invoice_line_root.xpath(".//*[text()='{{item_price_before_discount}}']", namespaces=invoice_helper.namespaces)[0]
        element.text = invoice_line["item_price_before_discount"]

        # Replace placeholders with actual invoice line values
        for key, value in invoice_line.items():
            placeholder = f"{{{{{key}}}}}"  # e.g., "{{IssueDate}}"
            elements = invoice_line_root.xpath(f".//*[text()='{placeholder}']", namespaces=invoice_helper.namespaces)
            for elem in elements:
                elem.text = value  # Replace with the value from the JSON

        # Append invoice line to the invoice
        root.append(invoice_line_root)

    @staticmethod
    def add_tax_subtotals(root, invoice_data: dict):
        """Add the tax subtotals template for each tax category in the second TaxTotal element"""

        tax_categories = invoice_data["tax_categories"]
        tax_total_element = root.xpath('.//cac:TaxTotal', namespaces=invoice_helper.namespaces)[1]
        
        for cat, vals in tax_categories.items():
            tax_subtotal_xml_template = etree.parse(os.path.abspath(os.path.join(current_dir, "templates", "tax_subtotal.xml"))).getroot()
            for key, value in vals.items():
                placeholder = f"{{{{{key}}}}}"  # e.g., "{{IssueDate}}"
                elements = tax_subtotal_xml_template.xpath(f".//*[text()='{placeholder}']", namespaces=invoice_helper.namespaces)
                for elem in elements:
                    elem.text = value  # Replace with the value from the JSON
            tax_total_element.append(tax_subtotal_xml_template)

    @staticmethod
    def add_allowance_charge(root, invoice_data: dict):
        """Add details about tax categories in the AllowanceCharge element"""

        allowance_xml_root = root.xpath('.//cac:AllowanceCharge', namespaces=invoice_helper.namespaces)[0]
        tax_categories = invoice_data["tax_categories"]
        
        if invoice_data["has_total_discount"] == True:
            for cat, vals in tax_categories.items():
                for key, value in vals.items():
                    placeholder = f"{{{{{key}}}}}"  # e.g., "{{IssueDate}}"
                    elements = allowance_xml_root.xpath(f".//*[text()='{placeholder}']", namespaces=invoice_helper.namespaces)
                    for elem in elements:
                        elem.text = value  # Replace with the value from the JSON
        else:
            root.remove(allowance_xml_root)
        
    @staticmethod
    def generate_xml_invoice(invoice_data: dict):
        """Generates the base xml invoice ready to be signed"""

        xml_template = etree.parse(os.path.abspath(os.path.join(current_dir, "templates", "invoice.xml")))
        root = xml_template.getroot()
        # Change name attribute of InvoiceTypeCode tag
        invoice_type_code = root.xpath(".//*[text()='{{invoice_type_code}}']", namespaces=invoice_helper.namespaces)[0]
        invoice_type_code.set('name', invoice_data['invoice_type'])
        invoice_helper.add_supplier_or_customer(root, invoice_data["supplier"], "supplier")
        if "customer" in invoice_data:
            invoice_helper.add_supplier_or_customer(root, invoice_data["customer"], "customer")
        for line in invoice_data["invoice_lines"]:
            invoice_helper.add_invoice_line(line, root)
        invoice_helper.add_tax_subtotals(root, invoice_data)
        invoice_helper.add_allowance_charge(root, invoice_data)
        # Update general invoice data
        for key, value in invoice_data.items():
            placeholder = f"{{{{{key}}}}}"  # e.g., "{{IssueDate}}"
            elements = root.xpath(f".//*[text()='{placeholder}']", namespaces=invoice_helper.namespaces)
            for elem in elements:
                elem.text = value  # Replace with the value from the JSON
        # Update all attributes named "currencyID"
        for elem in root.iter():  # Iterate through all elements in the XML tree
            if 'currencyID' in elem.attrib:
                elem.attrib['currencyID'] = invoice_data["document_currency_code"]
        # Clear empty tags that were not given in the json data
        invoice_helper.clear_empty_tags(root)
        # Transform the XML to a string, remove all \n, \t and tabs (4 consecutive spaces) then use toprettyxml() to re-indent the resulting XML string
        xml_str = etree.tostring(xml_template, encoding="UTF-8")
        xml_str = xml_str.replace(b'\n', b'').replace(b'\t', b'').replace(b'    ', b'')
        pretty_xml = minidom.parseString(xml_str).toprettyxml().rstrip()
        return pretty_xml


    @staticmethod
    def extract_invoice_hash(xml_input) -> str:
        if isinstance(xml_input, str):
            decoded_xml = base64.b64decode(xml_input)
            if decoded_xml is None:
                raise ValueError("Invalid Base64 string provided.")
            xml_input = decoded_xml
        elif not isinstance(xml_input, (bytes, etree._Element)):
            raise ValueError("Input must be a string or lxml.etree._Element.")
        # Load XML into an lxml Element
        if isinstance(xml_input, bytes):
            doc = etree.fromstring(xml_input)
        else:
            doc = xml_input  # Assume it's already an lxml Element
        # Extract invoiceHash
        invoice_hash_node = doc.xpath("//ds:Reference[@Id='invoiceSignedData']/ds:DigestValue", namespaces=invoice_helper.namespaces)
        invoice_hash = invoice_hash_node[0].text if invoice_hash_node else None
        return invoice_hash
    
    
    @staticmethod
    def extract_base64_qr_code(invoice) -> str | None:
        if isinstance(invoice, str):
            decoded_xml = base64.b64decode(invoice)
            if decoded_xml is None:
                raise ValueError("Invalid Base64 string provided.")
            invoice = decoded_xml
        elif not isinstance(invoice, (bytes, etree._Element)):
            return None
            # raise ValueError("Input must be a string or lxml.etree._Element.")
        # Load XML into an lxml Element
        if isinstance(invoice, bytes):
            doc = etree.fromstring(invoice)
        else:
            doc = invoice  # Assume it's already an lxml Element
        # Extract base64QRCode
        base64_qr_code_node = doc.xpath("//cac:AdditionalDocumentReference[cbc:ID='QR']/cac:Attachment/cbc:EmbeddedDocumentBinaryObject", namespaces=invoice_helper.namespaces)
        base64_qr_code = base64_qr_code_node[0].text if base64_qr_code_node else None
        return base64_qr_code


    @staticmethod
    def is_simplified_invoice(xml):
        namespace = {'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'}
        invoice_type_code_node = xml.find('.//cbc:InvoiceTypeCode', namespaces=namespace)
        if invoice_type_code_node is not None:
            name_attribute = invoice_type_code_node.get('name')
            return name_attribute.startswith('02')
        return False


    @staticmethod
    def get_invoice_filename(invoice_data):

        supplier_vat_number = invoice_data["SellerInfo"]["CompanyID"].strip()
        issue_date = invoice_data["IssueDate"].strip().replace('-', '')
        issue_time = invoice_data["IssueTime"].strip().replace(':', '')
        invoice_number = invoice_data["ID"].strip()
        
        # Replace all non-alphanumeric characters in the invoice number by a dash '-'
        invoice_number_list = list(invoice_number)
        for i, c in enumerate(invoice_number_list):
            if not c.isalnum():
                invoice_number_list[i] = '-'

        invoice_number = "".join(invoice_number_list)

        filename = supplier_vat_number + "_" + issue_date + "T" + issue_time + "_" + invoice_number
        return filename
    