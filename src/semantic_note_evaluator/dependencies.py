from semantic_note_evaluator.repositories.in_memory_note_repository import (
    InMemoryNoteRepository,
)

_note_repository: InMemoryNoteRepository | None = None


def get_note_repository() -> InMemoryNoteRepository:
    global _note_repository
    if _note_repository is None:
        _note_repository = InMemoryNoteRepository()
    return _note_repository
