import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

print(pytesseract.get_tesseract_version())

from signature_utils import extract_text_from_image

print(extract_text_from_image("../signatures_to_test/test_mark_stevens.png"))
print(extract_text_from_image("../signatures_to_test/test_eric_miller.png"))

