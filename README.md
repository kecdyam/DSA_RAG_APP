# DSA Notes RAG App

A Retrieval-Augmented Generation (RAG) pipeline built from scratch in Python. It searches my own Data Structures & Algorithms lecture notes (PDFs) and Java programs, and returns the most relevant passages with their source file and page number.

> **Status:** retrieval is working and has a first evaluation. Answer generation (an LLM that writes cited answers) and a REST API are the next steps.

## What it does

- Reads lecture PDFs with PyMuPDF and Java source files
- Runs OCR (Tesseract) on printed, image-only PDF pages, and keeps the result only if it looks like real text
- Cleans the text and removes NetBeans license headers from Java files
- Splits text into overlapping chunks (about 1,000 characters, 150 overlap) and keeps metadata: source file, page, file type
- Embeds chunks with `BAAI/bge-small-en-v1.5` and stores them in ChromaDB
- **Hybrid retrieval:** vector search (meaning) plus BM25 (exact keywords), merged with Reciprocal Rank Fusion
- **Theory-first ranking:** code chunks are down-ranked unless the question asks for code (for example, it contains "java" or "code")
- Rejects clearly unrelated questions with a similarity threshold
- Includes a small evaluation script that scores retrieval against a hand-checked question set

## How it works

```
DATA/ (PDFs, .java files)
   |
   v
chunker.py   extract text -> clean -> OCR printed scans -> split into chunks + metadata
   |
   v
store.py     embed each chunk -> save in ChromaDB (chroma_db/)
   |
   v
retriever.py vector search + BM25 -> merge (RRF) -> theory-first ranking
   |
   +--> search.py   ask questions in the terminal
   +--> eval.py     score retrieval on a test set
```

## Project structure

| File | Purpose |
|---|---|
| `chunker.py` | Reads PDFs and Java files, cleans text, OCRs printed scans, builds chunks |
| `ocr_helper.py` | Tesseract OCR for one PDF page, with a cache so each page is read once |
| `store.py` | Embeds the chunks and saves them in ChromaDB |
| `retriever.py` | Hybrid retrieval, theory-first ranking, similarity threshold |
| `search.py` | Command-line question loop |
| `eval.py` | Evaluation: recall per question, plus "should refuse" checks |
| `ingest.py`, `check_pdfs.py`, `check_java.py`, `embed_demo.py`, `ocr_test.py` | Small learning and debugging scripts |

## Setup

Requires Python 3.10 or newer.

```bash
git clone https://github.com/kecdyam/DSA_RAG_APP.git
cd demoDSAbot
python -m venv venv
venv\Scripts\activate          # Windows (on Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

**OCR (optional, for printed scanned pages):** install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) for Windows and check that the path at the top of `ocr_helper.py` matches your install. To skip OCR, set `OCR_FILES = set()` in `chunker.py`. The Python packages `pytesseract` and `pillow` are still needed for the import.

## Usage

1. Create a `DATA` folder next to the scripts and put your own PDFs and `.java` files in it (subfolders are fine). The lecture notes used in development are not included in this repo.
2. Build the database (run again whenever your files change):
   ```bash
   python store.py
   ```
3. Ask questions:
   ```bash
   python search.py
   ```
4. Run the evaluation:
   ```bash
   python eval.py
   ```

## Evaluation

The test set has 10 questions: 6 that my notes answer (theory and code questions) and 4 that my notes do not cover (quicksort, Dijkstra vs Bellman-Ford, hash collisions, DP vs greedy vs backtracking). For each answerable question, the correct file and page were checked by hand.

| Check | Result |
|---|---|
| Recall in the top 5 results, 6 answerable questions | 1.0 |
| Correctly refused, 4 questions not in the notes | 0 of 4 |

What I learned:

- **Similarity is not the same as "has the answer".** Questions outside my notes still scored 0.65 to 0.75 against general pages about algorithms, while real questions scored 0.79 to 0.85. A threshold alone cannot reliably refuse, so the plan is to let an LLM judge whether the retrieved chunks actually answer the question.
- **Chunker bugs show up in retrieval.** Leftover license headers in Java files made unrelated code chunks look alike. Fixing the header removal changed the results.
- **Short, image-heavy pages vanished silently.** A minimum-length rule in the chunker dropped pages with little text, which is why OCR was added for printed slides.
- **These 6 questions are easy.** They were built from pages I had already seen. Harder questions, worded differently from the notes, are the next test.

## Known limitations

- Handwritten notes that were scanned as images (linked lists, queues, binary trees, about 40 pages) cannot be read. Tesseract produced unusable text on them, so they are excluded from OCR.
- Java files are cut by size, so a chunk can start or end in the middle of a method.
- Diagram-only pages are skipped, because OCR on figures returns labels, not sentences.
- No answer generation yet: results are passages, not written answers.

## Roadmap

- [x] PDF and Java ingestion, cleaning, chunking with metadata
- [x] Embeddings and ChromaDB storage
- [x] Hybrid retrieval (vector + BM25 + RRF)
- [x] Theory-first ranking, similarity threshold
- [x] Evaluation set with recall scoring
- [x] OCR for printed scanned pages
- [ ] Answer generation with cited sources and "not in the notes" refusals (local Ollama model and optional Claude API)
- [ ] Harder, reworded evaluation questions
- [ ] Vision-model transcription for the handwritten pages
- [ ] Java chunking by class and method
- [ ] REST API with FastAPI (`POST /ask`)
- [ ] Simple Streamlit interface
- [ ] Docker packaging

## Tech stack

Python, PyMuPDF, Tesseract (pytesseract), sentence-transformers (`BAAI/bge-small-en-v1.5`), ChromaDB, rank-bm25.
