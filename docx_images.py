import io
import os
import sys
import zipfile
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

name = sys.argv[1]
for folder, subfolders, files in os.walk("DATA"):
    if name in files:
        z = zipfile.ZipFile(os.path.join(folder, name))
        images = [n for n in z.namelist() if n.startswith("word/media/")]
        print("Images inside", name, ":", len(images))
        for n in images:
            print("=====", n)
            try:
                img = Image.open(io.BytesIO(z.read(n)))
                print(pytesseract.image_to_string(img)[:500])
            except Exception as e:
                print("could not read:", e)