"""Recover the event mask from q̂, the half-window shift, and the phase."""

from __future__ import annotations

import math

import numpy as np

from lcd.common.const import KAPPA, W
from lcd.common.event import Window
from lcd.detect.change import change_score, segment
from lcd.detect.participation import cdf
from lcd.detect.reference import anchor_of, deviation
from lcd.features.pipeline import embed_texts, feature_matrix, standardize


def event_cuts(row_cuts: list, n: int) -> list:
    """Shift row cut points by κ = W/2+1, then clip them into the window."""
    mapped = []
    for row in row_cuts:
        event = min(n - 1, max(0, int(row) + KAPPA))
        if 0 < event < n and event not in mapped:
            mapped.append(event)
    return mapped


def mask_from_cuts(n: int, cuts: list, first_human: bool) -> list:
    z = [0] * n
    bounds = [0, *cuts, n]
    human = first_human
    for left, right in zip(bounds, bounds[1:]):
        if not human:
            for i in range(left, right):
                z[i] = 1
        human = not human
    return z


def _pure_rows(mask: list, total: int) -> list:
    rows = []
    for r in range(total):
        window = mask[r + 1 : r + 1 + W]
        if len(window) == W and all(value == 0 for value in window):
            rows.append(r)
    return rows


def choose_phase(raw: np.ndarray, cuts: list, anchor: np.ndarray) -> list:
    """Of the two phases, keep the one whose median of raw rows lying wholly inside the assumed human spans is closer to the anchor. On a tie, the first span is human."""
    n = len(raw) + W
    masks = [mask_from_cuts(n, cuts, True), mask_from_cuts(n, cuts, False)]
    distances = []
    for mask in masks:
        rows = _pure_rows(mask, len(raw))
        if not rows:
            distances.append(math.inf)
            continue
        med = np.median(raw[rows], axis=0)
        distances.append(float(np.linalg.norm(med - anchor)))
    return masks[0] if distances[0] <= distances[1] else masks[1]


def choose_q(costs: list, lam: float) -> int:
    """q̂ = argmin (J_q + λq). Equal cost keeps the smaller q."""
    best_q = 0
    best = costs[0]
    for q in range(1, len(costs)):
        total = costs[q] + lam * q
        if total < best:
            best = total
            best_q = q
    return best_q


def masks_for_q(item: dict) -> list:
    n = len(item["z"])
    masks = []
    for q, row_cuts in enumerate(item["cuts"]):
        if q == 0:
            masks.append(None)
            continue
        masks.append(choose_phase(item["raw"], event_cuts(row_cuts, n), item["anchor"]))
    return masks


def mask_of(item: dict, q: int, eta: float) -> list:
    """When q = 0 the whole window is decided by F_dev(s_dev) and η; otherwise use that q's phase mask."""
    if q == 0:
        label = 1 if item["f_dev"] >= eta else 0
        return [label] * len(item["z"])
    return item["masks"][q]


def localize(window: Window, model: dict, embed) -> tuple:
    """Return (ŷ, ẑ). ŷ follows whichever path's percentile is more extreme; ẑ is decided by q̂, the κ shift, and the phase."""
    raw = feature_matrix(window.events, embed_texts(window.events, embed))
    scaled = standardize(raw)
    anchor = anchor_of(window.outside, model["mu"], embed)
    s_chg = change_score(scaled)
    s_dev = deviation(np.median(raw, axis=0), anchor, model["sigma"], model["keep"])
    u = max(cdf(model["chg_values"], s_chg), cdf(model["dev_values"], s_dev))
    y = 1 if u >= model["tau"] else 0
    item = {
        "raw": raw,
        "anchor": anchor,
        "f_dev": cdf(model["dev_values"], s_dev),
        "z": [0] * len(window.events),
    }
    costs, cuts = segment(scaled, model["q_cap"])
    item["costs"] = costs
    item["cuts"] = cuts
    item["masks"] = masks_for_q(item)
    return y, mask_of(item, choose_q(costs, model["lam"]), model["eta"])
