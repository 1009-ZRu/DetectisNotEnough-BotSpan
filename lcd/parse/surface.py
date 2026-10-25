"""render and parse: the action and the first target must be read back unchanged."""

from __future__ import annotations

import re

HANDLE = re.compile(r"@([A-Za-z0-9_]{1,15})")
RT = re.compile(r"^\s*RT\s+@([A-Za-z0-9_]{1,15})", re.IGNORECASE)


def screen_name(target: str, used: dict) -> str:
    """Write a target as a screen name the parser can read back."""
    raw = re.sub(r"[^A-Za-z0-9_]", "", str(target))[:15]
    base = raw if raw else ("u" + format(abs(hash(str(target))) % 10**8, "08d"))
    name = base[:15]
    n = 1
    while name.lower() in used and used[name.lower()] != target:
        suffix = str(n)
        name = (base[: 15 - len(suffix)] + suffix)[:15]
        n += 1
    used[name.lower()] = target
    return name


def render(action: str, targets: tuple, text: str) -> str:
    body = text.strip()
    if action == "orig" or not targets:
        return body
    handle = targets[0]
    if action == "reply":
        return f"@{handle} {body}"
    if action == "share":
        return f"RT @{handle} {body}"
    return f"{body} @{handle}".strip()


def parse(surface: str) -> tuple:
    """Surface rule: the action, and the first target."""
    text = surface or ""
    share = RT.match(text)
    if share:
        return "share", (share.group(1),)
    reply = re.match(r"^\s*@([A-Za-z0-9_]{1,15})", text)
    if reply:
        return "reply", (reply.group(1),)
    mention = HANDLE.search(text)
    if mention:
        return "mention", (mention.group(1),)
    return "orig", ()


def parse_matches(action: str, targets: tuple, surface: str) -> bool:
    """parse(render(a, U, c)) must recover a and the first target in U."""
    got_action, got_targets = parse(surface)
    if got_action != action:
        return False
    if action == "orig":
        return got_targets == ()
    return bool(targets) and got_targets[:1] == targets[:1]
