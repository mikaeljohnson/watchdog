"""SQLite persistence layer for the Watchdog bot.

Stores per-guild watch channels, blacklisted players, and monitored zones.
"""

from __future__ import annotations

import os
import sqlite3

_DB_PATH = os.path.join(os.path.dirname(__file__), "watchdog.db")


def _connect() -> sqlite3.Connection:
    """Open a connection to the database with row access by name."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the database tables if they do not already exist."""
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS watched_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                UNIQUE(guild_id, channel_id)
            );
            CREATE TABLE IF NOT EXISTS blacklisted_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                player_name TEXT NOT NULL COLLATE NOCASE,
                UNIQUE(guild_id, player_name)
            );
            CREATE TABLE IF NOT EXISTS monitored_zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                zone_name TEXT NOT NULL,
                x1 INTEGER, y1 INTEGER, z1 INTEGER,
                x2 INTEGER, y2 INTEGER, z2 INTEGER
            );
            """
        )


# -- Watched channels -------------------------------------------------------

def add_watch_channel(guild_id: int, channel_id: int) -> bool:
    """Add a channel to watch.

    Returns:
        True if the channel was added, False if already watched.
    """
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO watched_channels (guild_id, channel_id) VALUES (?, ?)",
                (guild_id, channel_id),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def remove_watch_channel(guild_id: int, channel_id: int) -> bool:
    """Remove a watch channel.

    Returns:
        True if a row was removed, False if the channel was not watched.
    """
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM watched_channels WHERE guild_id = ? AND channel_id = ?",
            (guild_id, channel_id),
        )
        return cur.rowcount > 0


def get_watch_channels(guild_id: int) -> list[int]:
    """Return all watched channel IDs for a guild."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT channel_id FROM watched_channels WHERE guild_id = ? ORDER BY channel_id",
            (guild_id,),
        ).fetchall()
    return [row["channel_id"] for row in rows]


def is_watched_channel(guild_id: int, channel_id: int) -> bool:
    """Return True if the channel is being watched."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM watched_channels WHERE guild_id = ? AND channel_id = ? LIMIT 1",
            (guild_id, channel_id),
        ).fetchone()
    return row is not None


# -- Blacklist ----------------------------------------------------------------

def add_blacklist(guild_id: int, player_name: str) -> bool:
    """Add a player to the blacklist.

    Returns:
        True if the player was added, False if already blacklisted.
    """
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO blacklisted_players (guild_id, player_name) VALUES (?, ?)",
                (guild_id, player_name),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def remove_blacklist(guild_id: int, player_name: str) -> bool:
    """Remove a player from the blacklist.

    Returns:
        True if a row was removed, False if the player was not blacklisted.
    """
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM blacklisted_players WHERE guild_id = ? AND player_name = ?",
            (guild_id, player_name),
        )
        return cur.rowcount > 0


def get_blacklist(guild_id: int) -> list[str]:
    """Return the list of blacklisted player names for a guild."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT player_name FROM blacklisted_players WHERE guild_id = ? ORDER BY player_name",
            (guild_id,),
        ).fetchall()
    return [row["player_name"] for row in rows]


def is_blacklisted(guild_id: int, player_name: str) -> bool:
    """Return True if the player is blacklisted (case-insensitive)."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM blacklisted_players WHERE guild_id = ? AND player_name = ? LIMIT 1",
            (guild_id, player_name),
        ).fetchone()
    return row is not None


# -- Monitored zones ----------------------------------------------------------

def add_monitor(
    guild_id: int,
    zone_name: str,
    x1: int,
    y1: int,
    z1: int,
    x2: int,
    y2: int,
    z2: int,
) -> bool:
    """Add a monitored zone.

    Returns:
        True on success.
    """
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO monitored_zones
                (guild_id, zone_name, x1, y1, z1, x2, y2, z2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (guild_id, zone_name, x1, y1, z1, x2, y2, z2),
        )
    return True


def remove_monitor(guild_id: int, zone_name: str) -> bool:
    """Remove a monitored zone by name.

    Returns:
        True if a row was removed, False if no such zone existed.
    """
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM monitored_zones WHERE guild_id = ? AND zone_name = ?",
            (guild_id, zone_name),
        )
        return cur.rowcount > 0


def get_monitors(guild_id: int) -> list[dict]:
    """Return all monitored zones for a guild as a list of dicts."""
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT zone_name, x1, y1, z1, x2, y2, z2
            FROM monitored_zones
            WHERE guild_id = ?
            ORDER BY zone_name
            """,
            (guild_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def check_coords_in_any_zone(guild_id: int, x: int, y: int, z: int) -> str | None:
    """Return the name of the first zone containing the point, or None.

    Bounds are inclusive. Zone coordinates are assumed normalized so that
    x1 <= x2, y1 <= y2, z1 <= z2 (enforced at insert time by the cog).
    """
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT zone_name FROM monitored_zones
            WHERE guild_id = ?
              AND ? BETWEEN x1 AND x2
              AND ? BETWEEN y1 AND y2
              AND ? BETWEEN z1 AND z2
            LIMIT 1
            """,
            (guild_id, x, y, z),
        ).fetchone()
    return row["zone_name"] if row else None