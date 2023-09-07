import random
import datetime
import discord
from discord.ext import tasks, commands
from redbot.core import Config

from .custom_markov import POSifiedText
from .templates import gen_paulo, gen_gru, gen_komix, gen_demot
from .cleaners import polish_remover, links_remover, emoji_remover, empty_lines_remover


class MarkovGen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = 0
        ### List of channels ids where it's allowed to generate memes
        self.allowed_channels = []

        # Set the working directory (change as needed)
        self.workdir = './sources'
        self.load_data()

        # List of channels where bot will look for images to make memes with (use !refresh_images after loading for the first time)
        self.images_sources = []

        # List of channels where bot will look for text to make markov chains with (use !refresh_messages after loading for the first time)
        self.messages_sources = []

        # Path to templates (change as needed)
        self.templates_path = "./templates/"

        # Start a background task using the my_task method
        self.my_task.start()
        
        
        #PARAMETERS - max_chars/min_words/max_words
        self.duszenie = (200, 10, 50)
        self.demot = (60, 3, 10)
        self.paulo = (100, 4, 15)
        self.gru = (80, 6, 15)
        self.komix = (25, 2, 6)

    # Load data from files
    def load_data(self):
        self.sentences = self.load_text_data("sentences.txt")
        self.model = POSifiedText(self.sentences)
        self.images = self.load_image_data("images.txt")

    # Load text data from a file
    def load_text_data(self, filename):
        try:
            with open(f"{self.workdir}{filename}", "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return ""

    # Load image data from a file
    def load_image_data(self, filename):
        try:
            with open(f"{self.workdir}{filename}", "r", encoding="utf-8") as file:
                return file.readlines()
        except FileNotFoundError:
            return []

    # Clean and refresh text data
    async def clean_and_refresh_data(self):
        await polish_remover(f"{self.workdir}sentences.txt")
        await links_remover(f"{self.workdir}sentences.txt")
        await emoji_remover(f"{self.workdir}sentences.txt")
        await empty_lines_remover(f"{self.workdir}sentences.txt")

    # Choose a random image
    async def choose_random_image(self):
        image_url = random.choice(self.images).strip()
        if image_url:
            return image_url

    # Generate a markov chain
    async def make_sentence(self, max_chars, min_words, max_words):
        new_sentence = None
        counter = 0
        while not new_sentence and counter < 1000:
            counter += 1
            new_sentence = self.model.make_short_sentence(max_chars=max_chars, min_words=min_words, max_words=max_words)
        return new_sentence


    async def cog_unload(self):
        self.my_task.cancel()

    # Define a command group called "pykpyk"
    @commands.group(name="pykpyk")
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    async def pykpyk(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            return

    # Define a subcommand called "duszenie" under "pykpyk"
    @pykpyk.command()
    async def duszenie(self, ctx: commands.Context):
        if ctx.channel.id in self.allowed_channels:
            max_chars, min_words, max_words = self.duszenie
            sentence = await self.make_sentence(max_chars, min_words, max_words)
            if sentence:
                await ctx.send(sentence)
            else:
                await ctx.send("Failed to generate")

    # Define a subcommand called "demot" under "pykpyk"
    @pykpyk.command()
    async def demot(self, ctx: commands.Context):
        if ctx.channel.id in self.allowed_channels:
            max_chars, min_words, max_words = self.demot
            image_url = await self.choose_random_image()
            sentences = []
            for _ in range(2):
                sentence = await self.make_sentence(max_chars, min_words, max_words)
                if sentence is None:
                    await ctx.send("Failed to generate")
                    return
                sentences.append(sentence)
            await gen_demot(self.templates_path, image_url, *sentences)
            file = discord.File(fp=f"{self.templates_path}demot_meme.png")
            await ctx.send(file=file)


    # Define a subcommand called "paulo" under "pykpyk"
    @pykpyk.command()
    async def paulo(self, ctx: commands.Context):
        if ctx.channel.id in self.allowed_channels:
            max_chars, min_words, max_words = self.paulo
            sentence = await self.make_sentence(max_chars, min_words, max_words)
            if sentence:
                await gen_paulo(self.templates_path, sentence)
                file = discord.File(fp=f"{self.templates_path}paulo_meme.jpg")
                await ctx.send(file=file)
            else:
                await ctx.send("Failed to generate")



    # Define a subcommand called "gru" under "pykpyk"
    @pykpyk.command()
    async def gru(self, ctx: commands.Context):
        if ctx.channel.id in self.allowed_channels:
            max_chars, min_words, max_words = self.gru
            sentence = await self.make_sentence(max_chars, min_words, max_words)
            if sentence:
                await gen_gru(self.templates_path, sentence)
                file = discord.File(fp=f"{self.templates_path}gru_meme.jpg")
                await ctx.send(file=file)
            else:
                await ctx.send("Failed to generate")


    # Define a subcommand called "komix" under "pykpyk"
    @pykpyk.command()
    async def komix(self, ctx: commands.Context):
        if ctx.channel.id in self.allowed_channels:
            max_chars, min_words, max_words = self.komix
            sentences = []
            for _ in range(4):
                sentence = await self.make_sentence(max_chars, min_words, max_words)
                if sentence is None:
                    await ctx.send("Failed to generate")
                    return
                sentences.append(sentence)
            await gen_komix(self.templates_path, *sentences)
            file = discord.File(fp=f"{self.templates_path}komix_meme.jpg")
            await ctx.send(file=file)


    @commands.is_owner()
    @pykpyk.command()
    async def change(self, ctx: commands.Context, name: str, max_chars: int, min_words: int, max_words: int):
        if ctx.channel.id in self.allowed_channels:
            if name == 'duszenie':
                self.duszenie = (max_chars, min_words, max_words)
                await ctx.send(f'Parameters for {name} have been changed')
            elif name == 'demot':
                self.demot = (max_chars, min_words, max_words)
                await ctx.send(f'Parameters for {name} have been changed')
            elif name == 'paulo':
                self.paulo = (max_chars, min_words, max_words)
                await ctx.send(f'Parameters for {name} have been changed')
            elif name == 'gru':
                self.gru = (max_chars, min_words, max_words)
                await ctx.send(f'Parameters for {name} have been changed')
            elif name == 'komix':
                self.komix = (max_chars, min_words, max_words)
                await ctx.send(f'Parameters for {name} have been changed')
            else:
                await ctx.send('Wrong meme template')




    # Regenerate a text file containing text data for markov models
    @commands.is_owner()
    @commands.command()
    async def refresh_messages(self, ctx: commands.Context):
        try:
            with open(f'{self.workdir}sentences.txt', 'w', encoding='utf-8'):
                pass
        except:
            pass
        await ctx.send('Deleted old data, getting new one...')
        if ctx.channel.id in self.allowed_channels:
            counter = 0
            for channel_id in self.messages_sources:
                channel = self.bot.get_channel(int(channel_id))
                if channel is None:
                    await ctx.send(f'Channel with ID {channel_id} not found.')
                    continue
                scrapped_messages = []

                async for message in channel.history(limit=None):
                    scrapped_messages.append(message.content)

                if scrapped_messages:
                    with open(f'{self.workdir}sentences.txt', 'a', encoding='utf-8') as file:
                        file.write('\n'.join(scrapped_messages))
                counter += len(scrapped_messages)

            await ctx.send(
                f'Successfully scraped {counter} messages and saved them to "sentences.txt".')
            await self.clean_and_refresh_data()

    # Regenerate a text file containing links to all images
    @commands.is_owner()
    @commands.command()
    async def refresh_images(self, ctx: commands.Context):
        try:
            with open(f'{self.workdir}images.txt', 'w', encoding='utf-8'):
                pass
        except:
            pass
        await ctx.send('Deleted old data, getting new one...')
        if ctx.channel.id in self.allowed_channels:
            counter = 0
            for channel_id in self.images_sources:
                channel = self.bot.get_channel(int(channel_id))
                if channel is None:
                    await ctx.send(f'Channel with ID {channel_id} not found.')
                    continue
                scrapped_urls = []

                async for message in channel.history(limit=None):
                    for attachment in message.attachments:
                        if attachment.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                            scrapped_urls.append(attachment.url)

                if scrapped_urls:
                    with open(f'{self.workdir}images.txt', 'a', encoding='utf-8') as file:
                        file.write('\n'.join(scrapped_urls))
                counter += len(scrapped_urls)

            await ctx.send(
                f'Successfully scraped {counter} messages and saved them to "images.txt".')

    # Define a listener for on_message events
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id in self.images_sources:
            for attachment in message.attachments:
                if attachment.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    with open(f'{self.workdir}images.txt', 'a', encoding='utf-8') as file:
                        file.write('\n' + attachment.url)
        if message.channel.id in self.messages_sources:
            if message.content:
                with open(f'{self.workdir}sentences.txt', 'a', encoding='utf-8') as file:
                    file.write('\n' + message.content)


        # Make funny sentence in specified channel every 25 messages 
        if message.channel.id == 692651905029242940:
            self.counter += 1
            if self.counter == 25:
                channel = self.bot.get_channel(692651905029242940)
                sentence = await self.make_sentence(200, 10, 50)
                await channel.send(sentence)
                self.counter = 0

    # Pin generated memes which got 7 or more users reacting to it
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == 1148259718096240701:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            unique_users = set()
            for reaction in message.reactions:
                async for user in reaction.users():
                    unique_users.add(user.id)

            if len(unique_users) >= 6 and message.author.bot:
                await message.pin()

    # Clean text files and update markov models with new data
    @tasks.loop(seconds=1800)
    async def my_task(self):
        if datetime.datetime.now().strftime("%a %H") == 'Wed 03':
            await self.clean_and_refresh_data()
            self.load_data()

    @my_task.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(MarkovGen(bot))