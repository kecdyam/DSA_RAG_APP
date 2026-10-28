import ollama

MODEL = "llama3.2:3b"

SYSTEM = (
    "You are a careful study assistant. Answer the QUESTION using ONLY the "
    "EXCERPTS from the student's course notes.\n"
    "Rules:\n"
    "1. Some excerpts may be about other topics. Ignore any excerpt that does "
    "not directly help answer the question.\n"
    "2. Write ONE combined answer in your own words. Do not copy the excerpt "
    "headers and do not repeat the excerpts one by one.\n"
    "3. Cite the excerpts you used like [1] or [2] at the end of the sentence "
    "that uses them.\n"
    "4. Do not add facts, reasons or examples that are not written in the "
    "excerpts, even if you know them.\n"
    "5. If the excerpts do not contain the answer, reply exactly: "
    "I can't find that in the notes.\n"
    "6. If the excerpts answer only part of the question, answer that part, "
    "then write: The notes do not cover: followed by the missing part.\n"
    "Keep the answer short."
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