# ChatDoctor - Clinical AI Assistant

Clinical web assistant: Intent Router + RAG (Qdrant) + Appointment Agent + Explainable AI (XAI).

## Architecture

```
Patient Question
     |
Intent Classifier (medical_info / appointment_request / escalation)
     |                    |                     |
RAG Pipeline        Appointment Agent     Emergency Redirect
(Qdrant + LLM)      (slot-filling)        (911 / ER)
     |                    |                     |
     +-------- XAI Explanation -----------------+
     (decision_path, feature_contributions, retrieval_quality, sources, confidence)
```

## Setup

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (free tier works) | (empty = fallback mode) |
| `EMBEDDING_MODEL` | Sentence-transformers model | `all-MiniLM-L6-v2` |
| `LLM_MODEL` | Gemini model name | `gemini-1.5-flash` |
| `QDRANT_PATH` | Local Qdrant data directory | `./qdrant_data` |
| `COLLECTION_NAME` | Qdrant collection name | `chatdoctor` |

## Data Ingestion

Downloads the ChatDoctor dataset from Kaggle and loads it into Qdrant:

```bash
python -m scripts.ingest                     # full dataset
python -m scripts.ingest --limit 500         # quick test with 500 rows
python -m scripts.ingest --csv file.json     # local file
```

## Run the API

```bash
uvicorn app.main:app --reload
```

## Endpoints

- `GET  /health` - health check
- `POST /chat`   - main chat endpoint

### Example Request

```json
{
  "message": "I have a severe headache and dizziness"
}
```

### Example Response (with XAI)

```json
{
  "answer": "Based on the retrieved source ...",
  "route": "medical_info",
  "xai": {
    "route": "medical_info",
    "confidence": 0.48,
    "rationale": "Message classified as an informational request ...",
    "decision_path": [
      {"step": "red_flag_check", "outcome": "clear", "detail": "..."},
      {"step": "appointment_keyword_check", "outcome": "clear", "detail": "..."},
      {"step": "default_route", "outcome": "medical_info", "detail": "..."},
      {"step": "rag_retrieval", "outcome": "3 sources found", "detail": "Top score: 0.58"},
      {"step": "llm_generation", "outcome": "answer_generated", "detail": "..."}
    ],
    "feature_contributions": {"token_weight:headache": 0.14},
    "sources": [
      {"id": "700", "title": "ChatDoctor row 267", "snippet": "...", "score": 0.58}
    ],
    "retrieval_quality": {
      "avg_score": 0.55,
      "max_score": 0.58,
      "min_score": 0.52,
      "source_count": 3.0
    },
    "safety_note": "This system is for informational purposes only ..."
  }
}
```

## RAGAS Evaluation

```bash
python -m scripts.evaluate_ragas --samples 5
```

Uses Gemini as the judge LLM and Google text embeddings for
`faithfulness`, `answer_relevancy`, `context_precision`, and
`context_recall`.

## XAI (Explainable AI) Features

Every answer includes the following explainability fields:

| Field | Description |
|---|---|
| `decision_path` | Ordered reasoning steps (red_flag_check, routing, retrieval, generation) |
| `feature_contributions` | Which keywords/signals contributed to the decision |
| `retrieval_quality` | Retrieval metrics (avg/max/min score, source count) |
| `sources` | The sources used and their similarity scores |
| `confidence` | Overall confidence score (0-1) |
| `safety_note` | Mandatory medical disclaimer |

## Tests

```bash
pytest
```

## Technology Stack

- **FastAPI** - Backend API
- **Qdrant** - Vector store (local, embedded mode)
- **sentence-transformers** - Embeddings (all-MiniLM-L6-v2)
- **LangChain + Google Gemini** - LLM integration
- **RAGAS** - RAG quality evaluation
- **Pydantic** - Data modeling and validation
