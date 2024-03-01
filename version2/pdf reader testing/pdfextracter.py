import fitz  # PyMuPDF
import pytesseract
import re
from PIL import Image
import io

# Path to the PDF document
pdf_path = 'faxed.pdf'

# Open the PDF file
pdf_document = fitz.open(pdf_path)

# Define the desired DPI (increase this value if needed)
dpi = 300  # Use a higher DPI for the postal code extraction

# Loop through each page in the PDF document
for page_num in range(len(pdf_document)):
    page = pdf_document.load_page(page_num)
    
    # Render the page to an image with the specified DPI for general OCR
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
    img_path = f'page_{page_num + 1}.png'
    pix.save(img_path)
    
    # Perform OCR on the image for general information extraction
    extracted_text = pytesseract.image_to_string(img_path)
    
    # Attempt to extract all information including the postal code
    match = re.search(r'Name\s*:?(\s+([^:]*?)\s+AHC/WCB\s*#\s*:\s*([\w-]+))\s*Address\s*:\s*([^:]+)\s*City\s*:\s*([^:]+)\s*Province\s*:\s*([^:]+)\s*Postal\s*Code\s*:\s*([^\s]+)', extracted_text, re.IGNORECASE)
    if match:
        # Extract general information
        name, ahc_wcb_number, address, city, province = match.group(2, 3, 4, 5, 6)
        postal_code = match.group(7)  # Initial attempt to capture the postal code
        
        # Check if the postal code format is incorrect or missing and attempt to extract it from the top right quadrant
        if not re.match(r'[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d', postal_code):
            # Increase DPI and focus on the top right quadrant for postal code extraction
            top_right_quadrant = fitz.Rect(page.rect.width / 2, 0, page.rect.width, page.rect.height / 2)
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi * 2 / 72, dpi * 2 / 72), clip=top_right_quadrant)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            postal_code_text = pytesseract.image_to_string(img)
            postal_code_match = re.search(r'Postal Code:\s*([A-Za-z]\d[A-Za-z] \d[A-Za-z]\d)', postal_code_text)
            if postal_code_match:
                postal_code = postal_code_match.group(1)  # Update the postal code with the correctly extracted one
        
        # Output extracted information
        print(f"Page {page_num + 1}:")
        print(f"Name: {name}")
        print(f"AHC/WCB Number: {ahc_wcb_number}")
        print(f"Address: {address}")
        print(f"City: {city}")
        print(f"Province: {province}")
        print(f"Postal Code: {postal_code}\n")  # '\n' for an extra line break between pages
    else:
        print(f"No match found on page {page_num + 1}\n")  # '\n' for spacing between pages

# Close the PDF document
pdf_document.close()
