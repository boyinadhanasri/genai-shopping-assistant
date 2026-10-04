# GenAI Shopping Assistant for Conversational Product Discovery and Comparison

A production-grade conversational e-commerce discovery engine that helps users find, filter, compare, and discover products using natural language. Built with FastAPI, React, FAISS, SentenceTransformers, and Groq Llama 3.1.

---

## Key Features

### Natural Language Shopping Assistant
- Understands conversational shopping queries.
- Extracts category, budget, brand, product type, and preferences.
- Supports multi-turn conversations.

### Hybrid Product Search
- Semantic search using SentenceTransformers.
- FAISS vector retrieval.
- Structured filtering using category, budget, brand, and ratings.

### Intelligent Product Ranking
Ranking Formula:

Score = (Semantic Score × 0.7)
      + (Rating Score × 0.2)
      + (Price Score × 0.1)

- Returns the most relevant products.
- Prioritizes relevance, rating, and value.

### Product Comparison Engine
- Side-by-side comparison.
- Price comparison.
- Rating comparison.
- Feature comparison.
- AI-generated recommendation.

### Conversational Memory
Example:

User: Need a phone under ₹20,000

User: Samsung only

User: Show better ratings

The assistant remembers previous context and refines results.

### Analytics Dashboard
- Search logging.
- Product click tracking.
- Query analytics.
- User interaction metrics.

---

## System Architecture

```text
User Query
    │
    ▼
Conversational Memory
    │
    ▼
Query Understanding Layer
(Groq Llama 3.1 / Rule Engine)
    │
    ▼
Hybrid Search Engine
 ├─ FAISS Vector Search
 └─ Structured Filters
    │
    ▼
Ranking Engine
    │
    ▼
Recommendation Layer
    │
    ▼
FastAPI Backend
    │
    ▼
React Frontend
```

---

## Tech Stack

### Backend
- FastAPI
- Python
- FAISS
- SentenceTransformers
- SQLite
- JWT Authentication

### Frontend
- React 19
- Vite
- Tailwind CSS
- Framer Motion

### AI
- Groq API
- Llama 3.1 8B
- Rule-based fallback engine

---

## Authentication Features

- User Registration
- Login
- Email Verification OTP
- Forgot Password
- Password Reset OTP
- JWT Authentication
- Protected Routes
- Password Hashing
- Secure Session Management

---

## Project Structure

```text
genai-shopping-assistant/
│
├── backend/
│   ├── ai/
│   ├── api/
│   ├── auth/
│   ├── config/
│   ├── database/
│   ├── ranking/
│   ├── security/
│   ├── services/
│   └── main.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── data/
├── datasets/
├── scripts/
├── tests/
│
├── requirements.txt
├── README.md
└── .env.example
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/boyinadhanasri/genai-shopping-assistant.git
cd genai-shopping-assistant
```

### Create Environment

```bash
python -m venv .venv
```

Activate:

Windows

```bash
.venv\Scripts\activate
```

Linux/Mac

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create `.env`

```env
GROQ_API_KEY=your_groq_api_key
SHOPAI_JWT_SECRET=your_secret
SHOPAI_JWT_REFRESH_SECRET=your_refresh_secret
```

---

## Train Embeddings

```bash
python scripts/train_embeddings.py
```

---

## Run Backend

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

---

## Run Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## Testing

Run all tests:

```bash
pytest tests/ -v
```

---

## API Endpoints

| Endpoint | Method | Description |
|-----------|----------|-------------|
| / | GET | Health Check |
| /api/chat | POST | AI Shopping Assistant |
| /api/search | GET | Product Search |
| /api/query | POST | Structured Search |
| /api/compare | POST | Product Comparison |
| /api/products | GET | Product Listing |
| /api/products/{id} | GET | Product Details |
| /api/categories | GET | Categories |
| /api/analytics | GET | Analytics |
| /api/auth/login | POST | Login |
| /api/auth/register | POST | Registration |
| /api/auth/forgot-password | POST | Forgot Password |

---

## Dataset Summary

- Total Products: 1200+
- Categories: Electronics, Fashion, Beauty, Books, Sports, Toys, Home & Kitchen, Automotive, Appliances
- Vector Embeddings: 384 Dimensions
- Search Engine: FAISS IndexFlatIP

---

## Future Enhancements

- Amazon Product API Integration
- Flipkart Product API Integration
- Real-Time Pricing
- Personalized Recommendations
- Wishlist
- Cart System
- Order Tracking
- Multi-Language Support

---

## License

Educational and Hackathon Project.

Built for AI-powered conversational product discovery and comparison.