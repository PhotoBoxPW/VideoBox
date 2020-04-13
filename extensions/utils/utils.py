# -*- coding: utf-8 -*-

# videobox \utils
# Provides utils for various things.

'''Utils File'''

import os
import re
import uuid
import asyncio
import discord
import filetype
import functools
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientTimeout, ServerTimeoutError

class FindMediaResponse():
    """The response to finding media in a Discord channel."""

    def __init__(self, bot, message, url, spoiler=False, skip_head=False):
        self.bot = bot
        self.message = message
        self.url = url
        self.spoiler = spoiler
        self.skip_head = skip_head

    def __repr__(self):
        attrs = [
            ('url', self.url),
            ('spoiler', self.spoiler),
            ('skip_head', self.skip_head),
        ]
        return '<%s %s>' % (self.__class__.__name__, ' '.join('%s=%r' % t for t in attrs))

class DownloadURLError(Exception):
    """Exception that is thrown when URL verification fails."""

    def __init__(self, error_type, error=None,
        mime=None, response=None):
        # types: badformat, timeout, badstatus
        self.type = error_type
        self.error = error
        self.mime = mime
        self.response = response
    
    def to_message(self):
        if self.type == 'badformat':
            return f"**`{self.mime}`** is an invalid file type for this command!"
        elif self.type == 'timeout':
            return f"The request for the URL took too long!"
        elif self.type == 'timeout':
            return f"*`{self.response.url}`* returns a **`{self.response.status}`** HTTP status code!"

class TwitterAuthException(Exception):
    """Exception that is thrown when Twitter credentials are invalid."""
    def __init__(self, response):
        self.response = response
        super().__init__(f"{response}")

class Utils():
    """Provides utils for various things."""

    def __init__(self, bot):
        self.bot = bot
        self.request = bot.request
        self.url_regex = r"https?://(-\.)?([^\s/?.#-]+\.?)+(/[^\s]*)?(?=|\|\|)"
        self.spoiler_regex = r"\|\|\s*?([^|]+)\s*?\|\|"

        self.VIDEO_FORMATS = [
            'video/mp4',
            'video/quicktime',
            'video/webm',
            'video/x-m4v',
            'video/mpeg',
            'video/x-matroska',
            'video/x-flv',
            'video/x-msvideo'
        ]

        self.PHOTO_FORMATS = [
            'image/png',
            'image/tiff',
            'image/jpeg',
            'image/webp',
            'image/gif'
        ]
    
    def _in_spoiler(self, message, text):
        spoiler_match = re.search(self.spoiler_regex, message.content)
        if spoiler_match:
            for spoil in spoiler_match.groups():
                if spoil.strip() == text.strip():
                    return True
        return False

    async def hastebin(self, string):
        """Posts a string to hastebin."""

        url = "https://hasteb.in/documents"
        data = string.encode('utf-8')
        async with self.request.post(url=url, data=data) as haste_response:
            haste_key = (await haste_response.json())['key']
            haste_url = f"http://hasteb.in/{haste_key}"
        return haste_url

    async def find_video(self, message, use_past=True):
        """Finds a video URL in the Discord channel and returns it."""

        # Attachments
        if len(message.attachments):
            return FindMediaResponse(
                self.bot, message, message.attachments[0].url,
                spoiler=message.attachments[0].is_spoiler(),
                skip_head=True
            )

        # URL in content
        url_match = re.search(self.url_regex, message.content)
        if url_match:
            target_url = url_match[0]
            converted_url = await self.bot.video_extractor.get_url(target_url)
            real_url = converted_url or target_url
            return FindMediaResponse(
                self.bot, message, real_url,
                spoiler=self._in_spoiler(message, target_url),
                skip_head=converted_url != None
            )

        if use_past:
            if message.channel.guild and message.channel.guild.me.permissions_in(message.channel).read_message_history == False:
                return
            message_limit = self.bot.config['past_message_limit'] or 10
            async for past_message in message.channel.history(limit=message_limit, before=message):
                result = await self.find_video(past_message, use_past=False)
                if result: return result

    async def find_photo(self, message, use_past=True):
        """Finds a photo URL in the Discord channel and returns it."""

        # Attachments
        if len(message.attachments):
            return FindMediaResponse(
                self.bot, message, message.attachments[0].url,
                spoiler=message.attachments[0].is_spoiler(),
                skip_head=True
            )

        # Embed
        if len(message.embeds):
            embed = message.embeds[0]
            url = None
            spoiler_url = ""
            if embed.url:
                spoiler_url = embed.url
            if embed.image:
                url = embed.image.url
            elif embed.thumbnail:
                url = embed.thumbnail.url
            if url:
                return FindMediaResponse(
                    self.bot, message, url,
                    spoiler=self._in_spoiler(message, spoiler_url),
                    skip_head=False
                )

        # URL in content
        url_match = re.search(self.url_regex, message.content)
        if url_match:
            target_url = url_match[0]
            converted_url = await self.bot.photo_extractor.get_url(target_url)
            spoiler_match = re.search(self.spoiler_regex, message.content)

            is_spoiler = False
            if spoiler_match:
                for spoil in spoiler_match.groups():
                    if spoil.strip() == target_url:
                        is_spoiler = True
                        break

            real_url = converted_url or target_url
            return FindMediaResponse(
                self.bot, message, real_url,
                spoiler=is_spoiler,
                skip_head=converted_url != None
            )

        if use_past:
            if message.channel.guild and message.channel.guild.me.permissions_in(message.channel).read_message_history == False:
                return
            message_limit = self.bot.config['past_message_limit'] or 10
            async for past_message in message.channel.history(limit=message_limit, before=message):
                result = await self.find_photo(past_message, use_past=False)
                if result: return result

    async def download_url(self, url, supported_formats=[], skip_head=False):
        """Verifies and downloads a url and returns the file path."""
        timeout_seconds = self.bot.config['request_timeout'] or 10
        timeout = ClientTimeout(total=timeout_seconds)
        try:
            # HEAD request
            if not skip_head:
                async with self.request.head(url, timeout=timeout) as head_response:
                    if not head_response.headers.get('content-type') in supported_formats:
                        raise DownloadURLError('badformat', response=head_response, mime=head_response.headers.get('content-type'))
                    if head_response.status < 200 or head_response.status >= 300:
                        raise DownloadURLError('badstatus', response=head_response)
            
            async with self.request.get(url, timeout=timeout) as response:
                if response.status < 200 or response.status >= 300:
                    raise DownloadURLError('badstatus', response=response)
                # Create cache if it doesn't exist
                if not os.path.exists('./cache'):
                    os.makedirs('./cache')

                # Read buffer
                buffer = await response.read()
                response.close()
                buffer_type = filetype.guess(buffer)
                if not buffer_type or not buffer_type.mime in supported_formats:
                    raise DownloadURLError('badformat', response=response, mime=buffer_type.mime)

                # Write file
                file_path = f"./cache/{uuid.uuid4().hex}.{buffer_type.extension}"
                file = open(file_path, 'wb')
                file.write(buffer)
                file.close()
                return file_path
        except ServerTimeoutError as error:
            raise DownloadURLError('timeout', error)

    def force_async(self, fn):
        """Forces sync functions to be async"""
        pool = ThreadPoolExecutor()
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            future = pool.submit(fn, *args, **kwargs)
            return asyncio.wrap_future(future)  # make it awaitable
        return wrapper

def setup(bot):
    bot.utils = Utils(bot)
