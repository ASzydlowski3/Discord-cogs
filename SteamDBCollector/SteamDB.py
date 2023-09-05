from redbot.core import commands
import discord
from bs4 import BeautifulSoup
from zenrows import ZenRowsClient
import asyncio
import aiofiles
import os
import zipfile

class SteamDB(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.counter = 0
        # Replace "YOUR_ZENROWS_API_KEY" with your actual ZenRows API key
        self.client = ZenRowsClient("YOUR_ZENROWS_API_KEY")
        self.params = {"js_render": "true"}
        # Replace with your desired work directory
        self.work_directory = 'path/to/your/work/directory/'  
        self.allowed_channels = [] # Replace with allowed channels

    # Method to add game IDs to text files
    async def add_game_ids(self, game_ids: list[str]) -> None:
        if len(game_ids) == 1:
            async with aiofiles.open(f"{self.work_directory}{self.counter}.txt", 'w') as my_file:
                await my_file.write(f"{game_ids}")
                self.counter += 1
        else:
            for game_id in game_ids:
                async with aiofiles.open(f"{self.work_directory}{self.counter}.txt", 'w') as my_file:
                    await my_file.write(f"{game_id}")
                    self.counter += 1

    # Method to retrieve and process DLC IDs
    async def scalp_dlc_ids(self, ctx: commands.Context, game_ids: list[str]) -> None:
        for game_id in game_ids:
            await ctx.send(f'Searching for DLCs for {game_id}...')
            url = f"https://steamdb.info/app/{game_id}/dlc/"
            response = self.client.get(url, params=self.params)
            website = response.text
            soup = BeautifulSoup(website, "html.parser")
            try:
                dlcs = soup.find(id='dlc').find_all(class_='app')
            except AttributeError:
                await ctx.send(f'No DLCs found for {game_id}')
                continue
            dlcs = [dlc.attrs['data-appid'] for dlc in dlcs]
            for dlc in dlcs:
                async with aiofiles.open(f"{self.work_directory}{self.counter}.txt", 'w') as my_file:
                    await my_file.write(dlc)
                self.counter += 1

    # Method to create a ZIP archive of files
    async def zip_files(self) -> None:
        if os.path.exists(self.work_directory):
            with zipfile.ZipFile('AppList.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(self.work_directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.work_directory)
                        zipf.write(file_path, arcname=arcname)

    # Method to clean up generated files
    async def cleanup_files(self) -> None:
        for root, _, files in os.walk(self.work_directory):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)

    # Method to validate input game IDs
    async def check_input(self, ctx: commands.Context, game_ids: list[str]) -> bool:
        try:
            for game_id in game_ids:
                int(game_id)
        except ValueError:
            await ctx.send("Invalid format.")
            return False
        return True

    # Command to download and process game and DLC IDs
    @commands.command()
    async def game_data(self, ctx: commands.Context, *, game_ids: str):
        game_ids = game_ids.split(", ")
        if await self.check_input(ctx, game_ids):
            if ctx.channel.id in self.allowed_channels:  # Replace with the appropriate channel ID
                if not os.path.exists(self.work_directory):
                    os.makedirs(self.work_directory)

                await ctx.send("Should I also add games? (reply 'yes' if games are from family sharing)")

                def check(message: discord.Message) -> bool:
                    return message.author == ctx.author and message.channel == ctx.channel

                try:
                    response_message = await self.bot.wait_for("message", check=check, timeout=10)
                except asyncio.TimeoutError:
                    await ctx.send("No, then.")
                    return
                if response_message.content.lower() == 'yes':
                    await self.add_game_ids(game_ids)
                await self.scalp_dlc_ids(ctx, game_ids)
                await self.zip_files()
                with open('AppList.zip', 'rb') as zip_file:
                    zip_discord_file = discord.File(zip_file, filename='AppList.zip')
                    await ctx.send(file=zip_discord_file)
                await self.cleanup_files()
                self.counter = 0

def setup(bot: commands.Bot):
    bot.add_cog(SteamDB(bot))