"""Sample-level quality check: times are kept unchanged; low-quality text and low-quality interaction may each be only a small fraction; a sample that is almost all orig is dropped."""

from __future__ import annotations

from lcd.common.event import Window, canonical_action

# The appendix only says "a small fraction" and "almost all orig"; those two phrases are written here as ratios.
LOW_QUALITY_MAX = 0.2
ORIG_MAX = 0.9


def finish(events, text_bad, inter_bad, z, outside, sources):
    if any(event.time != source.time for event, source in zip(events, sources)):
        return None
    generated = [i for i, label in enumerate(z) if label == 1]
    if not generated:
        return Window(events, z, outside)
    n = len(generated)
    text_frac = sum(text_bad[i] for i in generated) / n
    inter_frac = sum(inter_bad[i] for i in generated) / n
    orig_frac = sum(canonical_action(events[i].action) == "orig" for i in generated) / n
    if text_frac > LOW_QUALITY_MAX or inter_frac > LOW_QUALITY_MAX or orig_frac > ORIG_MAX:
        return None
    return Window(events, z, outside)
