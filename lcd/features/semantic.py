"""Semantics: how far the texts in a subwindow spread from their mean direction."""

from __future__ import annotations

import numpy as np


def meaning_spread(vectors: list) -> float:
    usable = [vec for vec in vectors if vec is not None]
    if len(usable) < 2:
        return 0.0
    mat = np.vstack(usable)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    mat = mat / norms
    center = mat.mean(axis=0)
    norm = np.linalg.norm(center)
    if norm == 0:
        return 0.0
    center = center / norm
    return float(np.mean(1.0 - mat @ center))
