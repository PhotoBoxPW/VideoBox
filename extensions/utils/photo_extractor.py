# -*- coding: utf-8 -*-

# videobox photo url extractor util
# Gets the photo URL for various links

'''URLExtractor File'''

import re
import json
import base64
from bs4 import BeautifulSoup
from discord.ext import commands
from .utils import TwitterAuthException

class PhotoExtractor():
    """Provides a way to get photo URLs from various URLs."""

    def __init__(self, bot):
        self.bot = bot
        self.request = bot.request
        self.fake_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3924.0 Safari/537.36'

        self.extractors = [
            'extract_vine',
            'extract_twitch_clip',
            'extract_twitch_vod',
            'extract_twitter',
            'extract_imgur',
            'extract_instagram'
        ]

    async def get_url(self, url):
        """Gets a photo URL from a URL."""

        try:
            for extractor in self.extractors:
                result = await getattr(self, extractor)(url)
                if result != None: return result
            return None
        except Exception as e:
            print(e)
            return None

    def _to_json(self, obj):
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)

    async def _refresh_twitter(self):
        creds = self.bot.config['twitter']
        auth = base64.b64encode(f"{creds['consumer']}:{creds['secret']}".encode('ascii')).decode("utf-8")

        async with self.request.post(
            url = "https://api.twitter.com/oauth2/token",
            headers = {
                'Authorization': f"Basic {auth}",
                'Content-Type': "application/x-www-form-urlencoded"
            },
            data = 'grant_type=client_credentials'
        ) as response:
            if response.status == 403:
                raise TwitterAuthException(response)
            self.bot._twitter_token = (await response.json())['access_token']
            response.close()

    async def extract_vine(self, url):
        """Get the photo link to a Vine URL."""

        regex = r"^https?://(?:www\.)?vine\.co/(?:v|oembed)/(\w+)"
        match = re.match(regex, url)
        if(not match): return None

        async with self.request.get(
            url = f"https://archive.vine.co/posts/{match.groups()[0]}.json"
        ) as response:
            if response.status == 403:
                response.close()
                return None
            photo_url = (await response.json())['thumbnailUrl']
            response.close()
            return photo_url
    
    async def extract_twitch_clip(self, url):
        """Get the photo link to a Twitch Clip URL."""

        regex = r"^https?://(?:clips\.twitch\.tv/(?:embed\?.*?\bclip=|(?:[^/]+/)*)|(?:www\.)?twitch\.tv\/[^/]+/clip/)([a-zA-Z]+)"
        match = re.match(regex, url)
        if(not match): return None

        payload = [{
            'operationName': 'incrementClipViewCount',
            'variables': { 'input': { 'slug': match.groups()[0] } },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': '6b2f169f994f2b93ff68774f6928de66a1e8cdb70a42f4af3a5a1ecc68ee759b',
                },
            },
        }]

        async with self.request.post(
            url = "https://gql.twitch.tv/gql",
            headers = {
                'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
                'User-Agent': self.fake_user_agent
            },
            data = self._to_json(payload)
        ) as response:
            clip = (await response.json())[0]
            response.close()
            if clip['data']['updateClipViewCount'] == None: return None
            return f"https://clips-media-assets2.twitch.tv/AT-cm%7C{clip['data']['updateClipViewCount']['clip']['id']}-preview-480x272.jpg"

    async def extract_twitch_vod(self, url):
        """Get the photo link to a Twitch VOD."""

        regex = r"^https?://(?:www\.)?twitch\.tv/videos/(\d+)"
        match = re.match(regex, url)
        if(not match): return None

        async with self.request.get(
            url = f"https://api.twitch.tv/helix/videos?id={match.groups()[0]}",
            headers = {
                'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
                'User-Agent': self.fake_user_agent
            }
        ) as response:
            if response.status == 400:
                response.close()
                return None
            clip = (await response.json())[0]
            response.close()
            return clip['data'][0]['thumbnail_url'].replace('%{width}', '1430').replace('%{height}', '800')

    async def extract_twitter(self, url):
        """Get the photo link to a Twitter URL."""

        regex = r"^https?://twitter\.com/\w+/status/(\d{17,19})(?:/(?:video/(\d))?)?"
        match = re.match(regex, url)
        if(not match): return None
        if(not self.bot.config['twitter']): return None
        if(not self.bot.config['twitter']['secret'] or
            not self.bot.config['twitter']['consumer']): return None
        if(not self.bot._twitter_token): await self._refresh_twitter()

        async with self.request.get(
            url = f"https://api.twitter.com/1.1/statuses/show/{match.groups()[0]}.json",
            headers = {
                'Authorization': f"Bearer {self.bot._twitter_token}"
            },
        ) as response:
            if response.status == 404:
                response.close()
                return None
            elif response.status == 403:
                response.close()
                await self._refresh_twitter()
                return await self.extract_twitter(url)
            data = await response.json()
            response.close()
            if data['extended_entities'] and data['extended_entities']['media'] and len(data['extended_entities']['media']) > 0:
                mediaID = 0

                # Parse video ID
                if match.groups()[1] != None and match.groups()[1].isdigit():
                    matchDigit = int(match.groups()[1])
                    if len(data['extended_entities']['media']) > matchDigit - 1 and matchDigit != 0:
                        mediaID = matchDigit - 1

                return data['extended_entities']['media'][mediaID]['media_url_https']

    async def extract_imgur(self, url):
        """Get the photo link to an Imgur URL."""

        regex = r"^https?://(?:i\.)?imgur\.com/(?!(?:a|gallery|(?:t(?:opic)?|r)/[^/]+)/)([a-zA-Z0-9]+)"
        match = re.match(regex, url)
        if(not match): return None
        return f"https://i.imgur.com/{match.groups()[0]}.png"

    async def extract_instagram(self, url):
        """Get the photo link to an Instagram URL."""

        regex = r"^https?://(?:www\.)?instagram\.com/(?:p|tv)/(\w+)"
        match = re.match(regex, url)
        if(not match): return None
        async with self.request.get(url=url) as response:
            html = await response.text()
            response.close()
            if response.status == 404: return None
            soup = BeautifulSoup(await response.text(), features='lxml')
            if soup.select("body link + script"):
                data = json.loads(re.sub(r"(^window._sharedData = |;$)", '', soup.select("body link + script")[0].text))
                return data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['display_url']

def setup(bot):
    bot.photo_extractor = PhotoExtractor(bot)
    pass