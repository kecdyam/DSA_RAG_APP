import os
import sys
import pymupdf
from ocr_helper import ocr_page

name = sys.argv[1]
number = int(sys.argv[2])

for folder, subfolders, files in os.walk("DATA"):
    if name in files:
        doc = pymupdf.open(os.path.join(folder, name))
        print(ocr_page(doc[number - 1], name, number))