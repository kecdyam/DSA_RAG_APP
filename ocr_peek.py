import re
from pathlib import Path
import pymupdf
from ocr_helper import ocr_page

FILES = {"Binary_Tree_and_Binary_Search_Tree.pdf": [1, 5], "LinkedList.pdf": [1, 8], "Queue.pdf": [1, 3]}

for name, pages in FILES.items():
    doc = pymupdf.open(next(Path("DATA").rglob(name)))
    for p in pages:
        text = ocr_page(doc[p - 1], name, p)          # result is cached in ocr_cache
        words = re.findall(r"[A-Za-z]{3,}", text)
        print(f"\n== {name} page {p}: {len(words)} real words ==")
        print(text[:500])