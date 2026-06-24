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
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except discord.DiscordException as exc:
            print(f"Failed to sync command tree: {exc}")

    async def on_message(self, message: discord.Message) -> None:
        # 1. Ignore our own messages.
        if message.author.id == self.user.id:
            return

        # Only handle guild messages.
        if message.guild is None:
            return

        # 2. Only react to the configured Eden Bot.
        if message.author.id != self.config.eden_bot_id:
            return

        # 3 & 4. Make sure this is the configured watch channel.
        watch_channel = database.get_watch_channel(message.guild.id)
        if watch_channel is None or message.channel.id != watch_channel:
            return

        # 5. Parse the snitch message.
        parsed = parse_snitch_message(message.content)
        if parsed is None:
            return

        # 6a/6b. Determine whether this triggers an alert.
        matched_reason: str | None = None
        if database.is_blacklisted(message.guild.id, parsed["player"]):
            matched_reason = "blacklist"
        else:
            zone = database.check_coords_in_any_zone(
                message.guild.id, parsed["x"], parsed["y"], parsed["z"]
            )
            if zone is not None:
                matched_reason = zone

        if matched_reason is None:
            return

        # 6c. Find the watchdog role and alert.
        role = discord.utils.get(
            message.guild.roles, name=self.config.watchdog_role_name
        )
        if role is None:
            return

        alert = f"{role.mention} — {parsed['player']} matched in zone {matched_reason}!"
        await message.reply(alert)
        try:
            await message.add_reaction("✅")
        except discord.DiscordException:
            pass


async def main() -> None:
    """Load config, build the bot, and run it."""
    config = load_config()
    bot = WatchdogBot(config)
    async with bot:
        await bot.start(config.token)


if __name__ == "__main__":
    asyncio.run(main())
