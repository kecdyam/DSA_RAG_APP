import io
import os
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
CACHE = "ocr_cache"


def _read_cache(cache_name):
    path = os.path.join(CACHE, cache_name + ".txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    return None


def _write_cache(cache_name, text):
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, cache_name + ".txt"), "w", encoding="utf-8") as f:
        f.write(text)


def ocr_page(page, filename, page_number):
    name = f"{filename}_p{page_number}"
    cached = _read_cache(name)
    if cached is not None:
        return cached
    pix = page.get_pixmap(dpi=200)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    text = pytesseract.image_to_string(image)
    _write_cache(name, text)
    return text


def ocr_image_bytes(data, cache_name):
    cached = _read_cache(cache_name)
    if cached is not None:
        return cached
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
        text = pytesseract.image_to_string(image)
    except Exception:
        text = ""
    _write_cache(cache_name, text)
    return text