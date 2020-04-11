# -*- coding: utf-8 -*-

# videobox check util
# Provides various check functions.

'''Checks File'''

from discord.ext import commands


def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

def is_bot_owner():
    def predicate(ctx):
        return ctx.author.id in ctx.bot.config.get('owners')
    return commands.check(predicate)

def setup(bot):
    pass