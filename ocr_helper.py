import os
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
CACHE = "ocr_cache"


def ocr_page(page, filename, page_number):
    os.makedirs(CACHE, exist_ok=True)
    cache_file = os.path.join(CACHE, f"{filename}_p{page_number}.txt")

    # OCR is slow, so reuse a saved result if we have one
    if os.path.exists(cache_file):
        with open(cache_file, encoding="utf-8") as f:
            return f.read()

    pix = page.get_pixmap(dpi=200)   # turn the page into a picture
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    text = pytesseract.image_to_string(image)

    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(text)
    return text