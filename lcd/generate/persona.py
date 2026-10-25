"""Persona π: distill it from I_0 when a human prefix exists; otherwise simulate it from the language alone."""

from __future__ import annotations

from lcd.common.const import ACTIONS
from lcd.common.event import action_rates
from lcd.generate.json_parse import json_obj


def language_of(events: list) -> str:
    text = " ".join(event.text for event in events)
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return "en"
    if sum("\u4e00" <= ch <= "\u9fff" for ch in text) >= 8:
        return "zh"
    latin = sum(ch.isascii() for ch in letters) / len(letters)
    return "en" if latin >= 0.8 else "other"


def distill_persona(llm, prefix: list) -> dict:
    """With a human prefix, π = LLM(I_0), and the action rates record the true proportions in the prefix."""
    lang = language_of(prefix)
    posts = "\n".join(event.text for event in prefix)
    raw = llm(
        "Summarize this account. Return JSON "
        '{"topics": ["..."], "style": "..."}.\n'
        f"Language: {lang}\n"
        f"Posts:\n{posts}"
    )
    data = json_obj(raw)
    return {
        "language": lang,
        "topics": [str(item) for item in data.get("topics", [])],
        "style": str(data.get("style", "")),
        "rates": action_rates(prefix),
    }


def simulate_persona(llm, lang: str) -> dict:
    """Without a human prefix, π = LLM(ℓ), and the action rates come from this simulation."""
    raw = llm(
        "Invent a social-media persona. Return JSON "
        '{"topics": ["..."], "style": "...", '
        '"orig": 0.5, "reply": 0.2, "share": 0.2, "mention": 0.1}.\n'
        f"Language: {lang}"
    )
    data = json_obj(raw)
    rates = {name: float(data.get(name, 0.0)) for name in ACTIONS}
    total = sum(rates.values())
    if total <= 0:
        rates = {name: 0.25 for name in ACTIONS}
    else:
        rates = {name: rates[name] / total for name in ACTIONS}
    return {
        "language": lang,
        "topics": [str(item) for item in data.get("topics", [])],
        "style": str(data.get("style", "")),
        "rates": rates,
    }
