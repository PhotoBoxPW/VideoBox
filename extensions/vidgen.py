# -*- coding: utf-8 -*-

# videobox vidgen
# Functions that create movies.

'''VidGen File'''

import os
import owo
import uuid
import time
import typing
import discord
from discord.ext import commands
from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip, ColorClip, AudioFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx

class VidGen(commands.Cog):
    """Provides commands that generate videos."""

    def __init__(self, bot):
        self.bot = bot
        self.emoji = "🎞️"
        self.__cog_name__ = "Video Generation"

    async def _send_video(self, ctx, video, clips=[], spoiler=False, preset='superfast'):
        """Exports and sends the video to the context."""
        videoname = f"cache/{uuid.uuid4().hex}.mp4"

        start_time = time.time()

        file_name = f"{ctx.command.name}.mp4"
        if spoiler:
            file_name = "SPOILER_" + file_name

        # Create cache if it doesn't exist
        if not os.path.exists('./cache'):
            os.makedirs('./cache')

        status_message = await ctx.send(
            f"`📹` {ctx.author.mention}'s **`{ctx.command.name}`**: Rendering..."
        )
        # Write and send file
        async with ctx.typing():
            video.write_videofile(videoname, threads=4, preset=preset, verbose=False, logger=None)
            if os.path.getsize(videoname) > 1000000 * 8 and self.bot.config['owo_key']: # 8 MB
                await status_message.edit(
                    content=f"`📹` {ctx.author.mention}'s **`{ctx.command.name}`**: Uploading..."
                )
                uploaded_files = owo.upload_files(self.bot.config['owo_key'], videoname)
                await status_message.delete()
                await ctx.send(
                    f"`📹` Rendered **`{ctx.command.name}`** in {time.time() - start_time:.2f} seconds for {ctx.author.mention}!" +
                    f"\n`🔗` *{uploaded_files[videoname]}*"
                )
            else:
                await status_message.delete()
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
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.channel)
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

        await self._send_video(ctx, video, clips=[clip])

    @commands.command(aliases=['tbc','roundabout'])
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.channel)
    async def tobecontinued(self, ctx, url: typing.Optional[str] = None):
        """Test"""

        videodata = await self._download_video(ctx)
        if not videodata: return
        (file_path, spoiler) = videodata

        clip = VideoFileClip(file_path, target_resolution=[720, 1280])
        # I WAS going to get the last 10 seconds but nvm
        if clip.duration > 10:
            clip = clip.subclip(0, -clip.duration + 10)

        # Startup
        startup_sound = AudioFileClip("assets/tobecontinued/roundabout_start.mp3")
        startup = ColorClip([1, 1], color=0)\
            .set_opacity(0)\
            .set_duration(startup_sound.duration).set_audio(startup_sound)
        if startup_sound.duration > clip.duration:
            startup = startup.subclip(startup_sound.duration - clip.duration, startup_sound.duration)
        else:
            startup = startup.fx(vfx.freeze, freeze_duration=clip.duration - startup_sound.duration)
        startup_compos = CompositeVideoClip([clip, startup])

        # Freeze fram stuff
        freeze_frame_sound = AudioFileClip("assets/tobecontinued/roundabout.mp3")
        freeze_frame = ImageClip(clip.get_frame(clip.duration))\
            .fx(vfx.blackwhite).set_duration(freeze_frame_sound.duration)
        arrow = ImageClip("assets/tobecontinued/arrow.png")\
            .set_pos( lambda t: (min(529, int((1400*t)-400)), 550) )
        freeze_compos = CompositeVideoClip([freeze_frame, arrow])\
            .set_duration(freeze_frame_sound.duration).set_audio(freeze_frame_sound)
        
        # Final clip
        final_clip = concatenate_videoclips([startup_compos, freeze_compos])

        await self._send_video(ctx, final_clip,
            clips=[clip, freeze_frame_sound, freeze_frame, arrow, freeze_compos, startup, startup_sound, startup_compos])
        os.remove(file_path)

    async def cog_check(self, ctx):
        if ctx.guild and ctx.guild.me.permissions_in(ctx.channel).attach_files == False:
            await ctx.send('`📟` I need to be able to attach files in order to do any video generation!')
            return False
        if ctx.author.id in ctx.bot.config.get('owners'):
            ctx.command.reset_cooldown(ctx)
            return True
        else:
            return True


def setup(bot):
    bot.add_cog(VidGen(bot))
