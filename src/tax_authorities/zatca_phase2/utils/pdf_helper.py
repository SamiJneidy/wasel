import pikepdf
import subprocess

def embed_xml_in_pdf(input_pdf, xml_file, output_pdf_with_xml):
    """
    Embed XML data into a PDF file.
    """
    try:
        # Open the PDF
        with pikepdf.Pdf.open(input_pdf) as pdf:
            # Add the XML file as an embedded file
            with open(xml_file, "rb") as file:
                xml_data = file.read()
            pdf.attachments["invoice.xml"] = xml_data
            # Save the updated PDF with embedded XML
            pdf.save(output_pdf_with_xml)
        print(f"XML data embedded successfully: {output_pdf_with_xml}")
    except Exception as e:
        print("Error embedding XML data:", e)

def convert_to_pdfa3(input_pdf, output_pdf):
    """
    Convert a PDF to PDF/A-3 using Ghostscript.
    """
    # Define the Ghostscript command
    gs_command = [
        "gswin64c",                # Ghostscript executable
        "-dPDFA=3",          # Specify PDF/A-3 compliance
        "-dBATCH",           # Exit after processing
        "-dNOPAUSE",         # Do not prompt for user input
        "-dNOOUTERSAVE",     # Save only the final result
        "-sDEVICE=pdfwrite", # Use the PDF write device
        f"-sOutputFile={output_pdf}",  # Output file
        "-dPDFACompatibilityPolicy=1", # Ensure strict PDF/A compliance
        input_pdf            # Input PDF file
    ]

    # Run the Ghostscript command
    try:
        subprocess.run(gs_command, check=True)
        print(f"Successfully converted to PDF/A-3: {output_pdf}")
    except subprocess.CalledProcessError as e:
        print("Error during PDF/A-3 conversion:", e)

# Paths for the files
input_pdf_path = "example.pdf"                # Original PDF
xml_file_path = "xmlinvoice.xml"                 # XML file to embed
pdf_with_xml_path = "example_with_xml.pdf"    # PDF with embedded XML
output_pdfa3_path = "example_pdfa3.pdf"       # Final PDF/A-3 file

# Step 1: Embed XML into the PDF
embed_xml_in_pdf(input_pdf_path, xml_file_path, pdf_with_xml_path)

# Step 2: Convert to PDF/A-3
convert_to_pdfa3(pdf_with_xml_path, output_pdfa3_path)
