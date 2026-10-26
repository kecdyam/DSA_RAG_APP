from retriever import retrieve, MIN_SIMILARITY
MIN_KEYWORD = 4.5 # below this, we say "not found in keywords"
while True:
    question = input("\nAsk a question (or type q to quit): ")
    if question.strip().lower() == "q":
        break
    if not question.strip():
        continue

    results, best_sim, best_kw = retrieve(question)
    print(f"(vector: {best_sim:.3f} | keyword: {best_kw:.2f})")

    if best_sim < MIN_SIMILARITY and best_kw < MIN_KEYWORD:
        print("I couldn't find anything about that in your notes.")
        continue

    for r in results:
        page = r["page"] if r["page"] != -1 else "(code file)"
        print("\n=====", r["source"], "| page", page)
        print(r["text"])