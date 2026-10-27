from retriever import retrieve, MIN_SIMILARITY
from llm import answer_stream

while True:
    question = input("\nAsk a question (or type q to quit): ")
    if question.strip().lower() == "q":
        break

    results, best_sim = retrieve(question, k=5)

    if best_sim < MIN_SIMILARITY:
        print("I couldn't find anything about that in your notes.")
        continue

    print("\nAnswer:\n")
    for piece in answer_stream(question, results):
        print(piece, end="", flush=True)

    print("\n\nSources:")
    for number, r in enumerate(results, start=1):
        where = f"page {r['page']}" if r["page"] != -1 else "code or document file"
        print(f"  [{number}] {r['source']} | {where}")