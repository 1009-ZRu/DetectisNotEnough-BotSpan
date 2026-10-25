"""Stack sliding windows into the feature matrix X, then standardize each column by its median and MAD."""

from __future__ import annotations

import numpy as np

from lcd.common.const import W
from lcd.features.interaction import interaction_features
from lcd.features.semantic import meaning_spread
from lcd.features.style import style_features


def embed_texts(events: list, embed) -> list:
    if not events:
        return []
    vectors = embed([event.text for event in events])
    out = []
    for text, vec in zip(events, vectors):
        out.append(None if not text.strip() else np.asarray(vec, dtype=np.float64))
    return out


def feature_matrix(events: list, vectors: list) -> np.ndarray:
    """Row r summarizes events e_{r+1}, ..., e_{r+W}, for T = n - W rows in total."""
    n = len(events)
    rows = []
    for r in range(n - W):
        window = events[r + 1 : r + 1 + W]
        vecs = vectors[r + 1 : r + 1 + W]
        rows.append((*style_features(window), meaning_spread(vecs), *interaction_features(window)))
    return np.asarray(rows, dtype=np.float64)


def standardize(x: np.ndarray) -> np.ndarray:
    """Subtract each column's median, then divide by that column's MAD. A constant column becomes 0."""
    out = np.zeros_like(x)
    for j in range(x.shape[1]):
        col = x[:, j]
        med = float(np.median(col))
        mad = float(np.median(np.abs(col - med)))
        if mad > 0:
            out[:, j] = (col - med) / mad
    return out
