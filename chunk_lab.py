import os
import sys
import pymupdf


def split_text(text, size, overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


name = sys.argv[1]
number = int(sys.argv[2])

for folder, subfolders, files in os.walk("DATA"):
    if name in files:
        doc = pymupdf.open(os.path.join(folder, name))
        text = doc[number - 1].get_text()
        print("Page has", len(text), "characters")

        for size in (200, 1000, 5000):
            overlap = min(150, size // 5)
            chunks = split_text(text, size, overlap)
            print("\n" + "=" * 60)
            print(f"size={size}, overlap={overlap} -> {len(chunks)} chunks")
            for i, c in enumerate(chunks[:3], start=1):
                print(f"  chunk {i} starts: {c[:60]!r}")
                print(f"  chunk {i} ends:   {c[-60:]!r}")