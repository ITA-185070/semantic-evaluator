from typing import Protocol

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from semantic_note_evaluator.models.note import Note


class NoteSource(Protocol):
    def find_all(self) -> list[Note]: ...


class RetrievalService:
    def __init__(
        self,
        repository: NoteSource,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self.repository = repository
        self._model_name = model_name
        self._model: SentenceTransformer | None = None
        self._embeddings: dict[str, np.ndarray] = {}

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def _get_note_vector(self, note: Note) -> np.ndarray:
        if note.title not in self._embeddings:
            text = f"{note.title}\n{note.content}"
            self._embeddings[note.title] = self.model.encode(text)
        return self._embeddings[note.title]

    def _get_embeddings(self, notes: list[Note]) -> np.ndarray:
        vectors = [self._get_note_vector(note) for note in notes]
        return np.array(vectors)

    def retrieve(
        self,
        query: str,
        limit: int = 3,
        min_similarity: float = 0.30,
    ) -> list[tuple[Note, float]]:
        if not query.strip():
            return []

        notes = self.repository.find_all()
        if not notes:
            return []

        embeddings = self._get_embeddings(notes)
        query_vec = self.model.encode([query])

        scores = cosine_similarity(query_vec, embeddings)[0]

        scored_notes: list[tuple[Note, float]] = [
            (note, float(score))
            for note, score in zip(notes, scores)
            if score >= min_similarity
        ]

        scored_notes.sort(key=lambda item: item[1], reverse=True)
        return scored_notes[:limit]

