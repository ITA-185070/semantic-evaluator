from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI

from semantic_note_evaluator.clients.groq_client import GroqClient
from semantic_note_evaluator.dependencies import get_llm_client, get_retrieval_service
from semantic_note_evaluator.schemas.evaluation import (
    EVALUATION_RESPONSE_FORMAT,
    EvaluationResult,
    NoteInput,
)
from semantic_note_evaluator.services.retrieval_service import RetrievalService
from semantic_note_evaluator.settings import get_settings

app = FastAPI(
    title="Semantic Note Evaluator",
    version="0.1.0",
)

SYSTEM_PROMPT = """\
You are a rigorous, supportive Cognitive Gatekeeper that evaluates \
personal study notes using the Feynman Technique.

Instructions:
1. Identify jargon used as a crutch — technical terms the author drops without \
explaining the underlying mechanism in plain words.
2. For suggested_links, ONLY reference notes whose EXACT title appears in the \
provided context. NEVER invent or hallucinate note titles.
3. Write one penetrating challenge_question targeting an edge case, failure mode, \
or physical constraint the note ignores.
4. Set status to "passed" only if the note explains mechanisms in plain language \
with minimal unexplained jargon. Otherwise set "flagged".
5. Keep summary_critique to 2-3 sentences: acknowledge strengths, then identify \
the primary conceptual gap.\
"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/api/notes/evaluate", response_model=EvaluationResult)
async def evaluate_note(
    note: NoteInput,
    retrieval: Annotated[RetrievalService, Depends(get_retrieval_service)],
    llm: Annotated[GroqClient, Depends(get_llm_client)],
) -> EvaluationResult:
    similar_notes = retrieval.retrieve(note.content, limit=3, min_similarity=0.30)

    context_lines = []
    for ref_note, score in similar_notes:
        context_lines.append(f"{ref_note.title} (similarity: {score:.2f})")
        context_lines.append(ref_note.content)
        context_lines.append("")
    context = "\n".join(context_lines) if context_lines else "No related notes found."

    user_prompt = (
        f"Note to evaluate\n"
        f"Title:*{note.title}\n\n"
        f"{note.content}\n\n"
        f"---\n"
        f"Reference context\n"
        f"{context}"
    )

    raw_json = await llm.generate(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format=EVALUATION_RESPONSE_FORMAT,
    )

    return EvaluationResult.model_validate_json(raw_json)


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "semantic_note_evaluator.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
