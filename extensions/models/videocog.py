# -*- coding: utf-8 -*-

# videobox videocog
# Functions that create movies.

'''VideoCog File'''

import os
import owo
import uuid
import time
import ffmpeg
import discord
from discord.ext import commands

class VideoCog(commands.Cog):
    async def _send_video(self, ctx, video, clips=[], spoiler=False, preset='ultrafast', threads=4):
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
            async_write = self.bot.utils.force_async(video.write_videofile)
            await async_write(videoname, threads=threads, preset=preset, verbose=False, logger=None)
            if os.path.getsize(videoname) > 1000000 * 8 and self.bot.config['owo_key']: # 8 MB
                await status_message.edit(
                    content=f"`📹` {ctx.author.mention}'s **`{ctx.command.name}`**: Uploading..."
                )
                async_upload = self.bot.utils.force_async(owo.upload_files)
                uploaded_files = await async_upload(self.bot.config['owo_key'], videoname)
                await status_message.delete()
                await ctx.send(
                    f"`📹` Rendered **`{ctx.command.name}`** in {time.time() - start_time:.2f} seconds for {ctx.author.mention}!" +
                    f"\n`🔗` {'||' if spoiler else ''}https://videobox.is-pretty.cool/{uploaded_files[videoname].split('/')[3]}{'||' if spoiler else ''}"
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

    async def _send_ffmpeg_stream(self, ctx, video, audio, args={}, spoiler=False):
        """Runs the FFmpeg stream and sends the video to the context."""
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
        # Run and send file
        async with ctx.typing():
            stream = ffmpeg.output(video, audio, videoname, **args)
            async_run = self.bot.utils.force_async(stream.run)
            await async_run(quiet=True)
            if os.path.getsize(videoname) > 1000000 * 8 and self.bot.config['owo_key']: # 8 MB
                await status_message.edit(
                    content=f"`📹` {ctx.author.mention}'s **`{ctx.command.name}`**: Uploading..."
                )
                async_upload = self.bot.utils.force_async(owo.upload_files)
                uploaded_files = await async_upload(self.bot.config['owo_key'], videoname)
                await status_message.delete()
                await ctx.send(
                    f"`📹` Rendered **`{ctx.command.name}`** in {time.time() - start_time:.2f} seconds for {ctx.author.mention}!" +
                    f"\n`🔗` {'||' if spoiler else ''}https://videobox.is-pretty.cool/{uploaded_files[videoname].split('/')[3]}{'||' if spoiler else ''}"
                )
            else:
                await status_message.delete()
                await ctx.send(
                    f"`📹` Rendered **`{ctx.command.name}`** in {time.time() - start_time:.2f} seconds for {ctx.author.mention}!",
                    file = discord.File(fp=videoname, filename=file_name)
                )

        # Cleanup
        os.remove(videoname)

    def _trunc(self, text: str, limit: int = 20) -> str:
        if len(text) <= limit:
            return text
        else:
            return text[limit:] + '...'

    def check_processes(self):
        return self.bot.videos_processing <= 10

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

    async def _download_photo(self, ctx, arg=''):
        media = await self.bot.utils.find_photo(ctx.message, arg)
        if not media:
            await ctx.send('`🛑` Could not find media to use!')
            return None
        try:
            file_path = await self.bot.utils.download_url(
                media.url, supported_formats=self.bot.utils.PHOTO_FORMATS, skip_head=media.skip_head)
        except Exception as error:
            if type(error).__name__ == 'DownloadURLError':
                await ctx.send(f'`🛑` {error.to_message()}')
            return None
        return file_path, media.spoiler

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
    pass
