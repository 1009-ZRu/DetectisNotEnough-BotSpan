"""Reference deviation: the raw profile h, the human center μ, and the account's own anchor p."""

from __future__ import annotations

import math

import numpy as np

from lcd.common.const import L_ANC
from lcd.features.pipeline import embed_texts, feature_matrix


def profile(events: list, embed) -> np.ndarray | None:
    """h(Γ): the column-wise median of the raw feature rows. Shorter than L_anc, it cannot yet serve as an anchor."""
    if len(events) < L_ANC:
        return None
    raw = feature_matrix(events, embed_texts(events, embed))
    if len(raw) == 0:
        return None
    return np.median(raw, axis=0)


def anchor_of(outside: list, mu: np.ndarray, embed) -> np.ndarray:
    """p(Γ): use h(Γ^out) when the human history outside the window is long enough; otherwise use the human center μ."""
    got = profile(outside, embed)
    return got if got is not None else mu


def fit_reference(profiles: list) -> tuple:
    """μ and σ come from the human-only profiles on the validation set. Coordinates with σ near 0 are left out of D."""
    mat = np.vstack(profiles)
    mu = np.median(mat, axis=0)
    sigma = np.median(np.abs(mat - mu), axis=0)
    keep = sigma > 1e-8
    return mu, sigma, keep


def deviation(window_profile: np.ndarray, anchor: np.ndarray, sigma: np.ndarray, keep: np.ndarray) -> float:
    """s_dev. It uses the raw profile, not the standardized rows."""
    idx = np.flatnonzero(keep)
    if len(idx) == 0:
        return 0.0
    diff = (window_profile[idx] - anchor[idx]) / sigma[idx]
    return float(np.linalg.norm(diff) / math.sqrt(len(idx)))
