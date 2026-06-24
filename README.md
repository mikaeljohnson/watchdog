# Watchdog Discord Bot

A Discord bot that monitors snitch pings relayed by **Eden Bot** in your Minecraft server's snitch channel, checks against a player blacklist and monitored location zones, and alerts the **@watchdog** role when a match is found.

## How It Works

1. Eden Bot posts snitch pings to a channel in your Discord server
2. Watchdog watches that channel for messages from Eden Bot
3. When a snitch ping is detected, it parses the player name and coordinates
4. If the player is **blacklisted** OR the snitch is inside a **monitored zone**, Watchdog pings @watchdog in reply to the original message

### Snitch Message Format

Watchdog expects Eden Bot messages in this format:

```
<t:UNIX_TIMESTAMP:T> [GroupName] playerName hit snitch snitchName at [X, Y, Z]
```

Example:
```
<t:1782271209:T> [Yeet-External] faie hit snitch yeet-tidehold-river-border at [5496, 62, -3340]
```

---

## Setup Guide

### Prerequisites

- Python 3.10+
- A Discord server where you can create roles and invite bots
- Eden Bot already in your server posting snitch pings

### Step 1: Create a Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** → name it "Watchdog" → **Create**
3. Go to **Bot** in the left sidebar
4. Click **Reset Token** → **Copy** the token (save it, you'll need it for `.env`)
5. Under **Privileged Gateway Intents**, enable:
   - ✅ **MESSAGE CONTENT INTENT** *(required — Watchdog needs to read message content)*
   - ✅ **SERVER MEMBERS INTENT**
6. Click **Save Changes**

### Step 2: Invite the Bot to Your Server

1. In the Developer Portal, go to **OAuth2** → **URL Generator**
2. Under **Scopes**, check:
   - ✅ `bot`
   - ✅ `applications.commands` *(for slash commands)*
3. Under **Bot Permissions**, check:
   - ✅ `Send Messages`
   - ✅ `Read Message History`
   - ✅ `Add Reactions`
   - ✅ `Mention Everyone` *(needed so it can ping @watchdog)*
4. Copy the generated URL at the bottom, open it in your browser
5. Select your Discord server → **Authorize**

### Step 3: Create the @watchdog Role

In your Discord server:
1. **Server Settings** → **Roles** → **Create Role**
2. Name: `watchdog`
3. Give it any color/permissions you want (or leave defaults)
4. Assign the role to members who should receive snitch alerts

### Step 4: Clone & Configure

```bash
git clone git@github.com:<your-username>/watchdog.git
cd watchdog
```

Copy and edit the config files:

```bash
cp .env.example .env
cp config.example.yaml config.yaml
```

**`.env`** — add your bot token:
```
DISCORD_TOKEN=MTE4NzY2Nz...
```

**`config.yaml`** — default settings (usually don't need to change):
```yaml
# Discord user ID of Eden Bot (the bot relaying snitch pings)
eden_bot_id: 1446004667678195885

# Name of the role to ping on a match
watchdog_role_name: "watchdog"
```

### Step 5: Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### Step 6: Run the Bot

```bash
python bot.py
```

You should see:
```
Logged in as Watchdog#1234
Synced 8 command(s)
```

> **For production**, run it 24/7 on a VPS using `tmux`, `screen`, or a systemd service.

---

## Usage

### Setting the Watch Channel

Once the bot is running, an admin needs to tell it which channel to watch:

```
/watchdog channel #snitch-pings
```
(Replace `#snitch-pings` with the channel where Eden Bot posts)

### Blacklisting Players

**Add a player:**
```
/watchdog blacklist add Notch
```

**Remove a player:**
```
/watchdog blacklist remove Notch
```

**List blacklisted players:**
```
/watchdog blacklist list
```

### Monitoring Locations

**Add a monitored zone:**
```
/watchdog monitor add base -100 0 -100 100 100 100
```
This monitors the cube from (-100, 0, -100) to (100, 100, 100).

**Remove a zone:**
```
/watchdog monitor remove base
```

**List all zones:**
```
/watchdog monitor list
```

### How Alerts Look

When a match is found, Watchdog replies to the Eden Bot message with:

```
@watchdog — faie matched in zone blacklist!
```

And adds a ✅ reaction to the Eden Bot message so you know it was processed.

---

## All Commands

| Command | Description | Permission |
|---|---|---|
| `/watchdog channel #channel` | Set the channel to watch | Manage Server |
| `/watchdog blacklist add <player>` | Blacklist a player | Manage Server |
| `/watchdog blacklist remove <player>` | Unblacklist a player | Manage Server |
| `/watchdog blacklist list` | Show blacklist | Anyone |
| `/watchdog monitor add <name> <x1> <y1> <z1> <x2> <y2> <z2>` | Add monitored zone | Manage Server |
| `/watchdog monitor remove <name>` | Remove zone | Manage Server |
| `/watchdog monitor list` | Show all zones | Anyone |

---

## Project Structure

```
watchdog/
├── bot.py              # Main entry point + message listener
├── config.py           # Config loader (.env + config.yaml)
├── database.py         # SQLite persistence layer
├── snitch_parser.py    # Snitch message regex parser
├── cogs/
│   └── watchdog.py     # Slash command cog
├── .env                # Bot token (gitignored)
├── config.yaml         # Bot config (eden_bot_id, role name)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## License

MIT