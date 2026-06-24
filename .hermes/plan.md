# Watchdog Discord Bot — Build Plan

## Overview
A Discord bot that monitors snitch pings relayed by Eden Bot, checks against a blacklist of players and monitored location zones, and alerts the @watchdog role.

## Steps

### Step 1: Project Scaffold
- Create `requirements.txt` (discord.py, python-dotenv, pyyaml)
- Create `.env.example` with DISCORD_TOKEN placeholder
- Create `config.yaml.example` with channel_id, eden_bot_id, role_name
- Create `CLAUDE.md` with project instructions
- Initialize git repo

### Step 2: Database Layer
- `database.py` — SQLite with three tables:
  - `guild_config(guild_id, channel_id)` — which channel to watch per guild
  - `blacklisted_players(guild_id, player_name)` — player blacklist
  - `monitored_zones(guild_id, zone_name, x1, y1, z1, x2, y2, z2)` — monitored regions
- Methods: add/remove/list players, add/remove/list zones, point-in-region check

### Step 3: Snitch Parser
- `snitch_parser.py` — regex to extract from eden bot messages:
  - Timestamp (unix)
  - Group (e.g., Yeet-External)
  - Player name
  - Snitch name
  - Coordinates (x, y, z)
- Validates the format before passing to watchdog logic

### Step 4: Watchdog Cog (Discord Commands)
- `cogs/watchdog.py` — slash command group `/watchdog`:
  - `/watchdog channel <channel>` — set watch channel for this guild
  - `/watchdog blacklist add <player>` — blacklist a player
  - `/watchdog blacklist remove <player>` — remove from blacklist
  - `/watchdog blacklist list` — show blacklist
  - `/watchdog monitor add <name> <x1> <y1> <z1> <x2> <y2> <z2>` — add zone
  - `/watchdog monitor remove <name>` — remove zone
  - `/watchdog monitor list` — show monitored zones

### Step 5: Message Listener
- `bot.py` — main entry point:
  - `on_ready` handler
  - `on_message` handler that:
    1. Checks if author == Eden Bot (by ID)
    2. Checks if channel matches configured channel for that guild
    3. Parses snitch format via parser
    4. Checks player blacklist + monitored zones
    5. If match: pings @watchdog role, replies to the triggering message

### Step 6: README & Setup Guide
- Full setup walkthrough: bot creation on Discord Developer Portal, invite URL, config, first run
- Example usage

### Step 7: GitHub Push
- Create repo, push code