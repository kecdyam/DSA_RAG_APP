# DSA Notes RAG App

A local, citation-first Retrieval-Augmented Generation (RAG) app over my own Data Structures & Algorithms lecture notes and Java programs. The ingestion, hybrid retrieval, grounding checks, evaluation and web interface are written in Python without a RAG framework (no LangChain or LlamaIndex). Answers are written by a pretrained open-source model (Llama 3.2 3B) running locally; embeddings come from `BAAI/bge-small-en-v1.5`. I did not train either model. The work in this repo is the pipeline around them and the evaluation.

> **Status:** working end to end (ingest, retrieve, cited answers, Streamlit UI, cheat-sheet generator) with a labelled evaluation of retrieval and refusals.

## What it does

- Reads lecture PDFs (PyMuPDF), Word files (python-docx) and Java source files; strips license headers and invisible characters
- OCR (Tesseract) for printed image-only pages and for pictures inside documents (for example pseudocode screenshots); OCR output is kept only if it looks like real text
- Splits text into overlapping chunks (about 1,000 characters, 150 overlap) with source, page and file type metadata, and embeds them into ChromaDB
- **Hybrid retrieval:** vector search plus BM25, merged with Reciprocal Rank Fusion; code chunks are down-ranked unless the question asks for code
- **Cited answers:** the local model must cite excerpts as `[n]` or reply "can't find that in the notes"; a similarity gate refuses clearly unrelated questions before the model is called
- **Streamlit interface:** multiple saved chats, a sources panel with passage previews, and a streaming answer
- **`/cheatsheet <topic>`:** builds a downloadable Markdown cheat sheet section by section. Every bullet must cite an excerpt and pass an automated word-overlap check against it, code is quoted word for word, and sections without evidence say "Not in your notes"
- Experimental: a quote-verification mode (`grounded.py`) that keeps only quotes found verbatim in a retrieved chunk

## How it works

```
DATA/ (PDF, DOCX, .java)
  -> chunker.py    extract, clean, OCR, chunk
  -> store.py      embed, save to ChromaDB (rebuilds from scratch each run)
  -> retriever.py  vector + BM25 -> RRF -> theory-first ranking
  -> llm.py        local model writes a cited answer
  -> app.py        Streamlit UI (chats, sources, /cheatsheet via cheatsheet.py + artifact.py)
```

| File | Purpose |
|---|---|
| `chunker.py`, `ocr_helper.py`, `store.py` | Ingestion, OCR with cache, embedding and storage |
| `retriever.py`, `llm.py` | Hybrid retrieval; answer generation and prompts |
| `app.py`, `styles.css`, `fx.js` | Web interface |
| `artifact.py`, `cheatsheet.py` | Per-section evidence gathering and verified cheat sheets |
| `eval_set.py`, `eval_retrieval.py`, `gate_sweep.py`, `refusal_eval.py`, `strict_eval.py` | Evaluation |

## Setup

Requires Python 3.10 or newer and [Ollama](https://ollama.com).

```bash
git clone https://github.com/kecdyam/DSA_RAG_APP.git
cd DSA_RAG_APP
python -m venv venv
venv\Scripts\activate          # Windows (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
ollama pull llama3.2:3b
```

Optional: install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and check the path at the top of `ocr_helper.py`.

## Usage

1. Put your own PDFs, DOCX and `.java` files in a `DATA` folder (the notes used in development are not included).
2. `python store.py` builds the database (run again whenever files change).
3. `streamlit run app.py` opens the app. Try `/cheatsheet merge sort`.

## Evaluation

Hand-labelled set of **50 questions the notes answer** (4 direct, 4 paraphrased, 5 tricky, 37 notes-based) and **22 questions they do not**. A hit means the correct file appears in the top results (file-level, not page-level).

| Method | recall@3 | MRR |
|---|---|---|
| Embeddings only | 1.00 | 0.99 |
| BM25 only | 0.94 | 0.89 |
| Hybrid (RRF) | 1.00 | 0.96 |
| Full system (hybrid + theory-first rules) | 0.90 | 0.86 |

recall@3 by question type:

| Method | direct | notes-based | paraphrased | tricky |
|---|---|---|---|---|
| Embeddings only | 1.00 | 1.00 | 1.00 | 1.00 |
| BM25 only | 0.75 | 0.95 | 1.00 | 1.00 |
| Hybrid (RRF) | 1.00 | 1.00 | 1.00 | 1.00 |
| Full system | 1.00 | 0.86 | 1.00 | 1.00 |

What I found:

- **Hybrid did not beat embeddings alone** on this corpus (about 150 chunks with well-separated topics). BM25 is weaker, mostly on long, generic questions.
- **My own ranking rule hurt recall.** The full system's 5 misses are all "Java" or "implement" questions: the word "java" switches retrieval to code-only mode, so it returned code files instead of the lecture slides.
- **The scores have a ceiling.** Most questions were written from the notes and labels are per file, so this measures finding the right file, not answer quality.
- **A similarity threshold cannot separate in-scope from out-of-scope questions.** In-scope questions scored 0.66 to 0.91 and out-of-scope 0.50 to 0.75. At the 0.6 gate, 3 of 22 out-of-scope questions were refused and 0 of 50 real ones.

End-to-end refusals (local model, similarity gate 0.70). All 22 out-of-scope questions, and an even sample of 20 of the 50 in-scope questions:

| Policy | Out-of-scope refused (of 22) | Real questions wrongly refused (of 20) |
|---|---|---|
| Similarity gate only | 15 | 1 |
| Gate + model refusal | 16 | 1 |
| Gate + quote check | 18 | 5 |

- The gate does most of the work. Moving it from 0.60 to 0.70 raised refusals from 3 to 15 of 22, but 0.70 was picked from a sweep on these same questions, so the figure is optimistic and needs a fresh hold-out set.
- The quote check (the model must copy an exact sentence from a retrieved passage) refuses 3 more out-of-scope questions but also refuses 4 of the 19 answerable questions that passed the gate. It fails on pseudocode, tables and short definitions, so it is an optional strict mode and not the default.
- 4 out-of-scope questions were still answered from the model's own knowledge (for example recursion vs iteration), because their similarity was above the gate.

## Known limitations

- About 40 pages of handwritten, scanned notes (linked lists, queues, binary trees) are not indexed: Tesseract returns unusable text on handwriting. 10 evaluation questions that depend on them are kept out of the scores.
- Text read from pictures is noisy (for example `ifp<r` for `if p<r`), and only some PDFs have their embedded pictures read.
- The 3B model answered 4 of 22 out-of-scope questions anyway (similarity 0.70 to 0.74); a reranker or a stronger grounding check is the next step.
- Java files are chunked by size, so a chunk can start in the middle of a method.

## Roadmap

- [x] Ingestion, OCR, chunking, ChromaDB, hybrid retrieval
- [x] Cited answers with a local model, Streamlit UI, multiple chats
- [x] Cheat-sheet generator with verified bullets
- [x] Labelled evaluation (50 in-scope, 22 out-of-scope)
- [ ] Reranker or answer-grounding check to improve refusals
- [ ] Better handling of "how do I implement X" questions
- [ ] Transcribe the handwritten pages and add them to the index
- [ ] Java chunking by class and method
- [ ] REST API (FastAPI) and Docker packaging

## Tech stack

Python, PyMuPDF, python-docx, Tesseract, sentence-transformers, ChromaDB, rank-bm25, Ollama (Llama 3.2 3B), Streamlit.