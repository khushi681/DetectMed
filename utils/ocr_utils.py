import cv2
import easyocr
import pytesseract
import numpy as np

reader = easyocr.Reader(['en'])

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    return blur

def extract_text_from_image(image_path):
    img = preprocess_image(image_path)

    # EasyOCR extraction
    easy_text = reader.readtext(img, detail=0)

    # Tesseract extraction
    tess_text = pytesseract.image_to_string(img)

    # Combine and remove duplicates
    all_text = easy_text + tess_text.split("\n")
    cleaned = [t.strip() for t in all_text if t.strip()]

    return cleaned
