"""In-window event e=(t, a, U, c), and a labeled fixed window Γ."""

from __future__ import annotations

from dataclasses import dataclass

from lcd.common.const import ACTIONS


@dataclass
class Event:
    time: str
    action: str
    targets: tuple
    text: str


@dataclass
class Window:
    """Fixed window Γ. events holds the n in-window events, z is the per-event label (length n), and outside is the human history outside the window, Γ^out."""

    events: list
    z: list
    outside: list


def canonical_action(action: str) -> str:
    if action == "original":
        return "orig"
    return action


def action_rates(events: list) -> dict:
    """Rates of the four actions over a span of events. With a human prefix, these are the rates recorded in the persona."""
    total = len(events) or 1
    counts = {name: 0 for name in ACTIONS}
    for event in events:
        name = canonical_action(event.action)
        if name in counts:
            counts[name] += 1
    return {name: counts[name] / total for name in ACTIONS}


def outside_history(before: list, after: list, n: int) -> list:
    """Γ^out: among the human events before and after the window, take the longer side, at most n events nearest the window. If the two sides are equal, take the side before."""
    if len(before) >= len(after):
        return list(before[-n:])
    return list(after[:n])
