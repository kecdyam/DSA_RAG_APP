import sys, time
from eval_set import EVAL, OUT_OF_SCOPE
import retriever as R
from llm import answer_stream
from grounded import extract_quotes

REFUSAL = "can't find that in the notes"
GATE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.70      # python -u strict_eval.py 0.70 20
LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 10**6      # how many in-scope questions to test
items = [e for e in EVAL if e["source"]]
step = max(1, len(items) // min(LIMIT, len(items)))
items = items[::step][:LIMIT]                                 # an even sample, not just the first ones

def judge(q):
    results, best = R.retrieve(q, k=4)
    if best < GATE:
        return {"gate": True, "model": False, "quotes": False}
    answer = "".join(answer_stream(q, results))
    model = REFUSAL in answer.lower().replace("\u2019", "'")
    quotes = len(extract_quotes(q, results)) == 0              # True = no verified quote found
    return {"gate": False, "model": model, "quotes": quotes}

def label(r):
    return "GATE" if r["gate"] else "MODEL" if r["model"] else "QUOTES" if r["quotes"] else "ANSWERED"

def run(name, questions):
    rows = []
    for i, q in enumerate(questions, 1):
        t = time.time()
        r = judge(q)
        rows.append(r)
        print(f"{name} {i}/{len(questions)} {label(r):<9}{time.time() - t:>5.0f}s  {q[:60]}", flush=True)
    return rows

def summarize(name, rows):
    n = len(rows)
    g = sum(r["gate"] for r in rows)
    m = sum(r["gate"] or r["model"] for r in rows)
    s = sum(r["gate"] or r["quotes"] for r in rows)
    b = sum(r["gate"] or r["model"] or r["quotes"] for r in rows)
    print(f"{name:<22} gate {g}/{n} | +model {m}/{n} | +quote check {s}/{n} | +both {b}/{n}", flush=True)

print(f"gate = {GATE}, {len(items)} in-scope questions, {len(OUT_OF_SCOPE)} out-of-scope", flush=True)
out_rows = run("out", OUT_OF_SCOPE)
in_rows = run("in ", [e["q"] for e in items])
print()
summarize("out-of-scope refused", out_rows)    # higher is better
summarize("in-scope refused", in_rows)         # lower is better