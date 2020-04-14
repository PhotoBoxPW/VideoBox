# -*- coding: utf-8 -*-

# videobox vidgen
# Commands that create movies.

'''VidGen File'''

import os
import owo
import uuid
import time
import typing
import discord
from discord.ext import commands
from extensions.models.videocog import VideoCog
from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip
import moviepy.video.fx.all as vfx

class VidGen(VideoCog):
    """Provides commands that generate videos."""

    def __init__(self, bot):
        self.bot = bot
        self.emoji = "🎞️"
        self.__cog_name__ = "Video Generation"

    @commands.command(aliases=['crab', '🦀'])
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.channel)
    async def crabrave(self, ctx, top_text: str, bottom_text: str):
        """
        Make some crabs rave to something.
        
        Command from [Dank Memer](https://github.com/DankMemer) by Melmsie
        """

        if len(top_text) == 0 or len(bottom_text) == 0:
            return await ctx.send('Strings can\'t be empty!')

        @self.bot.utils.force_async
        def process_clip():
            clip = VideoFileClip("assets/crabrave.mp4")
            text = TextClip(
                self._trunc(top_text).upper(), fontsize=48, color='white', font='Symbola'
            ).set_position(("center", 200)).set_duration(15.4)
            text2 = TextClip("____________________", fontsize=48, color='white', font='Verdana')\
                .set_position(("center", 210)).set_duration(15.4)
            text3 = TextClip(
                self._trunc(bottom_text).upper(), fontsize=48, color='white', font='Verdana'
            ).set_position(("center", 270)).set_duration(15.4)

            video = CompositeVideoClip([clip, text.crossfadein(1), text2.crossfadein(1), text3.crossfadein(1)]).set_duration(15.4)
            return video, [text, text2, text3, clip]

        final_clip, clips = await process_clip()
        await self._send_video(ctx, final_clip, clips=clips)

    @commands.command(aliases=['theboyslaugh'])
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.channel)
    async def theboys(self, ctx, url_or_flag: typing.Optional[str] = None):
        """The boys laugh at a picture."""

        photodata = await self._download_photo(ctx, url_or_flag)
        if not photodata: return
        (file_path, spoiler) = photodata

        @self.bot.utils.force_async
        def process_clip():
            clip = VideoFileClip("assets/theboys.mp4")
            picture = ImageClip(file_path, duration=clip.duration)\
                .fx(vfx.resize, newsize=[893, 288])\
                .set_pos( lambda t: (192, 432) )
            final_clip = CompositeVideoClip([clip, picture])

            return final_clip, [clip, picture]

        final_clip, clips = await process_clip()
        await self._send_video(ctx, final_clip, clips=clips, spoiler=spoiler)
        os.remove(file_path)

def setup(bot):
    bot.add_cog(VidGen(bot))
