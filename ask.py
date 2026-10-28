from retriever import retrieve, MIN_SIMILARITY
from llm import answer_stream

K = 4
REFUSAL = "can't find that in the notes"

while True:
    question = input("\nAsk a question (or type q to quit): ")
    if question.strip().lower() == "q":
        break

    results, best_sim = retrieve(question, k=K)

    if best_sim < MIN_SIMILARITY:
        print("I couldn't find anything about that in your notes.")
        continue

    print("\nAnswer:\n")
    answer = ""
    for piece in answer_stream(question, results):
        answer += piece
        print(piece, end="", flush=True)

    if REFUSAL in answer.lower().replace("\u2019", "'"):
        print()
        continue

    print("\n\nSources:")
    for number, r in enumerate(results, start=1):
        where = f"page {r['page']}" if r["page"] != -1 else "code or document file"
        print(f"  [{number}] {r['source']} | {where}")