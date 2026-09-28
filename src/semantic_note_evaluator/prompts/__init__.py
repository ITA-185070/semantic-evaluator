from pathlib import Path

_PROMPT_FILE = Path(__file__).parent / "evaluate_system.md"

SYSTEM_PROMPT: str = _PROMPT_FILE.read_text(encoding="utf-8").strip()
