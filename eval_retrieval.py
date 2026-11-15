# Compares four retrieval methods on the same questions, and measures the "not in your notes" gate.
import time
from collections import defaultdict
from eval_set import EVAL, OUT_OF_SCOPE
import retriever as R          # loads the same model, index and BM25 your app uses

def vec_ids(q, n):
    q_vec = R.model.encode(R.PREFIX + q, normalize_embeddings=True).tolist()
    return R.collection.query(query_embeddings=[q_vec], n_results=n)["ids"][0]

def kw_ids(q, n):
    scores = R.bm25.get_scores(R.tokenize(q))
    top = sorted(range(len(R.docs)), key=lambda i: scores[i], reverse=True)[:n]
    return [R.ids[i] for i in top if scores[i] > 0]

def as_chunks(id_list):
    return [{"source": R.metas[R.position[c]]["source"]} for c in id_list]

def embeddings_only(q):
    return as_chunks(vec_ids(q, 10))

def bm25_only(q):
    return as_chunks(kw_ids(q, 10))

def hybrid_plain(q):                      # same RRF fusion as retriever.py, but without the code rules
    fused = {}
    for lst in (vec_ids(q, 30), kw_ids(q, 30)):
        for rank, c in enumerate(lst, 1):
            fused[c] = fused.get(c, 0) + 1 / (60 + rank)
    return as_chunks(sorted(fused, key=fused.get, reverse=True)[:10])

def full_system(q):                       # exactly what the app calls
    return R.retrieve(q, k=10)[0]

METHODS = {"embeddings only": embeddings_only, "BM25 only": bm25_only,
           "hybrid (RRF)": hybrid_plain, "full system": full_system}

def first_hit(ranked, expected):
    expected = expected if isinstance(expected, list) else [expected]
    for i, r in enumerate(ranked, 1):
        if r["source"] in expected:
            return i
    return None

items = [e for e in EVAL if e["source"] is not None]
print(f"{len(items)} in-scope questions, {len(OUT_OF_SCOPE)} out-of-scope\n")
print(f"{'method':<18}{'recall@3':>9}{'MRR':>7}{'avg ms':>8}")
by_kind, misses = {}, {}
for name, fn in METHODS.items():
    hits, rr, ms = 0, 0.0, 0.0
    kinds, miss = defaultdict(list), []
    for e in items:
        t = time.perf_counter()
        pos = first_hit(fn(e["q"]), e["source"])
        ms += (time.perf_counter() - t) * 1000
        ok = bool(pos and pos <= 3)
        hits += ok
        rr += 1 / pos if pos else 0
        kinds[e["kind"]].append(ok)
        if not ok:
            miss.append((e["q"][:70], pos))
    n = len(items)
    print(f"{name:<18}{hits / n:>9.2f}{rr / n:>7.2f}{ms / n:>8.0f}")
    by_kind[name], misses[name] = kinds, miss

print("\nrecall@3 by question kind")
kinds_all = sorted({e["kind"] for e in items})
print(f"{'method':<18}" + "".join(f"{k:>12}" for k in kinds_all))
for name in METHODS:
    row = "".join(f"{sum(by_kind[name][k]) / len(by_kind[name][k]):>12.2f}" for k in kinds_all)
    print(f"{name:<18}{row}")

print("\nmisses of the full system (question -> first correct rank):")
for q, pos in misses["full system"]:
    print("  ", q, "->", pos)

# ---- the "not in your notes" gate: refuse when the best similarity is below MIN_SIMILARITY ----
def best_sim(q):
    return R.retrieve(q, k=1)[1]

out_sims = [best_sim(q) for q in OUT_OF_SCOPE]
in_sims = [best_sim(e["q"]) for e in items]
refused = sum(s < R.MIN_SIMILARITY for s in out_sims)
false_ref = sum(s < R.MIN_SIMILARITY for s in in_sims)
print(f"\ngate at {R.MIN_SIMILARITY}: refused {refused}/{len(out_sims)} out-of-scope, "
      f"wrongly refused {false_ref}/{len(in_sims)} in-scope")
print(f"similarity range: out-of-scope {min(out_sims):.2f}-{max(out_sims):.2f}, in-scope {min(in_sims):.2f}-{max(in_sims):.2f}")