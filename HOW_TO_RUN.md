# Running this locally in VS Code

1. Open a terminal in this folder.
2. Create a virtual environment (recommended): `python -m venv venv` then activate it.
3. Install dependencies: `pip install -r requirements.txt`
4. Start the API: `uvicorn backend.main:app --reload`
   - Runs at http://127.0.0.1:8000
   - Visit http://127.0.0.1:8000/docs for interactive API docs (try `/api/query` and `/api/compare`)
5. Open `frontend/index.html` directly in your browser (or use the VS Code
   "Live Server" extension) - it calls the API automatically, and falls
   back to built-in mock data (sampled from the real dataset) if the API isn't running.

## Rebuilding the data from scratch

The `data/*_catalog.json` files are already generated and committed, so steps 1-5
above work immediately with no extra setup. If you want to rebuild them (e.g. after
getting a fresher CSV), place your raw CSV somewhere and run:

```
python retrivals/preprocessing.py /path/to/flipkart.csv
```

This overwrites `data/<category>_catalog.json` for every category found in the CSV.

## Running the tests

```
pip install pytest
pytest tests/ -v
```
All 10 tests should pass - they cover preprocessing (schema mapping, price cleaning),
ranking (budget/availability scoring), and comparison (grounding, "Not specified" behavior).

## Turning on semantic search (optional, needs internet)

```
pip install sentence-transformers faiss-cpu
python retrivals/embeddings.py Electronics
python retrivals/embeddings.py mobiles
```
(category name is case-insensitive, matched against the catalog filename). The first
run downloads a small embedding model (~80MB) from Hugging Face - after that it's
cached locally. Once an index exists for a category, `/api/query` automatically blends
semantic matches into the results - no other code changes needed.

## Turning on GPT-4o mini for slot extraction (optional, needs an API key)

1. `pip install openai`
2. `export OPENAI_API_KEY=your_key_here`
3. In `backend/services/intent.py`, change the import from
   `query_understanding.intent_extraction` to `query_understanding.llm_parser`

## What's implemented vs placeholder

Real and working end-to-end (tested against the real Flipkart-derived catalogs):
- `frontend/` - full chat UI, product cards, compare tray
- `backend/` - FastAPI app, `/api/query` and `/api/compare`
- `retrivals/preprocessing.py` - real dataset -> generic schema pipeline
- `query_understanding/intent_extraction.py` - rule-based slot extraction
- `ranking/scoring.py`, `ranking/rerankar.py` - composite scoring and sorting
- `comparison/comparison_engine.py` - grounded comparison tables
- `tests/` - 10 passing pytest tests
- `notebooks/experiment.ipynb` - runs the full pipeline step by step

Real code, marked "BACKEND HOOK", needs one-time setup to activate:
- `retrivals/embeddings.py`, `retrivals/vector_search.py` - needs `sentence-transformers` + `faiss-cpu` + internet for the first model download
- `query_understanding/llm_parser.py` - needs an OpenAI API key
