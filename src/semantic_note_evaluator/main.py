import uvicorn
from fastapi import FastAPI

from semantic_note_evaluator.settings import get_settings

app = FastAPI(
    title="Semantic Note Evaluator",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


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
