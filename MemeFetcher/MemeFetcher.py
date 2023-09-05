from redbot.core import commands
import aiohttp
import json
import discord
from bs4 import BeautifulSoup
import random
from typing import Optional

class MemeFetcher(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_url = 'https://meme-api.com/gimme'
        self.memetypes = ['me_irl', 'dankmemes', 'memes', 'demot', 'kwejk']
        self.allowed_channels = []

    async def fetch_url(self, url: str) -> str:
        # Function to fetch content from a given URL
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    async def fetch_image(self, url: str) -> Optional[bytes]:
        # Function to fetch image data from a given URL
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    return None

    @commands.command()
    async def get_meme(self, ctx: commands.Context, memetype: Optional[str] = None):
        if ctx.channel.id in self.allowed_channels:
            if memetype not in self.memetypes and memetype is not None:
                # Check if the specified meme type is allowed
                await ctx.send(f"Sorry, that meme type isn't available. Allowed meme types: 'memes', 'dankmemes', 'me_irl', 'demot'")
                return
            elif memetype is None:
                # If no meme type specified, choose a random one from the list
                memetype = random.choice(self.memetypes)

        if memetype in ('me_irl', 'dankmemes', 'memes'):
            # Fetch a meme using the meme API
            self.api_url = f'https://meme-api.com/gimme/{memetype}'
            response_text = await self.fetch_url(self.api_url)
            data_dict = json.loads(response_text)
            image_url = data_dict['url']
            image_data = await self.fetch_image(image_url)

        if memetype == 'demot':
            # Fetch a demotivational image from demotywatory.pl
            demoty_website = await self.fetch_url('https://demotywatory.pl/losuj')
            soup = BeautifulSoup(demoty_website, "html.parser")
            image_url = soup.find(class_='picwrapper').find(class_='demot').attrs['src']
            image_data = await self.fetch_image(image_url)

        if memetype == 'kwejk':
            # Fetch a meme from kwejk.pl, memy.pl, or jbzd.com.pl
            source = random.choice(('kwejk', 'memy', 'jbzd'))
            try:
                if source == 'kwejk':
                    # Fetch a meme from kwejk.pl
                    page = random.randrange(1, 41)
                    url = f'https://kwejk.pl/top/tydzien/strona/{page}'
                    website = await self.fetch_url(url)
                    soup = BeautifulSoup(website, "html.parser")
                    kwejk_urls = soup.find_all(class_='media-element')
                    kwejk_urls = [kwejk.attrs['data-image'] for kwejk in kwejk_urls]
                    image_url = random.choice(kwejk_urls)
                    image_data = await self.fetch_image(image_url)
                elif source == 'memy':
                    # Fetch a meme from memy.pl
                    url = 'https://memy.pl/losuj'
                    website = await self.fetch_url(url)
                    soup = BeautifulSoup(website, "html.parser")
                    image_url = soup.find(class_='img-responsive').find(name="img").attrs['src']
                    image_data = await self.fetch_image(image_url)
                elif source == 'jbzd':
                    # Fetch a meme from jbzd.com.pl
                    url = 'https://jbzd.com.pl/losowe'
                    image_url = None
                    while image_url is None:
                        website = await self.fetch_url(url)
                        soup = BeautifulSoup(website, "html.parser")
                        try:
                            image_url = soup.find(class_='article-image').find(name="img").attrs['src']
                        except AttributeError:
                            continue
                    image_data = await self.fetch_image(image_url)
            except AttributeError:
                await ctx.send("Something went wrong. Please try again.")
                return

        if image_data:
            # Save and send the fetched meme image
            with open('downloaded_meme.png', 'wb') as file:
                file.write(image_data)
            file = discord.File(fp='downloaded_meme.png')
            await ctx.send(file=file)

def setup(bot: commands.Bot):
    bot.add_cog(MemeFetcher(bot))