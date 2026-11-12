import re
import ollama
from llm import MODEL
from artifact import gather, SECTIONS

SYSTEM = (
    "You write study notes. Use ONLY the numbered EXCERPTS. Write at most 3 short bullet points, "
    "one per line, each starting with '- ' and ending with the excerpt number, like [1]. "
    "Do not add any fact that is not in the excerpts. If the excerpts do not cover the section, output exactly: NONE"
)
STOP = set("the a an of to and in is are for on with that this it as by be or from at".split())
ORDER = ["Complexity", "Definition", "How it works"]   # build Complexity first so running-time facts land there

def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 2}

def write_bullets(section, topic, chunks):
    excerpts = "\n\n".join(f"[{i}] {c['text']}" for i, c in enumerate(chunks, 1))
    user = f"SECTION: {section} of a cheat sheet on {topic}\n\nEXCERPTS:\n{excerpts}"
    reply = ollama.chat(model=MODEL,
                        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                        options={"temperature": 0, "num_ctx": 4096})
    return reply["message"]["content"]

def verify(raw, chunks):
    """keep a bullet only if it cites a real excerpt AND its words mostly appear in that excerpt"""
    good = []
    for line in raw.splitlines():
        line = line.strip()
        cites = re.findall(r"\[(\d+)\]", line)
        if not line.startswith(("-", "*", "•")) or not cites:
            continue
        n = int(cites[-1])
        if not 1 <= n <= len(chunks):
            continue
        text = re.sub(r"\[\d+\]", "", line).lstrip("-*• ").strip()
        claim = words(text)
        if claim and len(claim & words(chunks[n - 1]["text"])) / len(claim) >= 0.6:
            good.append((text, n))
    return good

def clean_code(text):
    text = re.sub(r"^Text read from a picture in [^:]*:\s*", "", text.strip())
    return text[:700]

def is_code(text):
    numbered = len(re.findall(r"^\s*\d+\s+[A-Za-z]", text, re.M))   # pseudocode lines like "2 for i = ..."
    return numbered >= 2 or (";" in text and "{" in text)           # or real code such as Java

def build_cheatsheet(topic):
    gathered = gather(topic)
    sources, used, body = [], set(), {}

    def cite(chunk):
        key = (chunk["source"], chunk["page"])
        if key not in sources:
            sources.append(key)
        return sources.index(key) + 1

    for name in ORDER:
        chunks = gathered[name]["chunks"]
        bullets = verify(write_bullets(name, topic, chunks), chunks) if chunks else []
        pattern = SECTIONS[name][1]
        out = []
        for text, n in bullets:
            sig = " ".join(sorted(words(text)))
            if sig in used or (pattern and not re.search(pattern, text, re.I)):
                continue                      # duplicate, or doesn't belong in this section
            used.add(sig)
            out.append(f"- {text} [{cite(chunks[n - 1])}]")
        body[name] = out or ["*Not in your notes.*"]

    code = []                                  # code is copied as-is, never paraphrased by the model
    for c in [c for c in gathered["Code"]["chunks"] if is_code(c["text"])][:2]:
        code += ["```", clean_code(c["text"]), "```",
                 f"[{cite(c)}] copied as-is; text read from images may contain errors", ""]
    body["Code"] = code or ["*Not in your notes.*"]

    if not sources:
          return f"# {topic.title()} - cheat sheet\n\n*Nothing about this topic was found in your notes.*"

    lines = [f"# {topic.title()} - cheat sheet", ""]
    for name in ["Definition", "How it works", "Complexity", "Code"]:
        lines += [f"## {name}"] + body[name] + [""]
    lines.append("## Sources")
    for i, (src, page) in enumerate(sources, 1):
        lines.append(f"{i}. {src} | {'page ' + str(page) if page != -1 else 'code or document file'}")
    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    print(build_cheatsheet(" ".join(sys.argv[1:]) or "merge sort"))