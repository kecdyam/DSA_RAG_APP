import os
import pymupdf

root = "DATA"

for folder, subfolders, files in os.walk(root):
    for filename in files:
        if filename.lower().endswith(".pdf"):
            path = os.path.join(folder, filename)
            doc = pymupdf.open(path)

            total_chars = 0
            for page in doc:
                total_chars += len(page.get_text())

            avg = total_chars // len(doc)
            print(filename, "| pages:", len(doc), "| avg characters per page:", avg)
            doc.close()