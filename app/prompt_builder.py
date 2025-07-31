"""Prompt builder for AI Debugging Copilot.

Composes a structured prompt with the following sections::

1. System instructions (static)
2. Few-shot exemplars
3. Retrieved snippets (vector search)
4. Code context (line references)
5. Error log
6. Summary of recent changes
7. File list
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
import json

SYSTEM_INSTR = "You are an expert software engineer assisting with automated bug fixing.  Respond **only** with valid JSON that follows the provided schema."

_EXEMPLAR_PATH = Path(__file__).with_suffix(".examples.json")

def _load_examples() -> List[dict]:
    if _EXEMPLAR_PATH.exists():
        return json.loads(_EXEMPLAR_PATH.read_text(encoding="utf-8"))
    return []


def build_prompt(error_log: str,
                 summary: str,
                 retrieved_snippets: Iterable[str] | None = None,
                 context_snippets: Iterable[str] | None = None) -> str:
    """Return the full prompt string given all components."""
    parts: list[str] = [SYSTEM_INSTR]

    # Few-shot examples
    examples = _load_examples()
    if examples:
        example_section = "\n\n".join(ex["example"] for ex in examples)
        parts.append("Few-shot examples:\n" + example_section)

    if retrieved_snippets:
        parts.append("Relevant retrieved snippets:\n" + "\n\n".join(retrieved_snippets))
    if context_snippets:
        parts.append("Relevant code context:\n" + "\n\n".join(context_snippets))

    parts.append(f"Error log:\n{error_log}")
    parts.append(f"Summary of changes:\n{summary}")
    prompt = "\n\n".join(parts)
    return prompt
