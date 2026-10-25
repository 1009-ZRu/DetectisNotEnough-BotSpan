"""Participation decision: each of the two paths becomes a validation-set percentile, u takes the larger one, and τ maximizes F1."""

from __future__ import annotations

import math


def cdf(values: list, score: float) -> float:
    return sum(value <= score for value in values) / len(values)


def participation_f1(y: list, pred: list) -> float:
    tp = sum(gold == 1 and hat == 1 for gold, hat in zip(y, pred))
    fp = sum(gold == 0 and hat == 1 for gold, hat in zip(y, pred))
    fn = sum(gold == 1 and hat == 0 for gold, hat in zip(y, pred))
    if tp == 0:
        return 0.0
    prec = tp / (tp + fp)
    rec = tp / (tp + fn)
    return 2 * prec * rec / (prec + rec)


def choose_tau(items: list) -> float:
    labels = [item["y"] for item in items]
    best_tau, best_f1 = math.inf, -1.0
    for tau in sorted({item["u"] for item in items}) + [math.inf]:
        pred = [1 if item["u"] >= tau else 0 for item in items]
        score = participation_f1(labels, pred)
        if score > best_f1 or (score == best_f1 and tau > best_tau):
            best_tau, best_f1 = tau, score
    return best_tau
