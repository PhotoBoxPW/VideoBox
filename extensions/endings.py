# -*- coding: utf-8 -*-

# videobox endings
# Functions that create movies with endings.

'''Endings File'''

import os
import typing
from discord.ext import commands
from extensions.models.videocog import VideoCog
from moviepy.editor import VideoFileClip, TextClip, ImageClip, CompositeVideoClip, ColorClip, AudioFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx

class Endings(VideoCog):
    """Provides commands that generate endings for videos."""

    def __init__(self, bot):
        self.bot = bot
        self.emoji = "🔚"
        self.__cog_name__ = "Endings"

    @commands.command(aliases=['tbc','roundabout'])
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.channel)
    async def tobecontinued(self, ctx, url: typing.Optional[str] = None):
        """What's gonna happen next?"""

        videodata = await self._download_video(ctx)
        if not videodata: return
        (file_path, spoiler) = videodata

        if not self.check_processes():
            os.remove(file_path)
            return await ctx.send('`🛑` Too many videos are processing at the moment! Try again later!')

        self.bot.videos_processing += 1

        @self.bot.utils.force_async
        def process_clip():
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

            return final_clip, [clip, freeze_frame_sound, freeze_frame, arrow, freeze_compos, startup, startup_sound, startup_compos]

        final_clip, clips = await process_clip()
        await self._send_video(ctx, final_clip, clips=clips, spoiler=spoiler)
        os.remove(file_path)
        self.bot.videos_processing -= 1

    @commands.command(aliases=['wbrb','ericandre'])
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.channel)
    async def wellberightback(self, ctx, url: typing.Optional[str] = None):
        """Commercial break!"""

        videodata = await self._download_video(ctx)
        if not videodata: return
        (file_path, spoiler) = videodata

        if not self.check_processes():
            os.remove(file_path)
            return await ctx.send('`🛑` Too many videos are processing at the moment! Try again later!')

        self.bot.videos_processing += 1

        @self.bot.utils.force_async
        def process_clip():
            clip = VideoFileClip(file_path, target_resolution=[720, 1280])
            # I WAS going to get the last 10 seconds but nvm
            if clip.duration > 10:
                clip = clip.subclip(0, -clip.duration + 10)

            # Freeze fram stuff
            freeze_frame_sound = AudioFileClip("assets/wellberightback/sound.mp3")
            freeze_frame = ImageClip(clip.get_frame(clip.duration))\
                .fx(vfx.painting, black=0.001)\
                .fx(vfx.colorx, factor=0.8).set_duration(freeze_frame_sound.duration)
            text = ImageClip("assets/wellberightback/text.png")\
                .set_pos( lambda t: (50, 50) )
            freeze_compos = CompositeVideoClip([freeze_frame, text])\
                .set_duration(freeze_frame_sound.duration).set_audio(freeze_frame_sound)

            # Final clip
            final_clip = concatenate_videoclips([clip, freeze_compos])

            return final_clip, [clip, freeze_frame_sound, freeze_frame, text, freeze_compos]

        final_clip, clips = await process_clip()
        await self._send_video(ctx, final_clip, clips=clips, spoiler=spoiler)
        os.remove(file_path)
        self.bot.videos_processing -= 1

    @commands.command(aliases=['fnaf'])
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.channel)
    async def fnafjumpscare(self, ctx, url: typing.Optional[str] = None):
        """Give em' a scare!"""

        videodata = await self._download_video(ctx)
        if not videodata: return
        (file_path, spoiler) = videodata

        if not self.check_processes():
            os.remove(file_path)
            return await ctx.send('`🛑` Too many videos are processing at the moment! Try again later!')

        self.bot.videos_processing += 1

        @self.bot.utils.force_async
        def process_clip():
            clip = VideoFileClip(file_path, target_resolution=[720, 1280])
            # I WAS going to get the last 10 seconds but nvm
            if clip.duration > 10:
                clip = clip.subclip(0, -clip.duration + 10)

            # Freeze fram stuff
            sound = AudioFileClip("assets/fnafjumpscare/sound.mp3")
            gif = VideoFileClip("assets/fnafjumpscare/scare.gif", target_resolution=[720, 1280])\
                .fx(vfx.mask_color, color=[255,255,255]).set_duration(sound.duration)
            freeze_frame = ImageClip(clip.get_frame(clip.duration))\
                .set_duration(sound.duration)
            freeze_compos = CompositeVideoClip([freeze_frame, gif])\
                .set_duration(sound.duration).set_audio(sound)

            # Final clip
            final_clip = concatenate_videoclips([clip, freeze_compos])

            return final_clip, [clip, sound, freeze_frame, gif, freeze_compos]

        final_clip, clips = await process_clip()
        await self._send_video(ctx, final_clip, clips=clips, spoiler=spoiler)
        os.remove(file_path)
        self.bot.videos_processing -= 1

def setup(bot):
    bot.add_cog(Endings(bot))