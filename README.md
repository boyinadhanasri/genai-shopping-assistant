# GenAI Shopping Assistant for Conversational Product Discovery and Comparison

A production-grade conversational e-commerce discovery engine that lets shoppers find, filter, and compare products using natural language. Built with **FastAPI**, **React 19**, **FAISS**, **SentenceTransformers**, and **Groq (Llama 3.1 8B)**.

---

## 🌟 Key Capabilities

1. **Natural Language Query Understanding**:
   - Extracts category, brand, budget, and feature constraints using **Groq (`llama-3.1-8b-instant`)** with an automatic rule-based regex fallback.
2. **Hybrid Search Engine**:
   - Combines semantic dense retrieval (FAISS with `all-MiniLM-L6-v2`) and structured catalog filtering.
   - **Composite Ranking Formula**:
     $$\text{Score} = (\text{Semantic Score} \times 0.7) + (\text{Rating Score} \times 0.2) + (\text{Price Score} \times 0.1)$$
3. **Conversational Multi-Turn Memory**:
   - Retains conversation context across follow-ups (e.g. *"Need a phone under 20000"* → *"Only Samsung"* → *"Show higher ratings"*).
4. **Grounded Side-by-Side Comparison Matrix**:
   - Generates deterministic, hallucination-free comparison matrices comparing price, rating, brand, and specifications with an automated AI verdict.
5. **Grounded Recommendation Reasons**:
   - Every product recommendation includes clear justification ("Within budget", "High customer satisfaction", "Verified specs").
6. **Analytics & Search Logging**:
   - Tracks search queries and product clicks in `data/search_logs.csv` with a dedicated `GET /api/analytics` dashboard endpoint.

---

## 📐 System Architecture

```
User Message
    │
    ▼
[Conversational Memory Store] ◄── Session History & Accumulated Preferences
    │
    ▼
[LLM Query Understanding] ─────── Groq (llama-3.1-8b-instant) / Rule Parser
    │  (extracts: category, brand, budget, constraints, intent)
    ▼
[Hybrid Search Engine]
    ├── Dense Vector Retrieval ─── FAISS IndexFlatIP (all-MiniLM-L6-v2)
    └── Structured Filtering ───── Category, Brand, Budget, Min Rating
    │
    ▼
[Hybrid Ranking Layer] ────────── 0.7 * Semantic + 0.2 * Rating + 0.1 * Price
    │
    ▼
[Grounded Comparison & Reasoning]
    ├── Side-by-Side Spec Matrix
    └── Why Recommended Explanations
    │
    ▼
[FastAPI REST API] ────────────── /api/chat, /api/search, /api/compare, etc.
    │
    ▼
[React 19 + TailwindCSS SPA] ──── Modern Glassmorphic AI SaaS Interface
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.11 - 3.13)
- Node.js 18+ and npm
- (Optional) Groq API Key from [console.groq.com](https://console.groq.com)

### 2. Environment Setup

Clone repository and configure environment variables:
```bash
cp .env.example .env
```
Add your Groq API key to `.env` (the system operates seamlessly in rule-based fallback mode if left unconfigured):
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Backend Setup & Training

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Generate the unified master catalog (1,206 products across 9 categories):
```bash
python scripts/create_master_catalog.py
```

Train embeddings and build the FAISS vector index:
```bash
python scripts/train_embeddings.py
```

Run test suite to verify all components:
```bash
pytest tests/ -v
```

Start the FastAPI backend server:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 4. Frontend Setup & Run

In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

To produce a production build:
```bash
cd frontend
npm run build
```

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|:---:|---|
| `/` | `GET` | API Health & status check |
| `/api/auth/login` | `POST` | Authenticate user or initialize guest shopper |
| `/api/categories` | `GET` | Retrieve 9 supported shopping categories |
| `/api/products` | `GET` | Paginated product catalog listing (`?limit=20&offset=0&category=...`) |
| `/api/products/{id}` | `GET` | Detailed product specifications and metadata |
| `/api/products/trending` | `GET` | Top-rated trending products |
| `/api/products/recommended` | `GET` | Curated category recommendations with reason tags |
| `/api/search` | `GET` | Semantic vector search with structured filters |
| `/api/query` | `POST` | Structured slot search and reranking |
| `/api/compare` | `POST` | Grounded side-by-side spec comparison table + AI summary |
| `/api/chat` | `POST` | Conversational assistant with multi-turn memory |
| `/api/analytics` | `GET` | Search query frequency and product click metrics |
| `/api/analytics/click` | `POST` | Log product card click events |

---

## 📊 Dataset Statistics

- **Total Catalogs Ingested**: 9 category datasets
- **Total Products Indexed**: 1,206 products
- **Categories**: Electronics (150), Mobiles (150), Appliances (150), Home & Kitchen (150), Fashion (150), Beauty (150), Sports (150), Toys (150), Books (6)
- **Vector Index**: 384-dimensional dense `IndexFlatIP` (Cosine Similarity)
