import re
import unicodedata
import ollama
from llm import MODEL, build_prompt

EXTRACT_SYSTEM = (
    "You extract evidence from course notes. Copy sentences EXACTLY, word for "
    "word, from the numbered EXCERPTS that directly help answer the QUESTION. "
    "Output one quote per line in this format: QUOTE [number]: exact text. "
    "Copy at most 4 quotes. Do not explain, summarize or add anything else. "
    "If no excerpt directly helps answer the question, output exactly: NONE"
)


def norm(text):
    text = unicodedata.normalize("NFKC", text)
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"')):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_quotes(question, results):
    messages = [
        {"role": "system", "content": EXTRACT_SYSTEM},
        {"role": "user", "content": build_prompt(question, results)},
    ]
    reply = ollama.chat(model=MODEL, messages=messages,
                        options={"temperature": 0, "num_ctx": 4096})
    text = reply["message"]["content"]

    normalized = [norm(r["text"]) for r in results]
    found = []
    seen = set()
    for line in text.splitlines():
        m = re.match(r"\s*QUOTE\s*\[?\d*\]?\s*:\s*(.+)", line, re.IGNORECASE)
        if not m:
            continue
        quote = m.group(1).strip().strip('"').strip()
        q = norm(quote)
        if len(q) < 25 or q in seen:
            continue
        for r, n in zip(results, normalized):
            if q in n:                      # the quote really exists in this chunk
                found.append({"quote": quote, "source": r["source"], "page": r["page"]})
                seen.add(q)
                break
    return found