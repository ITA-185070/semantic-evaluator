from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI

from semantic_note_evaluator.dependencies import get_evaluation_service
from semantic_note_evaluator.schemas.evaluation import EvaluationResult, NoteInput
from semantic_note_evaluator.services.evaluation_service import EvaluationService
from semantic_note_evaluator.settings import get_settings

app = FastAPI(
    title="Semantic Note Evaluator",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/api/notes/evaluate", response_model=EvaluationResult)
async def evaluate_note(
    note: NoteInput,
    service: Annotated[EvaluationService, Depends(get_evaluation_service)],
) -> EvaluationResult:
    return await service.evaluate(note)


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
