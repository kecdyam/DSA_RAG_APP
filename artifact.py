import re
from retriever import retrieve, MIN_SIMILARITY

# name: (search template, regex a chunk must match to count as evidence; "" = no check)
SECTIONS = {
    "Definition":   ("what is {t}", ""),
    "How it works": ("how does {t} work steps", ""),
    "Complexity":   ("{t} time complexity", r"o\(|complexity|log\s*n|θ|ω|theta|omega"),
    "Code":         ("{t} pseudocode algorithm program", r"\b(for|while|return|void|int|if)\b|\w+\(\w(,\s*\w+)+\)"),
}

def squash(text):
    """lowercase and drop everything except letters/digits, so 'Merge_Sort' == 'merge sort'"""
    return re.sub(r"[^a-z0-9]", "", text.lower())

def topic_files(topic):
    """files whose NAME contains the topic, e.g. Merge_Sort.docx for 'merge sort'"""
    phrase = squash(topic)
    results, _ = retrieve(f"what is {topic}", k=10)
    return {r["source"] for r in results if phrase in squash(r["source"])}

def about_topic(chunk, topic, files):
    if files:                                   # a file is named after the topic: trust only that file
        return chunk["source"] in files
    return squash(chunk["text"]).count(squash(topic)) >= 2   # otherwise the topic must be mentioned twice

def gather(topic, k=3):
    files = topic_files(topic)
    pool, _ = retrieve(topic, k=20)   # everything near the topic, so other files' code can't crowd it out
    out = {}
    for name, (template, pattern) in SECTIONS.items():
        results, best = retrieve(template.format(t=topic), k=8)
        seen, keep = set(), []
        for r in results + pool:
            if r["text"] in seen:
                continue
            seen.add(r["text"])
            if about_topic(r, topic, files) and (not pattern or re.search(pattern, r["text"], re.I)):
                keep.append(r)
        out[name] = {"chunks": keep[:k] if best >= MIN_SIMILARITY else [], "best": best}
    return out

if __name__ == "__main__":
    import sys
    topic = " ".join(sys.argv[1:]) or "merge sort"
    print("topic files:", topic_files(topic) or "none")
    for name, s in gather(topic).items():
        print(f"\n== {name} (best {s['best']:.2f}) ==")
        if not s["chunks"]:
            print("   NOT IN YOUR NOTES")
        for r in s["chunks"]:
            print("  ", r["source"], r["page"], r["text"][:110].replace("\n", " "))