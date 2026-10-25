"""Interaction: the rates of the four actions, and how concentrated the targets are."""

from __future__ import annotations

from lcd.common.event import canonical_action


def interaction_features(events: list) -> tuple:
    total = float(len(events))
    mix = []
    for name in ("orig", "reply", "share", "mention"):
        count = sum(canonical_action(event.action) == name for event in events)
        mix.append(count / total)
    targets = [target for event in events for target in event.targets]
    if not targets:
        return (*mix, 0.0, 0.0)
    counts = {}
    for target in targets:
        counts[target] = counts.get(target, 0) + 1
    unique_ratio = len(counts) / len(targets)
    top1 = max(counts.values()) / len(targets)
    return (*mix, unique_ratio, top1)
