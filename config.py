"""Configuration loading for the Watchdog bot.

Loads secrets from ``.env`` and per-bot settings from ``config.yaml``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import yaml
from dotenv import load_dotenv

_BASE_DIR = os.path.dirname(__file__)
_CONFIG_PATH = os.path.join(_BASE_DIR, "config.yaml")


@dataclass
class Config:
    """Runtime configuration for the bot.

    Attributes:
        token: Discord bot token, read from the ``DISCORD_TOKEN`` env var.
        eden_bot_id: Discord user ID of the Eden Bot relaying snitch pings.
        watchdog_role_name: Name of the role to ping on a match.
    """

    token: str
    eden_bot_id: int
    watchdog_role_name: str = "watchdog"


def load_config() -> Config:
    """Load configuration from ``.env`` and ``config.yaml``.

    Returns:
        A populated :class:`Config` instance.

    Raises:
        RuntimeError: If the Discord token is missing.
    """
    load_dotenv(os.path.join(_BASE_DIR, ".env"))

    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is not set in the environment or .env file")

    data: dict = {}
    if os.path.exists(_CONFIG_PATH):
        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}

    eden_bot_id = int(data.get("eden_bot_id", 0))
    watchdog_role_name = str(data.get("watchdog_role_name", "watchdog"))

    return Config(
        token=token,
        eden_bot_id=eden_bot_id,
        watchdog_role_name=watchdog_role_name,
    )


def guild_config_path(channel_id: int) -> str:
    """Return a per-channel config path helper.

    Args:
        channel_id: The channel ID to build a path for.

    Returns:
        An absolute path scoped to the given channel ID.
    """
    return os.path.join(_BASE_DIR, f"guild_{channel_id}.yaml")
