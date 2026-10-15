"""Main entry point for the Watchdog Discord bot."""

from __future__ import annotations

import asyncio

import discord
from discord.ext import commands

import database
from config import Config, load_config
from snitch_parser import parse_snitch_message


class WatchdogBot(commands.Bot):
    """Discord bot that monitors relayed snitch pings."""

    def __init__(self, config: Config) -> None:
        intents = discord.Intents(messages=True, message_content=True, guilds=True)
        super().__init__(command_prefix="!", intents=intents)
        self.config = config

    async def setup_hook(self) -> None:
        """Load extensions before connecting."""
        database.init_db()
        await self.load_extension("cogs.watchdog")

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user}")
        try:
            for guild in self.guilds:
                g = discord.Object(id=guild.id)
                self.tree.copy_global_to(guild=g)
                await self.tree.sync(guild=g)
            synced = await self.tree.sync()
            print(f"Synced commands to {len(self.guilds)} guild(s) + {len(synced)} global")
        except discord.DiscordException as exc:
            print(f"Failed to sync command tree: {exc}")

    async def on_message(self, message: discord.Message) -> None:
        print(f"[DEBUG] MSG from={message.author.id} ({message.author}) ch={message.channel.id} guild={message.guild}", flush=True)

        # Ignore our own messages.
        if message.author.id == self.user.id:
            print(f"[DEBUG] SKIP: own message", flush=True)
            return

        # Only handle guild messages.
        if message.guild is None:
            print(f"[DEBUG] SKIP: not in guild", flush=True)
            return

        # Only react to the configured Eden Bot.
        if message.author.id != self.config.eden_bot_id:
            print(f"[DEBUG] SKIP: not Eden Bot (got {message.author.id}, expected {self.config.eden_bot_id})", flush=True)
            return

        guild_id = message.guild.id
        content_lower = message.content.lower()
        print(f"[DEBUG] content: {message.content[:200]}", flush=True)
        print(f"[DEBUG] content_lower: {content_lower[:200]}", flush=True)

        # Check if this channel is being watched.
        watch_channels = database.get_watch_channels(guild_id)
        print(f"[DEBUG] watch_channels: {watch_channels}", flush=True)
        if message.channel.id not in watch_channels:
            print(f"[DEBUG] SKIP: channel {message.channel.id} not in watch list", flush=True)
            return

        # CHECK 1: Blacklisted player name appears anywhere in the message
        matched_reason: str | None = None
        bl_players = database.get_blacklist(guild_id)
        print(f"[DEBUG] blacklist: {bl_players}", flush=True)
        for player in bl_players:
            print(f"[DEBUG] checking '{player.lower()}' in '{content_lower}' -> {player.lower() in content_lower}", flush=True)
            if player.lower() in content_lower:
                matched_reason = "blacklist"
                print(f"[DEBUG] BLACKLIST MATCH: {player}", flush=True)
                break

        # CHECK 2: Coordinates match a monitored zone (parse snitch format)
        if matched_reason is None:
            print(f"[DEBUG] no blacklist match, checking zones...", flush=True)
            parsed = parse_snitch_message(message.content)
            if parsed is not None:
                print(f"[DEBUG] parsed: {parsed}", flush=True)
                zone = database.check_coords_in_any_zone(
                    guild_id, parsed["x"], parsed["y"], parsed["z"]
                )
                if zone is not None:
                    matched_reason = zone
                    print(f"[DEBUG] ZONE MATCH: {zone}", flush=True)
            else:
                print(f"[DEBUG] parser returned None", flush=True)

        if matched_reason is None:
            print(f"[DEBUG] no match found, returning", flush=True)
            return

        # Find the watchdog role and alert.
        role = discord.utils.get(
            message.guild.roles, name=self.config.watchdog_role_name
        )
        if role is None:
            print(f"[DEBUG] @watchdog role not found", flush=True)
            return

        alert = f"{role.mention} — {message.content}"
        print(f"[DEBUG] SENDING ALERT: {alert[:200]}", flush=True)
        try:
            await message.reply(alert)
            print(f"[DEBUG] reply sent", flush=True)
        except discord.DiscordException as e:
            print(f"[DEBUG] reply failed ({e}), trying channel.send", flush=True)
            try:
                await message.channel.send(alert)
                print(f"[DEBUG] fallback send worked", flush=True)
            except discord.DiscordException as e2:
                print(f"[DEBUG] send also failed: {e2}", flush=True)
        try:
            await message.add_reaction("✅")
            print(f"[DEBUG] reaction added", flush=True)
        except discord.DiscordException as e:
            print(f"[DEBUG] reaction failed: {e}", flush=True)


async def main() -> None:
    """Load config, build the bot, and run it."""
    config = load_config()
    bot = WatchdogBot(config)
    async with bot:
        await bot.start(config.token)


if __name__ == "__main__":
    asyncio.run(main())