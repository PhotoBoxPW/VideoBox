# -*- coding: utf-8 -*-

# VideoBox - a bot that creates funny videos.
# All original work by Snazzah, tacibase by taciturasa with some code by ry00001.
# Used and modified with permission.
# See LICENSE for license information.

'''Main File'''

import discord
from discord.ext import commands
import traceback
import json
import os
import sys
import asyncio
import aiohttp
from typing import List, Optional
from dbots import ClientPoster


class Bot(commands.AutoShardedBot):
    """Custom Bot Class that subclasses the commands.ext one"""

    def __init__(self, **options):
        """Initializes the main parts of the bot."""

        # Initializes parent class
        super().__init__(self._get_prefix_new, **options)

        # Setup
        self.extensions_list: List[str] = []
        self._twitter_token = None

        with open('config.json') as f:
            self.config = json.load(f)

            # Info
            self.prefix: List[str] = self.config['prefixes']
            self.version: str = self.config['version']

            # Toggles
            self.case_insensitive: bool = self.config['case_insensitive']
            self.custom_help: bool = self.config['custom_help']

            # Poster
            self.poster = ClientPoster(self, 'discord.py', api_keys = self.config['botlist'])

    def _init_extensions(self):
        """Initializes extensions."""

        # Utils
        # Avoids race conditions with online
        utils_dir = os.listdir('extensions/utils')
        if 'online.py' in utils_dir:
            utils_dir.remove('online.py')
            bot.load_extension('extensions.utils.online')

        # Rest of utils
        for ext in utils_dir:
            if ext.endswith('.py'):
                try:
                    bot.load_extension(f'extensions.utils.{ext[:-3]}')
                    self.extensions_list.append(
                        f'extensions.utils.{ext[:-3]}')
                except Exception as e:
                    print(e)

        # Models
        for ext in os.listdir('extensions/models'):
            if ext.endswith('.py'):
                try:
                    bot.load_extension(f'extensions.models.{ext[:-3]}')
                    self.extensions_list.append(
                        f'extensions.models.{ext[:-3]}')
                except Exception as e:
                    print(e)

        # Extensions
        for ext in os.listdir('extensions'):
            if ext.endswith('.py'):
                try:
                    bot.load_extension(f'extensions.{ext[:-3]}')
                    self.extensions_list.append(
                        f'extensions.{ext[:-3]}')
                except Exception as e:
                    print(e)

    async def _get_prefix_new(self, bot, msg):
        """More flexible check for prefix."""
        return commands.when_mentioned_or(*self.prefix)(bot, msg)

    async def on_ready(self):
        """Initializes the main portion of the bot once it has connected."""

        print('Connected.\n')

        # Prerequisites
        if not hasattr(self, 'request'):
            self.request = aiohttp.ClientSession()
        if not hasattr(self, 'appinfo'):
            self.appinfo = await self.application_info()
        if self.description == '':
            self.description = self.appinfo.description

        await self.change_presence(
            activity=discord.Activity(
                name="FFmpeg render videos | 📹help",
                type=discord.ActivityType.watching
            ),
            status=discord.Status.online
        )

        # NOTE Extension Entry Point
        # Loads core, which loads all other extensions
        if not self.extensions_list:
            self._init_extensions()

        print('Initialized.\n')

        if len(self.config['botlist']) != 0:
            self.poster.start_loop()
            await self.poster.post()

    async def on_message(self, message):
        """Handles what the bot does whenever a message comes across."""

        ctx = await self.get_context(message)

        if not hasattr(bot, 'appinfo'):
            return
        elif message.author.bot or message.type != discord.MessageType.default:
            return
        elif message.author.id in self.config.get('blocked'):
            return
        else:
            await self.process_commands(message)


# Creates Bot object
bot = Bot(max_messages=1, guild_subscriptions=False)


@bot.listen()
async def on_command_error(ctx, error):
    """Handles all errors stemming from ext.commands."""

    if isinstance(error, commands.MissingRequiredArgument):
        args = ""
        if ctx.command.signature:
            args = f" `{ctx.command.signature}`"
        await ctx.send('\n'.join([
            f"`❗` **`{error.param.name}`** (required argument) is missing!",
            f"`|` Usage: {ctx.prefix}{ctx.command}{args}"
        ]))
        return

    if isinstance(error, commands.CommandNotFound) or isinstance(error, commands.CheckFailure):
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"`⏱️` **This command is on a cooldown!** Wait {error.retry_after:.0f} seconds before executing!")
        return

    # Provides a very pretty embed if something's actually a dev's fault.
    elif isinstance(error, commands.CommandInvokeError):

        # Prerequisites
        embed_fallback = f"`🔥` **An error occured: `{type(error.original).__name__}`.** Please report this in the support server. (`📹serverinvite`)"
        formatted_tb = traceback.format_tb(error.original.__traceback__)
        formatted_tb = ''.join(formatted_tb)
        print(error.original)
        print(formatted_tb)

        # Sending
        await ctx.send(embed_fallback)

    # If anything else goes wrong, just go ahead and send it in chat.
    else:
        await ctx.send(error)
# NOTE Bot Entry Point
# Starts the bot
print("Connecting...\n")
bot.run(bot.config['token'])
