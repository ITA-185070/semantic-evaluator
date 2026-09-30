[English](README.md) | **Español**

# Semantic Note Evaluator

Servicio FastAPI que evalúa notas de estudio aplicando la **Técnica Feynman**. Detecta jerga técnica usada sin comprensión real, sugiere conexiones a conceptos relacionados mediante RAG y genera preguntas de desafío — todo a través de salida estructurada de un LLM.

Desarrollado como cierre del Módulo 1 de *"Hackathon 1: Construir un Asistente Inteligente con Llama"*.

## Cómo Funciona

```
POST /api/notes/evaluate  { title, content }
        │
        ▼
┌────────────────────────────────────────────────────────────┐
│  1. Recuperación Semántica (RAG)                           │
│     Embedding + similitud coseno → top 3 notas seed        │
│     (umbral ≥ 0.30) inyectadas como contexto grounded.     │
│                                                            │
│  2. Ensamblaje de Prompt (Zero-shot)                       │
│     Rol de evaluador Técnica Feynman + contenido de nota   │
│     + contexto recuperado → llamada única al LLM.          │
│                                                            │
│  3. Generación Restringida (Groq API)                      │
│     JSON Schema mode fuerza conformidad a nivel de token   │
│     con el contrato EvaluationResult.                      │
│                                                            │
│  4. Validación de Tipos (Pydantic)                         │
│     JSON crudo → DTOs tipados (EvaluationResult,           │
│     JargonFlag, SuggestedLink).                            │
└────────────────────────────────────────────────────────────┘
        │
        ▼
  200 OK  { status, summary_critique, jargon_flags,
            suggested_links, challenge_question }
```

## Inicio Rápido

**Requisitos:** Python 3.12+, [uv](https://docs.astral.sh/uv/), una [API key de Groq](https://console.groq.com/keys)

```bash
# Clonar e instalar
git clone https://github.com/PoliBytes/semantic-note-evaluator.git
cd semantic-note-evaluator
uv sync

# Configurar
cp .env.example .env
# Editar .env y establecer tu GROQ_API_KEY

# Ejecutar
uv run python -m semantic_note_evaluator.main
```

El servidor inicia en `http://localhost:8100`. Verificar con:

```bash
curl http://localhost:8100/health
# {"status":"healthy"}
```

## API

### `POST /api/notes/evaluate`

Evalúa una nota de estudio en profundidad conceptual.

**Petición:**

```bash
curl -X POST http://localhost:8100/api/notes/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "What is RAG",
    "content": "RAG uses vector databases to find relevant documents and feeds them to an LLM for better answers."
  }'
```

**Respuesta:**

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

Retorna `{"status": "healthy"}`.

## Estructura del Proyecto

```
src/semantic_note_evaluator/
├── main.py                 # App FastAPI, /health y /api/notes/evaluate
├── settings.py             # Pydantic Settings (PORT, GROQ_API_KEY)
├── dependencies.py         # Proveedores de inyección de dependencias
├── models/
│   └── note.py             # Entidad de dominio Note(title, content)
├── repositories/
│   └── in_memory_note_repository.py  # Base de conocimiento seed (9 notas del dominio LLM)
├── services/
│   └── retrieval_service.py  # Recuperación por similitud coseno con protocolo NoteSource
├── clients/
│   └── groq_client.py       # Wrapper asíncrono de la API de Groq
├── schemas/
│   ├── evaluation.py         # DTOs Pydantic + cargador de JSON schema
│   └── evaluation_schema.json  # Contrato de respuesta del LLM (fuente única de verdad)
└── prompts/
    ├── __init__.py           # Carga y exporta SYSTEM_PROMPT
    └── evaluate_system.md    # Prompt del Feynman Cognitive Gatekeeper
```

## Variables de Entorno

| Variable | Descripción | Default |
|---|---|---|
| `PORT` | Puerto del servidor | `8100` |
| `GROQ_API_KEY` | API key de Groq para inferencia LLM | *requerido* |

## Decisiones de Diseño

- **JSON Schema como Fuente Única de Verdad** — El contrato de respuesta del LLM vive en [`evaluation_schema.json`](src/semantic_note_evaluator/schemas/evaluation_schema.json). Tanto la decodificación restringida de Groq como los DTOs Pydantic derivan de este archivo.
- **Contratos Dirigidos por el Consumidor** — `RetrievalService` depende de un `NoteSource(Protocol)`, no de `InMemoryNoteRepository` directamente. El repositorio puede intercambiarse por una base de datos vectorial sin tocar el servicio.
- **Prompt como Recurso Declarativo** — El prompt de sistema vive en un [archivo markdown](src/semantic_note_evaluator/prompts/evaluate_system.md) independiente, no inline en código Python.
- **Sin Interfaces Abstractas para Clients** — `GroqClient` es una clase concreta. Agregar un `Protocol` para proveedores LLM se difiere hasta que un segundo proveedor (ej. Ollama) sea realmente necesario.

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Framework Web | FastAPI |
| Inferencia LLM | Groq API (modo JSON schema restringido) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Similitud | scikit-learn (similitud coseno) |
| Configuración | Pydantic Settings |
| Gestor de Paquetes | uv |
