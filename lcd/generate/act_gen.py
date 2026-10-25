"""Actions are drawn from the rates recorded in the persona. A non-orig target comes from the context alias book, or is new."""

from __future__ import annotations

import random

from lcd.common.const import ACTIONS, K_ALIAS
from lcd.common.event import Event
from lcd.generate.text_gen import ask_text, text_ok
from lcd.parse.surface import parse_matches, render, screen_name

# Retry generation a few times when an event fails.
RETRIES = 3


def sample_action(rates: dict, rng: random.Random) -> str:
    pick = rng.random()
    acc = 0.0
    for name in ACTIONS:
        acc += rates[name]
        if pick <= acc:
            return name
    return "orig"


def alias_book(context: list) -> list:
    """V_j: the K most common targets in the human context H_j."""
    counts = {}
    for event in context:
        for target in event.targets:
            counts[target] = counts.get(target, 0) + 1
    ranked = sorted(counts, key=lambda item: (-counts[item], str(item)))
    used = {}
    return [screen_name(str(target), used) for target in ranked[:K_ALIAS]]


def ask_target(llm, book: list) -> str:
    shown = ", ".join(book) if book else "(empty)"
    raw = llm(
        "Choose one interaction target. Reply with one alias, or the word new.\n"
        f"Alias book: {shown}"
    ).strip()
    token = raw.split()[0].strip(",.\"'") if raw.split() else "new"
    if token == "new" or token not in book:
        return "new"
    return token


def generate_event(llm, persona, context, source, earlier, rng):
    """Generate one bot event. The text stores the tweet after render; the action and targets are kept in their fields as well."""
    book = alias_book(context)
    last = None
    text_bad = True
    inter_bad = True
    for _ in range(RETRIES):
        try:
            text = ask_text(llm, persona, context)
        except (ValueError, IndexError, KeyError):
            continue
        action = sample_action(persona["rates"], rng)
        if action == "orig":
            targets = ()
        else:
            chosen = ask_target(llm, book)
            if chosen == "new":
                chosen = screen_name(f"new{len(earlier)}", {})
            targets = (chosen,)
        surface = render(action, targets, text)
        text_bad = not text_ok(text, persona, context, earlier)
        inter_bad = not parse_matches(action, targets, surface)
        last = Event(source.time, action, targets, surface)
        if not text_bad and not inter_bad:
            return last, False, False
    if last is None:
        last = Event(source.time, "orig", (), source.text)
    return last, text_bad, inter_bad
