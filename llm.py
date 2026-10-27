import ollama

MODEL = "llama3.2:3b"

SYSTEM = (
    "You are a study assistant that answers using ONLY the numbered excerpts "
    "from the student's course notes. "
    "If the excerpts do not contain the answer, reply exactly: "
    "I can't find that in the notes. "
    "If the excerpts answer only part of the question, answer that part and "
    "say clearly what the notes do not cover. "
    "Cite the excerpts you used like [1] or [2]. "
    "Never use outside knowledge. Keep the answer short and clear."
)


def build_prompt(question, results):
    parts = []
    for number, r in enumerate(results, start=1):
        where = f"page {r['page']}" if r["page"] != -1 else "code or document file"
        parts.append(f"[{number}] (source: {r['source']}, {where})\n{r['text']}")
    excerpts = "\n\n".join(parts)
    return f"EXCERPTS:\n{excerpts}\n\nQUESTION: {question}"


def answer_stream(question, results):
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": build_prompt(question, results)},
    ]
    stream = ollama.chat(
        model=MODEL,
        messages=messages,
        stream=True,
        options={"temperature": 0, "num_ctx": 4096},
    )
    for part in stream:
        yield part["message"]["content"]