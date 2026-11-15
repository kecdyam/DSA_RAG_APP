import sys, zipfile
from pathlib import Path
import chromadb

name = " ".join(sys.argv[1:]).lower()            # part of a file name, e.g. linked
coll = chromadb.PersistentClient(path="chroma_db").list_collections()[0]
data = coll.get(include=["documents", "metadatas"])

# 1) what the index holds for these files
by_file = {}
for doc, meta in zip(data["documents"], data["metadatas"]):
    src = meta.get("source", "?")
    if name in src.lower():
        by_file.setdefault(src, []).append(doc)

for src, docs in by_file.items():
    ocr = sum("Text read from a picture" in d for d in docs)
    print(f"\n{src}: {len(docs)} chunks, {ocr} tagged as read-from-picture, {sum(map(len, docs))} characters")
    for d in docs[:6]:
        print("   ", repr(d[:90]))

# 2) how many pictures the original file really has
for f in Path("DATA").rglob("*"):
    if name not in f.name.lower():
        continue
    if f.suffix.lower() == ".docx":
        n = sum(1 for z in zipfile.ZipFile(f).namelist() if z.startswith("word/media/"))
        print(f"\n{f.name}: {n} pictures inside")
    elif f.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
            pages = PdfReader(str(f)).pages
            n = sum(len(p.images) for p in pages)
            print(f"\n{f.name}: {len(pages)} pages, {n} pictures inside")
        except Exception as e:
            print(f"\n{f.name}: could not count pictures ({e})")
    else:
        print(f"\n{f.name}: plain text file, no OCR needed")