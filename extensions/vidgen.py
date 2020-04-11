# -*- coding: utf-8 -*-

# videobox vidgen
# Functions that create movies.

'''VidGen File'''

import os
import uuid
import time
import discord
from discord.ext import commands
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


class VidGen(commands.Cog):
    """Provides commands that generate videos."""

    def __init__(self, bot):
        self.bot = bot
        self.emoji = "🎞️"
        self.__cog_name__ = "Video Generation"

    async def _send_video(self, ctx, video, *clips):
        """Exports and sends the video to the context."""
        videoname = f"cache/{uuid.uuid4().hex}.mp4"

        start_time = time.time()

        # Create cache if it doesn't exist
        if not os.path.exists('./cache'):
            os.makedirs('./cache')

        # Write and send file
        async with ctx.typing():
            video.write_videofile(videoname, threads=4, preset='superfast', verbose=False)
            await ctx.send(
                f"`📹` Rendered **`{ctx.command.name}`** in {time.time() - start_time:.2f} seconds for {ctx.author.mention}!",
                file = discord.File(fp=videoname, filename=f"{ctx.command.name}.mp4")
            )

        # Cleanup
        for clip in clips:
            clip.close()
        video.close()
        os.remove(videoname)

    @commands.command(aliases=['crab', '🦀'])
    async def crabrave(self, ctx, top_text: str, bottom_text: str):
        """
        Make some crabs rave to something.
        
        Command from [Dank Memer](https://github.com/DankMemer) by Melmsie
        """

        if len(top_text) == 0 or len(bottom_text) == 0:
            return await ctx.send('Strings can\'t be empty!')
        
        ctx.trigger_typing()

        name = uuid.uuid4().hex + '.mp4'
        clip = VideoFileClip("assets/crabrave.mp4")
        text = TextClip(top_text.upper(), fontsize=48, color='white', font='Symbola')
        text2 = TextClip("____________________", fontsize=48, color='white', font='Verdana')\
            .set_position(("center", 210)).set_duration(15.4)
        text = text.set_position(("center", 200)).set_duration(15.4)
        text3 = TextClip(bottom_text.upper(), fontsize=48, color='white', font='Verdana')\
            .set_position(("center", 270)).set_duration(15.4)

        video = CompositeVideoClip([clip, text.crossfadein(1), text2.crossfadein(1), text3.crossfadein(1)]).set_duration(15.4)

        await self._send_video(ctx, video, clip)

    async def cog_check(self, ctx):
        return commands.cooldown(rate=1, per=60, type=commands.BucketType.channel)\
            (commands.bot_has_guild_permissions(attach_files=True)(ctx.command))


def setup(bot):
    bot.add_cog(VidGen(bot))
