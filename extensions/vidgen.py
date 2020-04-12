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

    async def _send_video(self, ctx, video, *clips, spoiler=False):
        """Exports and sends the video to the context."""
        videoname = f"cache/{uuid.uuid4().hex}.mp4"

        start_time = time.time()

        file_name = f"{ctx.command.name}.mp4"
        if spoiler:
            file_name = "SPOILER_" + file_name

        # Create cache if it doesn't exist
        if not os.path.exists('./cache'):
            os.makedirs('./cache')

        # Write and send file
        async with ctx.typing():
            video.write_videofile(videoname, threads=4, preset='superfast', verbose=False, logger=None)
            await ctx.send(
                f"`📹` Rendered **`{ctx.command.name}`** in {time.time() - start_time:.2f} seconds for {ctx.author.mention}!",
                file = discord.File(fp=videoname, filename=file_name)
            )

        # Cleanup
        for clip in clips:
            clip.close()
        video.close()
        os.remove(videoname)
    
    def _trunc(self, text: str, limit: int = 20) -> str:
        if len(text) <= limit:
            return text
        else:
            return text[limit:] + '...'

    async def _download_video(self, ctx):
        media = await self.bot.utils.find_video(ctx.message)
        if not media:
            await ctx.send('`🛑` Could not find media to use!')
            return None
        try:
            file_path = await self.bot.utils.download_url(
                media.url, supported_formats=self.bot.utils.VIDEO_FORMATS, skip_head=media.skip_head)
        except Exception as error:
            if type(error).__name__ == 'DownloadURLError':
                await ctx.send(f'`🛑` {error.to_message()}')
            return None
        return file_path, media.spoiler

    @commands.command(aliases=['crab', '🦀'])
    async def crabrave(self, ctx, top_text: str, bottom_text: str):
        """
        Make some crabs rave to something.
        
        Command from [Dank Memer](https://github.com/DankMemer) by Melmsie
        """

        if len(top_text) == 0 or len(bottom_text) == 0:
            return await ctx.send('Strings can\'t be empty!')

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

        await self._send_video(ctx, video, clip)

    async def cog_check(self, ctx):
        return commands.cooldown(rate=1, per=60, type=commands.BucketType.channel)\
            (commands.bot_has_guild_permissions(attach_files=True)(ctx.command))


def setup(bot):
    bot.add_cog(VidGen(bot))
