from pathlib import Path
from pypdf import PdfReader

for name in ["Binary_Tree_and_Binary_Search_Tree.pdf", "LinkedList.pdf", "Merge_Sort.pdf", "Queue.pdf"]:
    f = next(Path("DATA").rglob(name), None)
    if not f:
        print(name, "not found")
        continue
    try:
        pages = PdfReader(str(f)).pages
        chars = [len(p.extract_text() or "") for p in pages]
        pics = sum(len(p.images) for p in pages)
        print(f"{name}: {len(pages)} pages, text characters per page {chars}, pictures {pics}")
    except Exception as e:
        print(f"{name}: cannot read ({e})")