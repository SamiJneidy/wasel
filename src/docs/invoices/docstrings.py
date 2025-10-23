DOCSTRINGS = {
    "create_invoice": """Create a new invoice with comprehensive validation and processing. 

This endpoint handles three different invoice creation flows based on the user's current stage and requested invoice type:

- **Compliance Stage**: Creates a compliance invoice that is signed and submitted to ZATCA for testing/validation purposes
- **Production Stage - Standard**: Creates a standard invoice using production CSID, signs it, and submits to ZATCA for clearance
- **Production Stage - Simplified**: Creates a simplified invoice using production CSID, signs it, and submits to ZATCA for reporting

The process includes calculating invoices totals, signing with appropriate CSID certificates, and submitting to ZATCA. All invoices are stored with their ZATCA responses, QR codes, and signatures.""",

    "get_invoice": """Retrieve a complete invoice by its unique identifier.
    
This endpoint returns the full invoice details including:
- Invoice header information (dates, totals, tax calculations, ZATCA status)
- All invoice line items with individual pricing, quantities, and tax amounts
- Customer snapshot data as it existed when the invoice was created
- ZATCA response details, invoice hash, and signed XML content
- Generated QR code for the invoice

The invoice data is retrieved from the current user's account, ensuring proper access control.""",

    "generate_invoice_number": """Generate and return a new invoice number.

This function creates a unique invoice number that is displayed to the user when a new invoice is being created."""
} 