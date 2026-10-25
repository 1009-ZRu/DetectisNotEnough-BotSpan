"""human-only is kept as is, bot-only rewrites the whole window, and partial rewrites only the bot spans."""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from lcd.common.const import W
from lcd.common.event import Event, Window, canonical_action
from lcd.generate.act_gen import generate_event
from lcd.generate.persona import distill_persona, language_of, simulate_persona
from lcd.generate.qc import finish


def even_boundaries(n: int, m: int) -> list:
    """m switches, with the first span human. Each span is at least W+1 so that it contains at least one full subwindow."""
    parts = m + 1
    if m < 1 or parts * (W + 1) > n:
        raise ValueError("cannot place these switches while keeping every span at least W+1")
    base, rem = divmod(n, parts)
    lengths = [base + (1 if i < rem else 0) for i in range(parts)]
    bounds = []
    cursor = 0
    for length in lengths[:-1]:
        cursor += length
        bounds.append(cursor)
    return bounds


def mask_of(n: int, boundaries: list, first_human: bool) -> list:
    z = [0] * n
    cuts = [0, *boundaries, n]
    human = first_human
    for left, right in zip(cuts, cuts[1:]):
        if not human:
            for i in range(left, right):
                z[i] = 1
        human = not human
    return z


def human_only(events: list, outside: list) -> Window:
    copied = [
        Event(event.time, canonical_action(event.action), tuple(event.targets), event.text)
        for event in events
    ]
    return Window(copied, [0] * len(copied), list(outside))


def _rewrite(events, persona, context_of, llm, rng):
    output = []
    text_bad = []
    inter_bad = []
    seen = []
    for index, source in enumerate(events):
        context = context_of(index)
        event, bad_text, bad_inter = generate_event(llm, persona, context, source, seen, rng)
        output.append(event)
        text_bad.append(bad_text)
        inter_bad.append(bad_inter)
        seen.append(event.text)
    return output, text_bad, inter_bad


def bot_only(events: list, outside: list, llm, rng: random.Random | None = None):
    """Rewrite the whole window. No human prefix remains, so the persona is generated from the language alone and the context is empty."""
    rng = rng or random.Random()
    persona = simulate_persona(llm, language_of(events))
    output, text_bad, inter_bad = _rewrite(events, persona, lambda index: [], llm, rng)
    return finish(output, text_bad, inter_bad, [1] * len(output), outside, events)


def bot_only_empty(n: int, lang: str, llm, rng: random.Random | None = None):
    """An account with no tweets: generate the whole window from an empty timeline. With no times to copy, lay them out hourly, then keep them unchanged after generation."""
    start = datetime(2017, 1, 1, tzinfo=timezone.utc)
    blank = []
    for i in range(n):
        stamp = (start + timedelta(hours=i)).isoformat()
        blank.append(Event(stamp, "orig", (), ""))
    rng = rng or random.Random()
    persona = simulate_persona(llm, lang)
    output, text_bad, inter_bad = _rewrite(blank, persona, lambda index: [], llm, rng)
    return finish(output, text_bad, inter_bad, [1] * n, [], blank)


def partial(events: list, m: int, outside: list, llm, rng: random.Random | None = None):
    """Rewrite only the bot spans. H_j is the immediately preceding human span, and bot spans cannot see each other."""
    rng = rng or random.Random()
    bounds = even_boundaries(len(events), m)
    persona = distill_persona(llm, events[: bounds[0]])
    cuts = [0, *bounds, len(events)]
    output = []
    text_bad = []
    inter_bad = []
    seen = []
    human = True
    for left, right in zip(cuts, cuts[1:]):
        if human:
            for source in events[left:right]:
                output.append(
                    Event(
                        source.time,
                        canonical_action(source.action),
                        tuple(source.targets),
                        source.text,
                    )
                )
                text_bad.append(False)
                inter_bad.append(False)
                seen.append(source.text)
        else:
            context = events[cuts[cuts.index(left) - 1] : left]
            for source in events[left:right]:
                event, bad_text, bad_inter = generate_event(llm, persona, context, source, seen, rng)
                output.append(event)
                text_bad.append(bad_text)
                inter_bad.append(bad_inter)
                seen.append(event.text)
        human = not human
    return finish(output, text_bad, inter_bad, mask_of(len(events), bounds, True), outside, events)
