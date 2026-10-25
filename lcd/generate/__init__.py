"""Synthesis of the three timeline types. The model is called only in this layer."""

from lcd.generate.timeline import bot_only, bot_only_empty, human_only, partial

__all__ = ["human_only", "bot_only", "bot_only_empty", "partial"]
