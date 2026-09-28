import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

SCHEMA_FILE = Path(__file__).parent / "evaluation_schema.json"

with open(SCHEMA_FILE, encoding="utf-8") as _f:
    EVALUATION_JSON_SCHEMA: dict[str, Any] = json.load(_f)

EVALUATION_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "note_evaluation",
        "schema": EVALUATION_JSON_SCHEMA,
    },
}


class NoteInput(BaseModel):
    title: str
    content: str


class JargonFlag(BaseModel):
    term: str
    critique: str


class SuggestedLink(BaseModel):
    note_title: str
    reason: str


class EvaluationResult(BaseModel):
    status: Literal["passed", "flagged"]
    summary_critique: str
    jargon_flags: list[JargonFlag]
    suggested_links: list[SuggestedLink]
    challenge_question: str
