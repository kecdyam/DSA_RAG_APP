import re
import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

MIN_SIMILARITY = 0.6   # below this, we say "not in your notes"
CODE_PENALTY = 0.5     # code chunks lose half their score unless code was asked for
PREFIX = "Represent this sentence for searching relevant passages: "
STOPWORDS = {"what", "is", "are", "the", "a", "an", "of", "how", "do", "i", "to", "in", "does"}

# PDFs whose pages are really Java programs
CODE_PDFS = {"Singly_Linked_List_Searching.pdf", "Stack_using_Array.pdf"}

# words that mean "I want code" (edit this list as you like)
CODE_WORDS = ["code", "codes", "program", "programs", "java", "snippet", "syntax", "implementation"]

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("dsa")

data = collection.get()
ids = data["ids"]
docs = data["documents"]
metas = data["metadatas"]
position = {cid: i for i, cid in enumerate(ids)}

# True for every chunk that is code (a .java file, or a PDF full of code)
is_code_chunk = [m["type"] == "java" or m["source"] in CODE_PDFS for m in metas]


def tokenize(text):
    words = re.findall(r"\w+", text.lower())
    return [w for w in words if w not in STOPWORDS]


bm25 = BM25Okapi([tokenize(d) for d in docs])


def wants_code(question):
    q = question.lower()
    return any(re.search(r"\b" + re.escape(w) + r"\b", q) for w in CODE_WORDS)


def retrieve(question, k=5, pool=30):
    code_mode = wants_code(question)

    # 1) meaning-based search
    q_vec = model.encode(PREFIX + question, normalize_embeddings=True).tolist()
    res = collection.query(query_embeddings=[q_vec], n_results=pool)
    vec_ids = res["ids"][0]
    best_sim = 1 - res["distances"][0][0]

    # 2) keyword search
    scores = bm25.get_scores(tokenize(question))
    top = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)[:pool]
    kw_ids = [ids[i] for i in top if scores[i] > 0]

    # 3) merge both rankings (RRF)
    fused = {}
    for rank, cid in enumerate(vec_ids, start=1):
        fused[cid] = fused.get(cid, 0) + 1 / (60 + rank)
    for rank, cid in enumerate(kw_ids, start=1):
        fused[cid] = fused.get(cid, 0) + 1 / (60 + rank)

    # 4) theory first, code only when asked
    candidates = list(fused)
    if code_mode:
        code_only = [c for c in candidates if is_code_chunk[position[c]]]
        if code_only:
            candidates = code_only
    else:
        for c in candidates:
            if is_code_chunk[position[c]]:
                fused[c] *= CODE_PENALTY

    best = sorted(candidates, key=fused.get, reverse=True)[:k]
    results = [
        {
            "text": docs[position[c]],
            "source": metas[position[c]]["source"],
            "page": metas[position[c]]["page"],
            "is_code": is_code_chunk[position[c]],
        }
        for c in best
    ]
    return results, best_sim