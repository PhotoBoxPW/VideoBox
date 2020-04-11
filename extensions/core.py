# -*- coding: utf-8 -*-

# videobox core
# Handles all important main features of any bot.

'''Core File'''

import discord
import os
from discord.ext import commands
import time
import asyncio
import sys
import humanize
import math
import psutil
from datetime import datetime
from extensions.models.help import VBoxHelpCommand
from extensions.utils import checks


class Core(commands.Cog):
    """Provides all core features of a bot."""

    def __init__(self, bot):

        # Main Stuff
        self.bot = bot
        self.extensions_list = bot.extensions_list
        self.emoji = "\U0001F4E6"

        # Help Command
        self._original_help_command = bot.help_command
        if bot.custom_help:
            bot.help_command = VBoxHelpCommand()
        bot.help_command.cog = self

    def _humanbytes(self, B) -> str:  # function lifted from StackOverflow
        """Return the given bytes as a human friendly KB, MB, GB, or TB string."""

        B = float(B)
        KB = float(1024)
        MB = float(KB ** 2)  # 1,048,576
        GB = float(KB ** 3)  # 1,073,741,824
        TB = float(KB ** 4)  # 1,099,511,627,776

        if B < KB:
            return '{0} {1}'.format(
                B, 'Bytes' if 0 == B > 1 else 'Byte')
        elif KB <= B < MB:
            return '{0:.2f} KB'.format(B/KB)
        elif MB <= B < GB:
            return '{0:.2f} MB'.format(B/MB)
        elif GB <= B < TB:
            return '{0:.2f} GB'.format(B/GB)
        elif TB <= B:
            return '{0:.2f} TB'.format(B/TB)

    @commands.command(aliases=['✉', '📧'])
    async def invite(self, ctx):
        """Gets a link to invite this bot to your server."""
        await ctx.send(f"<https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot>")

    @commands.command(aliases=['🗄'])
    async def serverinvite(self, ctx):
        """Gets the server invite link."""
        await ctx.send(f"<https://join.photobox.pw/>")

    @commands.command(aliases=['ℹ'])
    async def info(self, ctx):
        """Provides info on the bot itself."""
        
        currproc = psutil.Process(os.getpid())
        usage = self._humanbytes(currproc.memory_info().rss)
        proc_start = datetime.fromtimestamp(currproc.create_time())
        embed = discord.Embed(
            title="VideoBox Information",
            description='\n'.join([
                f"**:bulb: WS Ping:** {int(ctx.bot.latency * 1000)}",
                "**:bust_in_silhouette: Creator:** Snazzah (https://snazzah.com/)",
                "**:file_folder: GitHub Repo:** [Snazzah/VideoBox](https://github.com/Snazzah/VideoBox)",
                F"**:computer: Version:** {ctx.bot.config['version']}",
                f"**:clock: Uptime:** {humanize.naturaldelta(datetime.now() - proc_start)}",
                f"**:gear: Memory Usage:** {usage}",
                f"**:file_cabinet: Servers:** {len(ctx.bot.guilds):,}",
                f"**:gear: Commands:** {len(ctx.bot.commands):,}",
                f"**:gear: Extensions:** {len(ctx.bot.cogs):,}"
            ])
        )
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Snazzah/PhotoBox/master/avatar.png")
        if ctx.bot.config.get('color'):
            embed.color = ctx.bot.config.get('color')
        await ctx.send(embed=embed)

    @commands.command(aliases=['pong', '🏓'])
    async def ping(self, ctx):
        """Checks the ping of the bot."""

        before = time.monotonic()
        pong = await ctx.send("> 🏓 Ping...")
        after = time.monotonic()
        ping = (after - before) * 1000
        await pong.edit(content=f"> 🏓 **Pong!**\n> WS: {int(ctx.bot.latency * 1000)} ms\n> REST: {int(ping)} ms")

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Core(bot))
