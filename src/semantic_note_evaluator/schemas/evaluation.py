import json
from pathlib import Path
from typing import Any

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
