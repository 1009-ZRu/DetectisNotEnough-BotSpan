"""The terminal prints only mask IoU and F1, plus coverage, mae, medae, and hit@2/5/10 for single-switch windows."""

from __future__ import annotations

import numpy as np

from lcd.detect.calibrate import fit
from lcd.detect.localize import localize
from lcd.eval.metrics import boundary_errors, family_of, family_switches, macro, mask_iou_f1


def report(val: list, test: list, embed) -> dict:
    # q_cap does not exceed the largest number of switches seen in this batch of synthetic windows.
    q_cap = max((family_switches(window) for window in [*val, *test]), default=0)
    model = fit(val, embed, q_cap)
    scored = []
    errors = []
    covered = []
    for window in test:
        _y, pred = localize(window, model, embed)
        gold = list(window.z)
        fam = family_of(gold)
        f1, iou = mask_iou_f1(gold, pred, fam == "human-only")
        scored.append({"family": fam, "iou": iou, "f1": f1})
        if fam == "partial" and family_switches(window) == 1:
            errs = boundary_errors(gold, pred)
            errors.extend(errs)
            covered.extend(err for err in errs if err < len(gold))
    result = {
        "mask_IoU": macro(scored, "iou"),
        "mask_F1": macro(scored, "f1"),
    }
    if errors:
        arr = np.asarray(errors, dtype=np.float64)
        result["coverage"] = len(covered) / len(errors)
        result["mae"] = float(np.mean(arr))
        # medae counts only gold boundaries covered by some predicted boundary, and should be read together with coverage.
        result["medae"] = float(np.median(covered)) if covered else float("nan")
        for k in (2, 5, 10):
            result[f"hit@{k}"] = float(np.mean(arr <= k))
    else:
        result["coverage"] = float("nan")
        result["mae"] = float("nan")
        result["medae"] = float("nan")
        for k in (2, 5, 10):
            result[f"hit@{k}"] = float("nan")
    for name in ("mask_IoU", "mask_F1", "coverage", "mae", "medae", "hit@2", "hit@5", "hit@10"):
        print(f"{name} {result[name]:.4f}")
    return result
