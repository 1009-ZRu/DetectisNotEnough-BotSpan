"""Internal change: within-block squared distance to the mean, and a penalized multi-segment cut."""

from __future__ import annotations

import numpy as np

from lcd.common.const import DELTA_MIN


def cost_fn(x: np.ndarray):
    total, dim = x.shape
    ps = np.zeros((total + 1, dim))
    pq = np.zeros(total + 1)
    for i in range(total):
        ps[i + 1] = ps[i] + x[i]
        pq[i + 1] = pq[i] + float(np.dot(x[i], x[i]))

    def cost(a: int, b: int) -> float:
        length = b - a
        diff = ps[b] - ps[a]
        return float(pq[b] - pq[a] - np.dot(diff, diff) / length)

    return cost


def change_score(x: np.ndarray) -> float:
    """s_chg: the cost of the whole span minus the best single cut, divided by the number of rows. Each side has at least δ_min rows."""
    total = len(x)
    if total < 2 * DELTA_MIN:
        return 0.0
    cost = cost_fn(x)
    base = cost(0, total)
    best = min(cost(0, r) + cost(r, total) for r in range(DELTA_MIN, total - DELTA_MIN + 1))
    return (base - best) / total


def segment(x: np.ndarray, q_cap: int) -> tuple:
    """J_q: the minimum total cost of a cut into q+1 segments of at least δ_min rows each, and the corresponding row cut points."""
    total = len(x)
    limit = min(q_cap, max(0, total // DELTA_MIN - 1))
    cost = cost_fn(x)
    max_seg = limit + 1
    inf = 1e300
    best = np.full((max_seg + 1, total + 1), inf)
    prev = np.full((max_seg + 1, total + 1), -1, dtype=int)
    if total >= DELTA_MIN:
        for end in range(DELTA_MIN, total + 1):
            best[1, end] = cost(0, end)
    for segs in range(2, max_seg + 1):
        for end in range(segs * DELTA_MIN, total + 1):
            choice = inf
            cut_at = -1
            for start in range((segs - 1) * DELTA_MIN, end - DELTA_MIN + 1):
                value = best[segs - 1, start] + cost(start, end)
                if value < choice:
                    choice = value
                    cut_at = start
            best[segs, end] = choice
            prev[segs, end] = cut_at
    costs = []
    cuts = []
    for q in range(limit + 1):
        segs = q + 1
        costs.append(float(best[segs, total]))
        points = []
        end = total
        for seg in range(segs, 1, -1):
            start = int(prev[seg, end])
            points.append(start)
            end = start
        points.reverse()
        cuts.append(points)
    return costs, cuts
