# Rename "metadata" to "data" in tax authorities and sale invoices

## Files to edit:
- [ ] src/tax_authorities/zatca_phase2/services.py: Function names, variable names
- [ ] src/tax_authorities/zatca_phase2/routers.py: Function names
- [ ] src/tax_authorities/zatca_phase2/repositories.py: Method names
- [ ] src/sale_invoices/services.py: Variable names, field names
- [ ] src/sale_invoices/schemas.py: Field names
- [ ] Alembic migration files: Table names

## Key changes:
- Function/method names: compliance_metadata → tax_authority_data
- Variable names: branch_metadata → branch_data, line_metadata → line_data
- Field names: tax_authority_metadata → tax_authority_data
- Table names: zatca_branches_metadata → zatca_branches_data, zatca_sale_invoice_metadata → zatca_sale_invoice_data, zatca_sale_invoice_lines_metadata → zatca_sale_invoice_lines_data
