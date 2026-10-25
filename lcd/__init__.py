"""LCD: synthesize the three timeline types by the paper's method, and localize with the two-path score."""

__version__ = "0.1.0"

from lcd.detect.calibrate import fit
from lcd.detect.localize import localize
from lcd.eval.report import report
from lcd.generate.timeline import bot_only, bot_only_empty, human_only, partial

__all__ = [
    "human_only",
    "bot_only",
    "bot_only_empty",
    "partial",
    "fit",
    "localize",
    "report",
]
