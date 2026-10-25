"""c = LLM(π, H). Text that is empty, of abnormal length, in the wrong language, repeated, or marked by prompt traces is counted as low quality."""

from __future__ import annotations

import json
import re

from lcd.generate.json_parse import json_obj

PROMPT_MARKS = ("Persona:", "Human context:", "Alias book:")


def _word_count(text: str) -> int:
    return len(text.split())


def _normal_length(text: str, context: list) -> bool:
    words = _word_count(text)
    counts = [_word_count(event.text) for event in context if event.text.strip()]
    if not counts:
        return words > 0
    median = sorted(counts)[len(counts) // 2]
    if words > max(20, median * 4):
        return False
    if median >= 8 and words * 4 < median:
        return False
    return words > 0


def _in_language(text: str, lang: str) -> bool:
    if _word_count(text) < 8 and lang != "zh":
        return True
    if lang == "zh":
        return sum("\u4e00" <= ch <= "\u9fff" for ch in text) > 0
    if lang == "en":
        letters = [ch for ch in text if ch.isalpha()]
        if not letters:
            return False
        return sum(ch.isascii() for ch in letters) / len(letters) >= 0.5
    return True


def text_ok(text: str, persona: dict, context: list, earlier: list) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if any(mark in stripped for mark in PROMPT_MARKS):
        return False
    key = re.sub(r"\s+", " ", stripped.casefold())
    seen = [re.sub(r"\s+", " ", item.casefold()) for item in earlier]
    seen += [re.sub(r"\s+", " ", event.text.casefold()) for event in context]
    if key in seen:
        return False
    if not _normal_length(stripped, context):
        return False
    return _in_language(stripped, persona["language"])


def ask_text(llm, persona: dict, context: list) -> str:
    context_block = "\n".join(event.text for event in context)
    prompt = (
        "Write one post for this account. Return JSON {\"post\": \"...\"}.\n"
        f"Persona: {json.dumps(persona, ensure_ascii=False)}\n"
    )
    if context_block:
        prompt += f"Human context:\n{context_block}\n"
    data = json_obj(llm(prompt))
    return str(data.get("post", "")).strip()
