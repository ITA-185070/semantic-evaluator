from typing import Any

from groq import AsyncGroq

DEFAULT_MODEL: str = "llama-3.3-70b-versatile"

EVALUATION_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["passed", "flagged"],
            "description": (
                "Set to 'passed' ONLY if the note explains the underlying mechanisms "
                "in plain words with minimal jargon. Set to 'flagged' if the author uses "
                "technical terms without explaining how they work, hand-waves over crucial "
                "steps, or has logical gaps."
            ),
        },
        "summary_critique": {
            "type": "string",
            "description": (
                "A concise 2-3 sentence Feynman-style assessment. Acknowledge what the "
                "note explains well, then identify the primary conceptual illusion or "
                "missing mechanism."
            ),
        },
        "jargon_flags": {
            "type": "array",
            "description": "Technical terms used as crutches without mechanistic understanding.",
            "items": {
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string",
                        "description": (
                            "The exact technical buzzword, acronym, or abstraction used as a "
                            "substitute for explaining what is physically happening."
                        ),
                    },
                    "critique": {
                        "type": "string",
                        "description": (
                            "Direct explanation of what mechanical detail was skipped "
                            "(e.g., memory layout, network packets, failure modes) and what "
                            "needs plain-English clarification."
                        ),
                    },
                },
                "required": ["term", "critique"],
                "additionalProperties": False,
            },
        },
        "suggested_links": {
            "type": "array",
            "description": "Grounded bidirectional links to reference notes from the retrieved context.",
            "items": {
                "type": "object",
                "properties": {
                    "note_title": {
                        "type": "string",
                        "description": (
                            "The EXACT title of an existing note from the provided reference context. "
                            "You must ONLY pick from the provided context. NEVER invent or hallucinate "
                            "titles not present in the context."
                        ),
                    },
                    "reason": {
                        "type": "string",
                        "description": "A 1-2 sentence explanation of the specific conceptual bridge connecting the two notes.",
                    },
                },
                "required": ["note_title", "reason"],
                "additionalProperties": False,
            },
        },
        "challenge_question": {
            "type": "string",
            "description": (
                "A single penetrating question targeting an edge case, failure mode, or "
                "physical constraint (e.g., 'What happens to the socket buffer when the client hangs?' "
                "or 'How does memory change during this operation?'). Avoid superficial definition questions."
            ),
        },
    },
    "required": [
        "status",
        "summary_critique",
        "jargon_flags",
        "suggested_links",
        "challenge_question",
    ],
    "additionalProperties": False,
}

EVALUATION_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "note_evaluation",
        "schema": EVALUATION_JSON_SCHEMA,
    },
}


class GroqClient:
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        client: AsyncGroq | None = None,
    ) -> None:
        self.model = model
        self._api_key = api_key
        self._client: AsyncGroq | None = client

    @property
    def client(self) -> AsyncGroq:
        if self._client is None:
            if not self._api_key:
                raise ValueError("GROQ_API_KEY is not configured")
            self._client = AsyncGroq(api_key=self._api_key)
        return self._client

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
        temperature: float = 0.5,
    ) -> str:
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_format,
            temperature=temperature,
        )
        return completion.choices[0].message.content or ""
