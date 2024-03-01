from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
from PIL import Image
import cv2
import numpy as np
import re

# Setup Tesseract path
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # Update this path as necessary

def is_checkbox_checked(cnt, thresh):
    x, y, w, h = cv2.boundingRect(cnt)
    aspect_ratio = w / float(h)
    if 0.8 < aspect_ratio < 1.2 and 20.5 < w < 26 and 20.5 < h < 26:
        roi = thresh[y:y+h, x:x+w]
        non_zero_pixels = cv2.countNonZero(roi)
        total_pixels = w * h
        fill_ratio = non_zero_pixels / total_pixels
        return fill_ratio > 0.573  # Adjust as necessary
    return False

def extract_text_near_checkbox(checked_checkboxes, data, margin=50):
    text_near_checkboxes = []
    for (x, y, w, h) in checked_checkboxes:
        x_start = x + w
        y_start = y - margin
        x_end = x_start + 200  # Adjust as necessary
        y_end = y + h + margin

        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 60:  # Confidence threshold
                x_text = int(data['left'][i])
                y_text = int(data['top'][i])
                w_text = int(data['width'][i])
                h_text = int(data['height'][i])

                if (x_start < x_text < x_end) and (y_start < y_text < y_end or y_start < y_text + h_text < y_end):
                    text_near_checkboxes.append(data['text'][i])
    return text_near_checkboxes

def process_faxed_form(pdf_path):
    images = convert_from_path(pdf_path)
    
    for page_num, image in enumerate(images, start=1):
        text = pytesseract.image_to_string(image)
        patterns = {
            'Name': r"Name:\s*(.*)",
            'AHC/WCB#': r"AHC/WCB\s*#:\s*(.*)",
            'Address': r"Address:\s*(.*)",
            'Date of Birth': r"Date of Birth:\s*(.*)",
            'Phone Number': r"Phone:\s*(.*)"
        }
        patient_info = {key: re.search(pattern, text).group(1) if re.search(pattern, text) else 'Not found' for key, pattern in patterns.items()}
        for key, value in patient_info.items():
            print(f"{key}: {value}")

        open_cv_image = np.array(image)
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        checked_checkboxes = []
        for cnt in contours:
            if is_checkbox_checked(cnt, thresh):
                x, y, w, h = cv2.boundingRect(cnt)
                checked_checkboxes.append((x, y, w, h))
                cv2.rectangle(open_cv_image, (x, y), (x+w, y+h), (0, 255, 0), 2)

        data = pytesseract.image_to_data(image, output_type=Output.DICT)
        texts_near_checkboxes = extract_text_near_checkbox(checked_checkboxes, data)
        for text in texts_near_checkboxes:
            print(f"Checkbox Text: {text}")

        result_image_path = f'bin/processed_page_{page_num}.jpg'
        cv2.imwrite(result_image_path, open_cv_image)
        print(f"Processed image with checkboxes outlined saved: {result_image_path}")

pdf_path = 'bin/faxed.pdf'
process_faxed_form(pdf_path)
