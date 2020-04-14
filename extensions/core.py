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

    @commands.command(aliases=['✉', '📧'])
    async def invite(self, ctx):
        """Gets a link to invite this bot to your server."""
        await ctx.send(f"`🔗` *https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot*")

    @commands.command(aliases=['🗄' ,'supportserver'])
    async def serverinvite(self, ctx):
        """Gets the server invite link."""
        await ctx.send(f"`🔗` *https://join.photobox.pw/*")

    @commands.command(aliases=['📁' ,'githubrepo', 'repo'])
    async def githup(self, ctx):
        """Gets the link to the GitHub repository."""
        await ctx.send(f"`🔗` *https://github.com/Snazzah/VideoBox*")

    @commands.command(aliases=['ℹ'])
    async def info(self, ctx):
        """Provides info on the bot itself."""
        
        currproc = psutil.Process(os.getpid())
        usage = self.bot.utils.humanbytes(currproc.memory_info().rss)
        proc_start = datetime.fromtimestamp(currproc.create_time())
        embed = discord.Embed(
            title="VideoBox Information",
            description='\n'.join([
                f"**`💡` WS Ping:** {int(ctx.bot.latency * 1000)} ms",
                "**`👤` Creator:** Snazzah (https://snazzah.com/)",
                "**`📁` GitHub Repo:** [Snazzah/VideoBox](https://github.com/Snazzah/VideoBox)",
                F"**`💻` Version:** {ctx.bot.config['version']}",
                f"**`🕰️` Uptime:** {humanize.naturaldelta(datetime.now() - proc_start)}",
                f"**`⚙️` Memory Usage:** {usage}",
                f"**`🗄️` Servers:** {len(ctx.bot.guilds):,}",
                f"**`🗄️` Shards:** {len(ctx.bot.shards):,}",
                f"**`🗂️` Commands:** {len(ctx.bot.commands):,}",
                f"**`🗃️` Extensions:** {len(ctx.bot.cogs):,}"
            ])
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url_as(static_format='png'))
        if ctx.bot.config.get('color'):
            embed.color = ctx.bot.config.get('color')
        await ctx.send(embed=embed)

    @commands.command(aliases=['pong', '🏓'])
    async def ping(self, ctx):
        """Checks the ping of the bot."""

        before = time.monotonic()
        pong = await ctx.send("`🏓` Ping...")
        after = time.monotonic()
        ping = (after - before) * 1000
        await pong.edit(content=f"`🏓` **Pong!**\n`🔻` WS: {int(ctx.bot.latency * 1000)} ms\n`🔻` REST: {int(ping)} ms")

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Core(bot))
