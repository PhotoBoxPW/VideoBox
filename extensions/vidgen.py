# -*- coding: utf-8 -*-

# videobox vidgen
# Commands that create movies.

'''VidGen File'''

import os
import owo
import uuid
import time
import math
import typing
import ffmpeg
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
            return await ctx.send('`🛑` Strings can\'t be empty!')

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

    @commands.command(aliases=['thisvid2', 'thisvid3', 'dvid2', 'dv2', 'thisvid__3', 'thisvid_2'])
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.channel)
    async def discordvid2(self, ctx, url_or_flag: typing.Optional[str] = None):
        """It's DiscordVid2!"""

        videodata = await self._download_video(ctx)
        if not videodata: return
        (file_path, spoiler) = videodata

        probe = ffmpeg.probe(file_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if not video_stream:
            os.remove(file_path)
            return await ctx.send('`🛑` No video stream was found!')

        width = int(video_stream['width'])
        height = int(video_stream['height'])
        duration = float(video_stream['duration'])
        if duration > 30: duration = 30

        font_size = (math.sqrt(math.pow(width, 2) + math.pow(height, 2)) / 1468.6 * 72) * 0.6
        videobox_at = f"@{ctx.bot.user.name}#{ctx.bot.user.discriminator}"
        user_at = f"@{ctx.author.name}#{ctx.author.discriminator}"

        inputstream = ffmpeg.input(file_path)

        audio = (
            inputstream.audio
            .filter('volume', enable=f"between(t,0,{duration}/2)", volume=0.25)
            .filter('volume', enable=f"between(t,{duration}/2, {duration})", volume=5)
            .filter('atrim', duration=duration)
        )

        video = (
            inputstream.video
            .filter('scale', h=240, w=320)
            .filter('frei0r', 'pixeliz0r')
            .filter('setsar', sar=1)
            .filter('trim', duration=duration)
            .filter('drawtext',
                fontfile='\'./assets/discordvid2/DejaVuSans.ttf\'',
                text=videobox_at,
                fontcolor='white',
                fontsize=font_size,
                box='1',
                boxcolor='black@0.5',
                boxborderw='5',
                x='(w-text_w)',
                y='0'
            ).filter('drawtext',
                fontfile='\'./assets/discordvid2/DejaVuSans.ttf\'',
                text=user_at,
                fontcolor='white',
                fontsize=font_size,
                box='1',
                boxcolor='black@0.5',
                boxborderw='5',
                x='0',
                y='0'
            ).filter('drawtext',
                fontfile='\'./assets/discordvid2/DejaVuSans-Bold.ttf\'',
                text=f'Downloaded using {videobox_at}',
                fontcolor='white',
                fontsize=font_size,
                shadowcolor='black',
                shadowx='2',
                shadowy='2',
                x='(w-text_w)/2',
                y='(h-text_h)/2'
            ).filter('drawtext',
                fontfile='\'./assets/discordvid2/Topaz.ttf\'',
                text=f'This video was downloaded using {videobox_at}. Reuploads are prohibited via VideoBox guidelines. Visit https://github.com/Snazzah/VideoBox for more information.',
                fontcolor='white',
                fontsize=font_size,
                x='w-mod(max(t-4.5,0)*(w+tw)/7.5,(w+tw))',
                y='h-line_h-10'
            )
        )

        outro = ffmpeg.input('./assets/discordvid2/outro.mp4')
        final = ffmpeg.concat(video, audio, outro.video, outro.audio, v=1, a=1).node
        await self._send_ffmpeg_stream(ctx, video=final[0], audio=final[1],
            args={'r':5, 'ac':1, 'ar':'8k', 'video_bitrate':'150k'}, spoiler=spoiler)

        os.remove(file_path)

def setup(bot):
    bot.add_cog(VidGen(bot))
