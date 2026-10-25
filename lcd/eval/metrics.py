"""Masks are macro-averaged over the three families. A human-only gold mask is all zeros, and only an empty prediction counts as correct."""

from __future__ import annotations

from collections import defaultdict

from lcd.common.event import Window

FAMILIES = ("human-only", "bot-only", "partial")


def family_of(z: list) -> str:
    if all(value == 0 for value in z):
        return "human-only"
    if all(value == 1 for value in z):
        return "bot-only"
    return "partial"


def family_switches(window: Window) -> int:
    return sum(window.z[i] != window.z[i - 1] for i in range(1, len(window.z)))


def mask_iou_f1(gold: list, pred: list, human_only: bool) -> tuple:
    if human_only:
        empty = all(value == 0 for value in pred)
        return (1.0, 1.0) if empty else (0.0, 0.0)
    tp = fp = fn = 0
    for g, p in zip(gold, pred):
        if g == 1 and p == 1:
            tp += 1
        elif g == 0 and p == 1:
            fp += 1
        elif g == 1 and p == 0:
            fn += 1
    if tp + fp + fn == 0:
        return 1.0, 1.0
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return f1, tp / (tp + fp + fn)


def macro(items: list, key: str) -> float:
    groups = defaultdict(list)
    for item in items:
        groups[item["family"]].append(item[key])
    means = [sum(groups[name]) / len(groups[name]) for name in FAMILIES if groups[name]]
    if not means:
        return float("nan")
    return sum(means) / len(means)


def boundary_errors(gold: list, pred: list) -> list:
    """Distance from each gold boundary to the nearest predicted boundary. If the window has no predicted boundary, the error is n."""
    n = len(gold)
    points = [i for i in range(1, n) if gold[i] != gold[i - 1]]
    hats = [i for i in range(1, n) if pred[i] != pred[i - 1]]
    if not hats:
        return [float(n)] * len(points)
    return [float(min(abs(point - hat) for hat in hats)) for point in points]
