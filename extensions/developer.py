# -*- coding: utf-8 -*-

# Developer functions
# Provides functions only useable for developers

'''Developer Cog'''

import discord
from discord.ext import commands
import datetime
from collections import OrderedDict
from contextlib import redirect_stdout
import traceback
import time
import io
import inspect
import textwrap
import subprocess
from extensions.utils import checks


class Developer(commands.Cog):
    """Provides various resources for developers."""

    def __init__(self, bot):

        # Main Stuff
        self.bot = bot
        self.request = bot.request
        self.online = bot.online
        self.emoji = "\U0001F3D7"

        # Repl/Eval Stuff
        self._eval = {}
        self.extensions_list = bot.extensions_list

    @commands.command(name='eval')
    async def eval_cmd(self, ctx, *, code: str):
        """Evaluates Python code."""

        if self._eval.get('env') is None:
            self._eval['env'] = {}
        if self._eval.get('count') is None:
            self._eval['count'] = 0

        codebyspace = code.split(" ")
        silent = False
        if codebyspace[0] == "--silent" or codebyspace[0] == "-s":
            silent = True
            codebyspace = codebyspace[1:]
            code = " ".join(codebyspace)

        self._eval['env'].update({
            'self': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'channel': ctx.message.channel,
            'guild': ctx.message.guild,
            'author': ctx.message.author,
        })

        # let's make this safe to work with
        code = code.replace('```py\n', '').replace('```', '').replace('`', '')

        _code = (
            'async def func(self):\n  try:\n{}\n  '
            'finally:\n    self._eval[\'env\'].update(locals())').format(
                textwrap.indent(code, '    '))

        before = time.monotonic()
        # noinspection PyBroadException
        try:
            exec(_code, self._eval['env'])
            func = self._eval['env']['func']
            output = await func(self)

            if output is not None:
                output = repr(output)
        except Exception as e:
            output = '{}: {}'.format(type(e).__name__, e)
        after = time.monotonic()
        self._eval['count'] += 1
        count = self._eval['count']

        code = code.split('\n')
        if len(code) == 1:
            _in = 'In [{}]: {}'.format(count, code[0])
        else:
            _first_line = code[0]
            _rest = code[1:]
            _rest = '\n'.join(_rest)
            _countlen = len(str(count)) + 2
            _rest = textwrap.indent(_rest, '...: ')
            _rest = textwrap.indent(_rest, ' ' * _countlen)
            _in = 'In [{}]: {}\n{}'.format(count, _first_line, _rest)

        message = '```py\n{}'.format(_in)
        if output is not None:
            message += '\nOut[{}]: {}'.format(count, output)
        ms = int(round((after - before) * 1000))
        if ms > 100:  # noticeable delay
            message += '\n# {} ms\n```'.format(ms)
        else:
            message += '\n```'

        try:
            if ctx.author.id == self.bot.user.id:
                await ctx.message.edit(content=message)
            else:
                if not silent:
                    await ctx.send(message)
        except discord.HTTPException:
            if not silent:
                url = await self.online.hastebin(output)
                embed = discord.Embed(
                    description=f"[View output - click]({url})"
                )
                await ctx.send(embed=embed)

    @commands.command(aliases=['sys',  'sh'])
    async def system(self, ctx, *, command: str):
        """Runs system commands."""

        msg = await ctx.send(
            '<a:loading:393852367751086090> Processing...'
        )
        result: tuple = ()
        try:
            process = subprocess.Popen(command.split(
                ' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = process.communicate()
        except FileNotFoundError:
            stderr = f'Command not found: {command}'
        embed = discord.Embed(
            title="Command output"
        )
        if len(result) >= 1 and result[0] in [None, b'']:
            stdout = 'No output.'
        if len(result) >= 2 and result[0] in [None, b'']:
            stderr = 'No output.'
        if len(result) >= 1 and result[0] not in [None, b'']:
            stdout = result[0].decode('utf-8')
        if len(result) >= 2 and result[1] not in [None, b'']:
            stderr = result[1].decode('utf-8')
        string = ""
        if len(result) >= 1:
            if (len(result[0]) >= 1024):
                stdout = result[0].decode('utf-8')
                string = string + f'[[STDOUT]]\n{stdout}'
                link = await self.online.hastebin(string)
                await msg.edit(
                    content=f":x: Content too long. {link}",
                    embed=None)
                return
        if len(result) >= 2:
            if (len(result[1]) >= 1024):
                stdout = result[0].decode('utf-8')
                string = string + f'[[STDERR]]\n{stdout}'
                link = await self.online.hastebin(string)
                await msg.edit(
                    content=f":x: Content too long. {link}",
                    embed=None)
                return
        embed.add_field(
            name="stdout",
            value=f'```{stdout}```' if 'stdout' in locals() else 'No output.',
            inline=False)
        embed.add_field(
            name="stderr",
            value=f'```{stderr}```' if 'stderr' in locals() else 'No output.',
            inline=False)
        await msg.edit(content='', embed=embed)

    @commands.group(aliases=['extensions', 'ext'], 
                    invoke_without_command=True)
    @checks.is_bot_owner()
    async def extend(self, ctx, name:str = None):
        """Provides status of extensions and lets you hotswap extensions."""

        # Provides status of extension
        if name is not None:
            status = "is" if name in self.extensions_list else "is not"
            msg = f"**{name}** {status} currently loaded and/or existent."

        # Handles empty calls
        else:
            msg = (
                "**Nothing was provided!**\n\n"
                "Please provide an extension name for status, "
                "or provide a subcommand."
            )

        # Sends completed message
        await ctx.send(msg)

    @extend.command(aliases=['le', 'l'])
    @checks.is_bot_owner()
    async def load(self, ctx, name: str):
        """Load an extension into the bot."""
        m = await ctx.send(f'Loading {name}')
        extension_name = f'extensions.{name}'
        if extension_name not in self.extensions_list:
            try:
                self.bot.load_extension(extension_name)
                self.extensions_list.append(extension_name)
                await m.edit(content='Extension loaded.')
            except Exception as e:
                await m.edit(
                    content=f'Error while loading {name}\n`{type(e).__name__}: {e}`')
        else:
            await m.edit(content='Extension already loaded.')

    @extend.command(aliases=["ule", "ul"])
    @checks.is_bot_owner()
    async def unload(self, ctx, name: str):
        """Unload an extension from the bot."""

        m = await ctx.send(f'Unloading {name}')
        extension_name = f'extensions.{name}'
        if extension_name in self.extensions_list:
            self.bot.unload_extension(extension_name)
            self.extensions_list.remove(extension_name)
            await m.edit(content='Extension unloaded.')
        else:
            await m.edit(content='Extension not found or not loaded.')

    @extend.command(aliases=["rle", "rl"])
    @checks.is_bot_owner()
    async def reload(self, ctx, name: str):
        """Reload an extension of the bot."""

        m = await ctx.send(f'Reloading {name}')
        extension_name = f'extensions.{name}'
        if extension_name in self.extensions_list:
            self.bot.unload_extension(extension_name)
            try:
                self.bot.load_extension(extension_name)
                await m.edit(content='Extension reloaded.')
            except Exception as e:
                self.extensions_list.remove(extension_name)
                await m.edit(
                    content=f'Failed to reload extension\n`{type(e).__name__}: {e}`')
        else:
            await m.edit(content='Extension isn\'t loaded.')

    @extend.command(name='list')
    async def list_cmd(self, ctx):
        """Lists all extensions loaded by the bot."""

        # Message Construction
        msg = "**Loaded Extensions**\n\n"
        msg += '\n'.join(f'`{e}`' for e in self.extensions_list)
        msg += "\n\n_See the other subcommands of this command to manage them._"

        # Message Sending
        await ctx.send(msg)

    @commands.command(aliases=['exit', 'reboot'])
    @checks.is_bot_owner()
    async def restart(self, ctx):
        """Turns the bot off."""

        await ctx.send(":zzz: **Restarting...**")
        exit()

    @commands.command()
    @checks.is_bot_owner()
    async def leave(self, ctx):
        """Makes the bot leave the server this was called in."""
        
        if ctx.guild:
            await ctx.send(
                "\U0001F4A8 **Leaving server.** "
                "_If you want me back, add me or get an admin to._")
            await ctx.guild.leave()
        else:
            await ctx.send(
                "**Can't leave!** _This channel is not inside a guild._")

    async def cog_check(self, ctx):
        return checks.is_bot_owner()(ctx.command)


def setup(bot):
    bot.add_cog(Developer(bot))
