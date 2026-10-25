"""Subwindow length, and δ_min, κ, and L_anc written from it."""

# Subwindow length. The other three quantities follow from the paper's formulas.
W = 10
DELTA_MIN = W + 1
KAPPA = W // 2 + 1
# Outside history must be long enough to form one feature row; otherwise the anchor falls back to the human center.
L_ANC = W + 1
# The alias book keeps only the K most common targets in the human context.
K_ALIAS = 20

ACTIONS = ("orig", "reply", "share", "mention")
