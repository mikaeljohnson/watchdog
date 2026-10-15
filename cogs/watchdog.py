"""Slash command cog exposing the ``/watchdog`` command group."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import database


class Watchdog(commands.Cog):
    """Cog holding the ``/watchdog`` slash command group."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group = app_commands.Group(
        name="watchdog",
        description="Configure snitch monitoring.",
        guild_only=True,
    )

    channel = app_commands.Group(
        name="channel",
        description="Manage watched channels.",
        parent=group,
    )

    blacklist = app_commands.Group(
        name="blacklist",
        description="Manage the player blacklist.",
        parent=group,
    )

    monitor = app_commands.Group(
        name="monitor",
        description="Manage monitored location zones.",
        parent=group,
    )

    # -- /watchdog channel -------------------------------------------------

    @channel.command(name="add", description="Add a channel to watch for snitch pings.")
    @app_commands.describe(channel="The channel Eden Bot posts snitch pings in.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def channel_add(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ) -> None:
        added = database.add_watch_channel(interaction.guild_id, channel.id)
        if added:
            msg = f"Now watching {channel.mention} for snitch pings."
        else:
            msg = f"Already watching {channel.mention}."
        await interaction.response.send_message(msg, ephemeral=True)

    @channel.command(name="remove", description="Stop watching a channel.")
    @app_commands.describe(channel="The channel to stop watching.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def channel_remove(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ) -> None:
        removed = database.remove_watch_channel(interaction.guild_id, channel.id)
        if removed:
            msg = f"Stopped watching {channel.mention}."
        else:
            msg = f"Was not watching {channel.mention}."
        await interaction.response.send_message(msg, ephemeral=True)

    @channel.command(name="list", description="Show all watched channels.")
    async def channel_list(self, interaction: discord.Interaction) -> None:
        channels = database.get_watch_channels(interaction.guild_id)
        if not channels:
            await interaction.response.send_message(
                "No channels configured. Use `/watchdog channel add` first.",
                ephemeral=True,
            )
            return

        lines = []
        for ch_id in channels:
            ch = interaction.guild.get_channel(ch_id)
            if ch:
                lines.append(f"• {ch.mention}")
            else:
                lines.append(f"• `#{ch_id}` (deleted?)")
        await interaction.response.send_message(
            "**Watched channels:**\n" + "\n".join(lines), ephemeral=True
        )

    # -- /watchdog blacklist ----------------------------------------------

    @blacklist.command(name="add", description="Add a player to the blacklist.")
    @app_commands.describe(player="The player name to blacklist.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def blacklist_add(self, interaction: discord.Interaction, player: str) -> None:
        added = database.add_blacklist(interaction.guild_id, player)
        if added:
            msg = f"Added **{player}** to the blacklist."
        else:
            msg = f"**{player}** is already blacklisted."
        await interaction.response.send_message(msg, ephemeral=True)

    @blacklist.command(name="remove", description="Remove a player from the blacklist.")
    @app_commands.describe(player="The player name to remove.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def blacklist_remove(self, interaction: discord.Interaction, player: str) -> None:
        removed = database.remove_blacklist(interaction.guild_id, player)
        if removed:
            msg = f"Removed **{player}** from the blacklist."
        else:
            msg = f"**{player}** was not on the blacklist."
        await interaction.response.send_message(msg, ephemeral=True)

    @blacklist.command(name="list", description="Show the blacklisted players.")
    async def blacklist_list(self, interaction: discord.Interaction) -> None:
        players = database.get_blacklist(interaction.guild_id)
        if not players:
            await interaction.response.send_message(
                "No players are blacklisted.", ephemeral=True
            )
            return

        chunk_size = 20
        chunks = [players[i : i + chunk_size] for i in range(0, len(players), chunk_size)]

        header = f"**Blacklisted players ({len(players)}):**\n"
        first = header + "\n".join(f"• {p}" for p in chunks[0])
        await interaction.response.send_message(first, ephemeral=True)
        for chunk in chunks[1:]:
            await interaction.followup.send(
                "\n".join(f"• {p}" for p in chunk), ephemeral=True
            )

    # -- /watchdog monitor -------------------------------------------------

    @monitor.command(name="add", description="Add a monitored location zone.")
    @app_commands.describe(
        name="A label for the zone.",
        x1="First corner X",
        y1="First corner Y",
        z1="First corner Z",
        x2="Second corner X",
        y2="Second corner Y",
        z2="Second corner Z",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def monitor_add(
        self,
        interaction: discord.Interaction,
        name: str,
        x1: int,
        y1: int,
        z1: int,
        x2: int,
        y2: int,
        z2: int,
    ) -> None:
        lo_x, hi_x = sorted((x1, x2))
        lo_y, hi_y = sorted((y1, y2))
        lo_z, hi_z = sorted((z1, z2))

        database.add_monitor(
            interaction.guild_id, name, lo_x, lo_y, lo_z, hi_x, hi_y, hi_z
        )
        await interaction.response.send_message(
            f"Added monitored zone **{name}**: "
            f"[{lo_x}, {lo_y}, {lo_z}] → [{hi_x}, {hi_y}, {hi_z}].",
            ephemeral=True,
        )

    @monitor.command(name="remove", description="Remove a monitored zone.")
    @app_commands.describe(name="The zone label to remove.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def monitor_remove(self, interaction: discord.Interaction, name: str) -> None:
        removed = database.remove_monitor(interaction.guild_id, name)
        if removed:
            msg = f"Removed monitored zone **{name}**."
        else:
            msg = f"No monitored zone named **{name}**."
        await interaction.response.send_message(msg, ephemeral=True)

    @monitor.command(name="list", description="List all monitored zones.")
    async def monitor_list(self, interaction: discord.Interaction) -> None:
        zones = database.get_monitors(interaction.guild_id)
        if not zones:
            await interaction.response.send_message(
                "No monitored zones configured.", ephemeral=True
            )
            return

        lines = [
            f"• **{z['zone_name']}**: "
            f"[{z['x1']}, {z['y1']}, {z['z1']}] → [{z['x2']}, {z['y2']}, {z['z2']}]"
            for z in zones
        ]
        await interaction.response.send_message(
            "**Monitored zones:**\n" + "\n".join(lines), ephemeral=True
        )

    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Handle errors from watchdog commands gracefully."""
        if isinstance(error, app_commands.MissingPermissions):
            msg = "You need **Manage Server** permission to use this command."
        else:
            msg = f"Error: {error}"
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                await interaction.followup.send(msg, ephemeral=True)
        except Exception:
            pass
        print(f"Watchdog error: {error}", flush=True)


async def setup(bot: commands.Bot) -> None:
    """Entry point used by ``bot.load_extension``."""
    await bot.add_cog(Watchdog(bot))