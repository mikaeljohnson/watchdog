"""Parser for Eden Bot snitch relay messages."""

from __future__ import annotations

import re

# Core pattern: [GROUP] player hit snitch SNITCHNAME at [X, Y, Z]
_CORE = (
    r"\[(?P<group>[^\]]+)\]\s+"
    r"(?P<player>\S+)\s+hit\s+snitch\s+"
    r"(?P<snitch>\S+)\s+at\s+"
    r"\[\s*(?P<x>-?\d+)\s*,\s*(?P<y>-?\d+)\s*,\s*(?P<z>-?\d+)\s*\]"
)

# Format 1: <t:UNIX_TIMESTAMP:T> [...]
_SNITCH_RE_WITH_TS = re.compile(r"<t:(?P<timestamp>\d+):[A-Za-z]>\s*" + _CORE)

# Format 2: HH:MM:SS AM/PM [...]  (or just [...])
_SNITCH_RE_NO_TS = re.compile(r"(?:\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM)?\s*)?" + _CORE)

# Format 3: fallback using search (handles leading whitespace etc.)
_SNITCH_RE_SEARCH = re.compile(
    r"(?:<t:(?P<timestamp>\d+):[A-Za-z]>|\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM)?\s*)?"
    + _CORE
)


def parse_snitch_message(content: str) -> dict | None:
    """Parse a snitch relay message into its components.

    Args:
        content: The raw message content.

    Returns:
        A dict with timestamp (0 if not present), group, player (lowercased),
        snitch_name, and x/y/z integers, or None if the message is not a
        valid snitch ping.
    """
    match = _SNITCH_RE_WITH_TS.match(content)
    has_ts = True
    if not match:
        match = _SNITCH_RE_NO_TS.match(content)
        has_ts = False
    if not match:
        # Try search (handles leading whitespace / newlines)
        match = _SNITCH_RE_SEARCH.search(content)
        has_ts = match is not None and match.group("timestamp") is not None
    if not match:
        return None

    ts = int(match.group("timestamp")) if has_ts and match.group("timestamp") else 0

    return {
        "timestamp": ts,
        "group": match.group("group"),
        "player": match.group("player").lower(),
        "snitch_name": match.group("snitch"),
        "x": int(match.group("x")),
        "y": int(match.group("y")),
        "z": int(match.group("z")),
    }