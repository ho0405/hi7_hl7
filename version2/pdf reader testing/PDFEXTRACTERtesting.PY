import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

pdf_path = 'faxed.pdf'
pdf_document = fitz.open(pdf_path)
dpi = 300  # Higher DPI for better text extraction

for page_num in range(len(pdf_document)):
    page = pdf_document.load_page(page_num)
    # Get the full pixmap of the page
    full_pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
    full_img_bytes = full_pix.tobytes("png")
    full_img = Image.open(io.BytesIO(full_img_bytes))
    
    # Calculate the dimensions of the top 1/4 of the image
    width, height = full_img.size
    top_quarter = (0, 0, width, height // 4)
    
    # Crop the image to the top quarter
    cropped_img = full_img.crop(top_quarter)
    
    # Perform OCR on the cropped image to analyze the top 1/4 of the page
    ocr_result = pytesseract.image_to_data(cropped_img, output_type=pytesseract.Output.DICT)
    
    # Since we're now focusing on a specific area, you may adjust your method for detecting the check mark
    # For example, looking for any non-text elements or specific symbols known to represent check marks
    # This part of your logic might need to be adapted based on your specific document layout and OCR output
    
    for i, text in enumerate(ocr_result['text']):
        if text.strip():  # This is a simplistic check; you might look for specific patterns or symbols
            # Assuming any non-empty text in this area could be relevant
            print(f"Text found in top quarter on page {page_num + 1}: {text}")

pdf_document.close()
