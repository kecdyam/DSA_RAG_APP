# Shows every picture inside Merge_Sort.pdf: its size, and what OCR reads from it.
import re
from pathlib import Path
import pymupdf
from ocr_helper import ocr_image_bytes

doc = pymupdf.open(next(Path("DATA").rglob("Merge_Sort.pdf")))
for pno, page in enumerate(doc, 1):
    for img in page.get_images(full=True):
        info = doc.extract_image(img[0])
        text = ocr_image_bytes(info["image"], f"peek_{pno}_{img[0]}")
        words = re.findall(r"[A-Za-z]{4,}", text)
        print(f"page {pno} xref {img[0]}: {info['width']}x{info['height']}, {len(words)} words | {text[:70]!r}")