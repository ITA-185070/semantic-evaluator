from typing import Annotated

from fastapi import Depends

from semantic_note_evaluator.repositories.in_memory_note_repository import (
    InMemoryNoteRepository,
)
from semantic_note_evaluator.services.retrieval_service import RetrievalService

_note_repository: InMemoryNoteRepository | None = None
_retrieval_service: RetrievalService | None = None


def get_note_repository() -> InMemoryNoteRepository:
    global _note_repository
    if _note_repository is None:
        _note_repository = InMemoryNoteRepository()
    return _note_repository


def get_retrieval_service(
    repo: Annotated[InMemoryNoteRepository, Depends(get_note_repository)],
) -> RetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService(repository=repo)
    return _retrieval_service
