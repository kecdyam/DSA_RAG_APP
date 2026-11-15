# Shows what the retriever returns for each UNLABELLED question, so you know which files to open and read.
# It only helps you look. YOU decide the answer key by reading the notes.
from retriever import retrieve
from eval_set import EVAL

for i, item in enumerate(EVAL):
    if item["source"] is not None:
        continue
    results, best = retrieve(item["q"], k=4)
    print(f"\n[{i}] ({item['kind']}) {item['q'][:110]}")
    print(f"    best similarity {best:.2f}")
    for r in results:
        print(f"      {r['source']} | page {r['page']} | {r['text'][:90]!r}")