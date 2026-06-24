# Watchdog Discord Bot

A Discord bot that monitors snitch pings relayed by Eden Bot, checks against a player blacklist and monitored location zones, and alerts the @watchdog role.

## Project Structure

```
watchdog/
├── bot.py              # Main entry point
├── database.py          # SQLite persistence layer
├── snitch_parser.py     # Snitch message parser
├── config.py            # Config loading
├── cogs/
│   └── watchdog.py      # Slash command cog
├── .env                 # Discord bot token (gitignored)
├── config.yaml          # Guild config (channel, eden_bot_id)
├── requirements.txt     # Dependencies
└── README.md            # Setup walkthrough
```

## Key Architecture

- **discord.py** with slash commands (`discord.app_commands`)
- **SQLite** via `sqlite3` stdlib — no ORM
- **Config**: `.env` for secrets, `config.yaml` for watched channels/per-guild settings
- **On message**: filter by author ID (Eden Bot), parse snitch format, check blacklist + monitored zones, ping @watchdog role

## Snitch Message Format

<t:UNIX_TIMESTAMP:T> [GroupName] playerName hit snitch snitchName at [X, Y, Z]

Example:
<t:1782271209:T> [Yeet-External] faie hit snitch yeet-tidehold-river-border at [5496, 62, -3340]

## Commands

All under `/watchdog`:
- `/watchdog channel <channel>` — set watch channel
- `/watchdog blacklist add <player>` — blacklist a player
- `/watchdog blacklist remove <player>` — unblacklist
- `/watchdog blacklist list` — show blacklist
- `/watchdog monitor add <name> <x1> <y1> <z1> <x2> <y2> <z2>` — add zone
- `/watchdog monitor remove <name>` — remove zone
- `/watchdog monitor list` — show monitored zones