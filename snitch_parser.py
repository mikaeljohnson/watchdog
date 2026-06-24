"""Parser for Eden Bot snitch relay messages."""

from __future__ import annotations

import re

# <t:1782271209:T> [Yeet-External] faie hit snitch yeet-tidehold-river-border at [5496, 62, -3340]
_SNITCH_RE = re.compile(
    r"<t:(?P<timestamp>\d+):[A-Za-z]>\s*"
    r"\[(?P<group>[^\]]+)\]\s+"
    r"(?P<player>\S+)\s+hit\s+snitch\s+"
    r"(?P<snitch>\S+)\s+at\s+"
    r"\[\s*(?P<x>-?\d+)\s*,\s*(?P<y>-?\d+)\s*,\s*(?P<z>-?\d+)\s*\]"
)


def parse_snitch_message(content: str) -> dict | None:
    """Parse a snitch relay message into its components.

    Args:
        content: The raw message content.

    Returns:
        A dict with timestamp, group, player (lowercased), snitch_name, and
        x/y/z integers, or None if the message is not a valid snitch ping.
    """
    match = _SNITCH_RE.search(content)
    if not match:
        return None

    return {
        "timestamp": int(match.group("timestamp")),
        "group": match.group("group"),
        "player": match.group("player").lower(),
        "snitch_name": match.group("snitch"),
        "x": int(match.group("x")),
        "y": int(match.group("y")),
        "z": int(match.group("z")),
    }
