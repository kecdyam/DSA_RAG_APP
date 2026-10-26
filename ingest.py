import os
import pymupdf

root = "DATA"

pdf_count = 0
java_count = 0

for folder, subfolders, files in os.walk(root):
    for filename in files:
        path = os.path.join(folder, filename)

        if filename.lower().endswith(".pdf"):
            doc = pymupdf.open(path)
            print("PDF :", filename, "->", len(doc), "pages")
            doc.close()
            pdf_count += 1

        elif filename.lower().endswith(".java"):
            with open(path, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            print("JAVA:", filename, "->", len(lines), "lines")
            java_count += 1

print("Total PDFs:", pdf_count)
print("Total Java files:", java_count)