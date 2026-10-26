import os
import pymupdf

for folder, subfolders, files in os.walk("DATA"):
    for filename in files:
        if filename.lower().endswith(".pdf"):
            doc = pymupdf.open(os.path.join(folder, filename))
            low = []
            for number, page in enumerate(doc, start=1):
                text = page.get_text().strip()
                if len(text) < 50:
                    low.append((number, len(text), len(page.get_images())))
            doc.close()
            if low:
                print(filename, "-> (page, characters, images):", low)