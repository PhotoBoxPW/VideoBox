# -*- coding: utf-8 -*-

# videobox getters
# Commands that get photo/video URLs.

'''Getters File'''

import typing
import discord
from discord.ext import commands

class Getters(commands.Cog):
    """Provides commands that generate videos."""

    def __init__(self, bot):
        self.bot = bot
        self.emoji = "🔗"
        self.__cog_name__ = "URL Getters"

    @commands.command(name='getvideourl', aliases=['getvideo'])
    @commands.cooldown(rate=3, per=10)
    async def get_video(self, ctx, url: typing.Optional[str] = None):
        """Get the MP4 URL from a link."""

        media = await self.bot.utils.find_video(ctx.message)
        if not media:
            await ctx.send('`🛑` Could not find media to get!')
            return None
        
        await ctx.send(
            f"`🔗` {ctx.author.mention}: <{media.url}>"
        )

    @commands.command(name='getphotourl', aliases=['getphoto', 'getpictureurl', 'getpicture', 'getpicurl', 'getpic'])
    @commands.cooldown(rate=3, per=10)
    async def get_photo(self, ctx, url_or_flag: typing.Optional[str] = None):
        """Get the photo URL from a link."""

        media = await self.bot.utils.find_photo(ctx.message, url_or_flag)
        if not media:
            await ctx.send('`🛑` Could not find media to get!')
            return None
        
        await ctx.send(
            f"`🔗` {ctx.author.mention}: <{media.url}>"
        )

    async def cog_check(self, ctx):
        if ctx.author.id in ctx.bot.config.get('owners'):
            ctx.command.reset_cooldown(ctx)
            return True
        else:
            return True


def setup(bot):
    bot.add_cog(Getters(bot))
