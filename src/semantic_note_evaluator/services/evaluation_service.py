from semantic_note_evaluator.clients.groq_client import GroqClient
from semantic_note_evaluator.models.note import Note
from semantic_note_evaluator.prompts import SYSTEM_PROMPT
from semantic_note_evaluator.schemas.evaluation import (
    EVALUATION_RESPONSE_FORMAT,
    EvaluationResult,
    NoteInput,
)
from semantic_note_evaluator.services.retrieval_service import RetrievalService

DEFAULT_RETRIEVAL_LIMIT: int = 3
DEFAULT_MIN_SIMILARITY: float = 0.30


class EvaluationService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_client: GroqClient,
        system_prompt: str = SYSTEM_PROMPT,
    ) -> None:
        self.retrieval = retrieval_service
        self.llm = llm_client
        self.system_prompt = system_prompt

    def _format_context(self, similar_notes: list[tuple[Note, float]]) -> str:
        if not similar_notes:
            return "No related notes found."

        context_lines: list[str] = []
        for ref_note, score in similar_notes:
            context_lines.append(f"{ref_note.title} (similarity: {score:.2f})")
            context_lines.append(ref_note.content)
            context_lines.append("")
        return "\n".join(context_lines)

    def _build_user_prompt(self, note: NoteInput, context: str) -> str:
        return (
            f"Note to evaluate\n"
            f"Title: {note.title}\n\n"
            f"{note.content}\n\n"
            f"---\n"
            f"Reference context\n"
            f"{context}"
        )

    async def evaluate(
        self,
        note: NoteInput,
        limit: int = DEFAULT_RETRIEVAL_LIMIT,
        min_similarity: float = DEFAULT_MIN_SIMILARITY,
    ) -> EvaluationResult:
        similar_notes = self.retrieval.retrieve(
            query=note.content,
            limit=limit,
            min_similarity=min_similarity,
        )

        context = self._format_context(similar_notes)
        user_prompt = self._build_user_prompt(note, context)

        raw_json = await self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            response_format=EVALUATION_RESPONSE_FORMAT,
        )

        return EvaluationResult.model_validate_json(raw_json)
