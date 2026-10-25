"""Estimate μ, σ, the percentiles, τ, λ, and η on the validation set."""

from __future__ import annotations

import numpy as np

from lcd.detect.change import change_score, segment
from lcd.detect.localize import choose_q, mask_of, masks_for_q
from lcd.detect.participation import cdf, choose_tau
from lcd.detect.reference import anchor_of, deviation, fit_reference, profile
from lcd.eval.metrics import family_of, macro, mask_iou_f1
from lcd.features.pipeline import embed_texts, feature_matrix, standardize


def _lambda_grid(items: list) -> list:
    top = max(item["costs"][0] for item in items)
    grid = [0.0]
    if top > 0:
        grid += list(np.geomspace(top / 1e4, top, num=24))
    return grid


def _choose_lambda_eta(items: list) -> tuple:
    """λ and η are the pair with the largest three-family macro-average IoU. On a tie, keep the smaller λ, then the smaller η under that λ."""
    etas = sorted({item["f_dev"] for item in items}) + [float("inf")]
    best = (0.0, float("inf"), -1.0)
    for lam in _lambda_grid(items):
        chosen = [choose_q(item["costs"], lam) for item in items]
        for eta in etas:
            scored = []
            for item, q in zip(items, chosen):
                pred = mask_of(item, q, eta)
                f1, iou = mask_iou_f1(item["z"], pred, item["family"] == "human-only")
                scored.append({"family": item["family"], "iou": iou, "f1": f1})
            iou = macro(scored, "iou")
            if iou > best[2]:
                best = (lam, eta, iou)
    return best[0], best[1]


def fit(val: list, embed, q_cap: int) -> dict:
    human_profiles = []
    for window in val:
        if family_of(window.z) != "human-only":
            continue
        h = profile(window.events, embed)
        if h is not None:
            human_profiles.append(h)
    if not human_profiles:
        raise ValueError("μ and σ come from human-only windows in the validation set")
    mu, sigma, keep = fit_reference(human_profiles)
    items = []
    for window in val:
        raw = feature_matrix(window.events, embed_texts(window.events, embed))
        anchor = anchor_of(window.outside, mu, embed)
        scaled = standardize(raw)
        s_dev = deviation(np.median(raw, axis=0), anchor, sigma, keep)
        costs, cuts = segment(scaled, q_cap)
        items.append(
            {
                "raw": raw,
                "anchor": anchor,
                "s_chg": change_score(scaled),
                "s_dev": s_dev,
                "costs": costs,
                "cuts": cuts,
                "z": list(window.z),
                "family": family_of(window.z),
                "y": 0 if family_of(window.z) == "human-only" else 1,
            }
        )
    chg_values = [item["s_chg"] for item in items]
    dev_values = [item["s_dev"] for item in items]
    for item in items:
        item["u"] = max(cdf(chg_values, item["s_chg"]), cdf(dev_values, item["s_dev"]))
        item["f_dev"] = cdf(dev_values, item["s_dev"])
        item["masks"] = masks_for_q(item)
    lam, eta = _choose_lambda_eta(items)
    return {
        "mu": mu,
        "sigma": sigma,
        "keep": keep,
        "chg_values": chg_values,
        "dev_values": dev_values,
        "tau": choose_tau(items),
        "lam": lam,
        "eta": eta,
        "q_cap": q_cap,
    }
