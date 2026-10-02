**English** | [Español](README.es.md)

# Semantic Note Evaluator

A FastAPI service that evaluates study notes using the **Feynman Technique**. It detects jargon used without real understanding, suggests connections to related concepts via RAG, and generates challenge questions — all through structured LLM output.

Built as the Module 1 Capstone for *"Hackathon 1: Construir un Asistente Inteligente con Llama"*.

## How It Works

```
POST /api/notes/evaluate  { title, content }
        │
        ▼
┌────────────────────────────────────────────────────────────┐
│  1. Semantic Retrieval (RAG)                               │
│     Embedding + cosine similarity → top 3 seed notes       │
│     (threshold ≥ 0.30) injected as grounded context.       │
│                                                            │
│  2. Prompt Assembly (Zero-shot)                            │
│     Feynman Technique evaluator role + note content        │
│     + retrieved context → single LLM call.                 │
│                                                            │
│  3. Constrained Generation (Groq API)                      │
│     JSON Schema mode forces token-level conformance        │
│     to the EvaluationResult contract.                      │
│                                                            │
│  4. Type Validation (Pydantic)                             │
│     Raw JSON → typed DTOs (EvaluationResult, JargonFlag,   │
│     SuggestedLink).                                        │
└────────────────────────────────────────────────────────────┘
        │
        ▼
  200 OK  { status, summary_critique, jargon_flags,
            suggested_links, challenge_question }
```

## Quickstart

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), a [Groq API key](https://console.groq.com/keys)

```bash
# Clone and install
git clone https://github.com/PoliBytes/semantic-note-evaluator.git
cd semantic-note-evaluator
uv sync

# Configure
cp .env.example .env
# Edit .env and set your GROQ_API_KEY

# Run
uv run python -m semantic_note_evaluator.main
```

The server starts at `http://localhost:8100`. Verify with:

```bash
curl http://localhost:8100/health
# {"status":"healthy"}
```

## API

### `POST /api/notes/evaluate`

Evaluates a study note for conceptual depth.

**Request:**

```bash
curl -X POST http://localhost:8100/api/notes/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "What is RAG",
    "content": "RAG uses vector databases to find relevant documents and feeds them to an LLM for better answers."
  }'
```

**Response:**

```json
{
  "status": "flagged",
  "summary_critique": "The note identifies the purpose of RAG but treats 'vector databases' as a black box without explaining that retrieval relies on measuring geometric distance between numerical embeddings.",
  "jargon_flags": [
    {
      "term": "vector databases",
      "critique": "Used without explaining that these store numerical embeddings and measure semantic similarity via cosine distance, not keyword matching."
    },
    {
      "term": "feeds them to an LLM",
      "critique": "Obscures the mechanism: retrieved text is concatenated into the prompt as context, and the LLM is instructed to ground its answer in that context."
    }
  ],
  "suggested_links": [
    {
      "note_title": "RAG (Retrieval-Augmented Generation)",
      "reason": "Provides the two-phase architectural definition that this note glosses over."
    },
    {
      "note_title": "Embedding",
      "reason": "Explains the numerical vectors that make semantic search possible."
    }
  ],
  "challenge_question": "If the vector database returns a semantically similar but factually incorrect document, how does the LLM decide whether to trust the retrieved context over its own parameters?"
}
```

### `GET /health`

Returns `{"status": "healthy"}`.

## Project Structure

```
src/semantic_note_evaluator/
├── main.py                 # FastAPI app, /health and /api/notes/evaluate
├── settings.py             # Pydantic Settings (PORT, GROQ_API_KEY)
├── dependencies.py         # FastAPI dependency injection providers
├── models/
│   └── note.py             # Note(title, content) domain entity
├── repositories/
│   └── in_memory_note_repository.py  # Seed knowledge base (9 LLM-domain notes)
├── services/
│   ├── evaluation_service.py # Orchestrates RAG context, prompt, LLM call, and validation
│   └── retrieval_service.py  # Cosine similarity retrieval with NoteSource protocol
├── clients/
│   └── groq_client.py       # Async Groq API wrapper
├── schemas/
│   ├── evaluation.py         # Pydantic DTOs + JSON schema loader
│   └── evaluation_schema.json  # LLM response contract (single source of truth)
└── prompts/
    ├── __init__.py           # Loads and exports SYSTEM_PROMPT
    └── evaluate_system.md    # Feynman Cognitive Gatekeeper prompt
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `PORT` | Server port | `8100` |
| `GROQ_API_KEY` | Groq API key for LLM inference | *required* |
| `LLM_MODEL` | Groq model identifier for evaluation | *required* |

## Tech Stack

| Component | Technology |
|---|---|
| Web Framework | FastAPI |
| LLM Inference | Groq API (constrained JSON schema mode) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Similarity | scikit-learn (cosine similarity) |
| Config | Pydantic Settings |
| Package Manager | uv |
