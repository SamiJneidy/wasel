invoice_data_template = {
  "invoice_type": "0200000", # to be replaced dynamically
  "invoice_type_code": "388", # to be replaced dynamically
  "issue_date": "2025-01-24", # to be replaced dynamically
  "issue_time": "14:30:00", # to be replaced dynamically
  "document_currency_code": "SAR",
  "actual_delivery_date": "2026-01-03", # to be replaced dynamically
  "payment_means_code": "10",
  "discount_amount": "0",
  "note": "Compliance invoice",
  "invoice_number": "SIMINV-26-000001", # to be replaced dynamically
  "line_extension_amount": "10.00",
  "taxable_amount": "10.00",
  "tax_amount": "1.50",
  "tax_inclusive_amount": "11.50",
  "payable_amount": "11.50",
  "uuid": "c339664c-4280-4a6d-afd7-86adb31263e2", # to be replaced dynamically
  "pih": "omfPMF2yqeQeNAjw7wGgyBokfdIjvwSRjTvvbz9HGY0=", # to be replaced dynamically
  "icv": "9", # to be replaced dynamically
  "has_total_discount": False,
  "supplier": { # to be replaced dynamically
    "country_code": "SA",
    "registration_name": "string",
    "vat_number": "399999999900003",
    "address": "string",
    "street": "string",
    "building_number": "2345",
    "division": "string",
    "city": "string",
    "postal_code": "23141",
    "party_identification_scheme": "CRN",
    "party_identification_value": "123124124"
  },
  "customer": {
    "registration_name": "Fatoora Samples LTD",
    "vat_number": "399999999800003",
    "street": "Salah Al-Din",
    "building_number": "1111",
    "division": "Al-Murooj",
    "city": "Riyadh",
    "postal_code": "12222",
    "party_identification_scheme": "CRN",
    "party_identification_value": "1010010000"
  },
  "invoice_lines": [
    {
      "item": {
        "name": "Cola",
        "default_sale_price": "10.15",
        "default_buy_price": "10.15",
        "unit_code": "PCE",
      },
      "id": 1,
      "item_price": "10",
      "quantity": "1",
      "price_discount": "0",
      "discount_amount": "0",
      "line_extension_amount": "10.00",
      "tax_amount": "1.50",
      "tax_rate": "15",
      "classified_tax_category": "S",
      "rounding_amount": "11.50",
      "item_price_before_discount": "10",
      "item_price_after_discount": "10.00"
    }
  ],
  "tax_categories": {
      "S": {
      "taxable_amount": "10.00",
      "tax_amount": "1.50",
      "classified_tax_category": "S",
      "tax_rate": "15",
      "tax_exemption_reason_code": None,
      "tax_exemption_reason": None,
      "used": True
    }
  }
}