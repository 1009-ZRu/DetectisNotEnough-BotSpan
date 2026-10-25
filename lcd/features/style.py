"""Style: post length, punctuation, and literal repetition."""

from __future__ import annotations

import math


def style_features(events: list) -> tuple:
    words = [len(event.text.split()) for event in events]
    mean_words = sum(words) / len(events)
    chars = "".join(event.text for event in events)
    punct = 0
    for ch in chars:
        if not ch.isalnum() and not ch.isspace():
            punct += 1
    punct_ratio = punct / len(chars) if chars else 0.0
    folded = " ".join(event.text.lower() for event in events)
    grams = [folded[i : i + 3] for i in range(max(0, len(folded) - 2))]
    if grams:
        repeat = 1.0 - len(set(grams)) / len(grams)
    else:
        repeat = 0.0
    return (math.log1p(mean_words), punct_ratio, repeat)
