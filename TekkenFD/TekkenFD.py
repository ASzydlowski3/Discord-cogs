import discord
from redbot.core import Config, commands
import asyncio

import os
from bs4 import BeautifulSoup
import aiohttp
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, relationship
from fuzzywuzzy import process, fuzz


class TekkenFD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_character = None
        self.last_message = None
        self.other_options_ids = None
        self.allowed_channels = [1003996397739188294, 692661446991151165]
        self.engine = create_engine('sqlite:///home/frizen/framedata.db', echo=True)

    class Base(DeclarativeBase):
        pass

    class Character(Base):
        __tablename__ = 'character'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        moves = relationship("Move", back_populates="character")
        link = Column(String)
        thumbnail = Column(String)

    class Move(Base):
        __tablename__ = 'move'
        id = Column(Integer, primary_key=True)
        character_id = Column(Integer, ForeignKey('character.id'))
        character = relationship("Character", back_populates="moves")
        Command = Column(String)
        HitLevel = Column(String)
        Damage = Column(String)
        StartUpFrame = Column(String)
        BlockFrame = Column(String)
        HitFrame = Column(String)
        CounterHitFrame = Column(String)
        Notes = Column(String)

    engine = create_engine('sqlite:///home/frizen/framedata.db', echo=True)
    Base.metadata.create_all(engine)

    async def fetch_url(self, url):
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url) as response:
                return await response.text(encoding='ISO-8859-1')

    async def get_links(self):
        data = await self.fetch_url('https://rbnorway.org/t7-frame-data/')
        soup = BeautifulSoup(data, "html.parser")
        links = soup.find_all("div", class_="make-column-clickable-elementor")
        links = [char.attrs['data-column-clickable'] for char in links]
        image_links = soup.findAll("img", {"src": lambda L: L and L.startswith('https://rbnorway.org/wp-content/uploads/elementor/thumbs/')})
        image_links = [char.attrs['src'] for char in image_links]
        return links, image_links

    async def add_characters_to_db(self, session, link, image_link):
        name = link.split('/')[3].split('-')[0].capitalize()
        new_character = self.Character(
            name=name,
            link=link,
            thumbnail=image_link
        )
        session.add_all([new_character])
        session.commit()

    async def add_moves_to_db(self, session, moves, char_id):
        move_objects = []

        for move in moves:
            move = move.find_all('td')
            move = [prop.text for prop in move]
            if len(move) == 8:
                new_move = self.Move(
                    Command=move[0].replace(" or ", "_"),
                    character_id=char_id,
                    HitLevel=move[1],
                    Damage=move[2],
                    StartUpFrame=move[3],
                    BlockFrame=move[4],
                    HitFrame=move[5],
                    CounterHitFrame=move[6],
                    Notes=move[7]
                )
                move_objects.append(new_move)

        if move_objects:
            session.add_all(move_objects)
            session.commit()

    async def fetch_moves(self, link):
        moves = []
        data = await self.fetch_url(link)
        soup = BeautifulSoup(data, "html.parser")
        tables = soup.find_all('table')
        for table in tables:
            for move in table.find_all('tr')[1:]:
                moves.append(move)
        return moves

    async def get_list_of_moves(self, session, char_name):
        character = session.query(self.Character).filter(self.Character.name == char_name).first()
        movelist = [move.Command for move in character.moves]
        return movelist

    async def find_character(self, session, char_name):
        characters = session.query(self.Character).all()
        character_names = [character.name for character in characters]
        found_character = process.extractOne(char_name, character_names)
        return found_character[0]

    async def get_move_id(self, movelist, searched_move):
        best_match = 0
        move_id = None

        for count, move in enumerate(movelist):
            move_match = fuzz.ratio(searched_move, move)

            if move_match > best_match:
                best_match = move_match
                move_id = count
        return move_id

    async def get_move_by_id(self, session, move_id, char_name):
        character = session.query(self.Character).filter(self.Character.name == char_name).first()
        move = character.moves[move_id]
        return move

    async def get_best_matches(self, movelist, searched_move):
        results_list = []
        checked_moves = []
        for move in movelist:
            if move in checked_moves:
                continue
            move_match = fuzz.ratio(searched_move, move)
            results_list.append(move_match)
            checked_moves.append(move)

        indexed_list = list(enumerate(results_list))
        sorted_list = sorted(indexed_list, key=lambda x: x[1], reverse=True)
        best_matches = [index for index, value in sorted_list[1:6]]
        return best_matches

    async def move_embed(self, move, character):
        embed = discord.Embed(title=character, url=move.character.link)
        embed.set_thumbnail(
            url=move.character.thumbnail)
        embed.add_field(name="Command", value=move.Command, inline=True)
        embed.add_field(name="Hit Level", value=move.HitLevel, inline=True)
        embed.add_field(name="Damage", value=move.Damage, inline=True)
        embed.add_field(name="Startup", value=move.StartUpFrame, inline=True)
        embed.add_field(name="Block", value=move.BlockFrame, inline=True)
        embed.add_field(name="Hit", value=move.HitFrame, inline=True)
        embed.add_field(name="CH", value=move.CounterHitFrame, inline=True)
        embed.add_field(name="Notes", value=move.Notes, inline=True)
        return embed

    async def others_embed(self, other_options):
        embed = discord.Embed(description="Other moves")
        numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for index, number in enumerate(numbers):
            embed.add_field(name=f"{number} {other_options[index].Command}", value="", inline=False)
        return embed

    @commands.is_owner()
    @commands.command()
    async def fetchfd(self, ctx):
        if ctx.channel.id in self.allowed_channels:
            with Session(self.engine) as session:
                links, image_links = await self.get_links()
                for index, link in enumerate(links):
                    await self.add_characters_to_db(session, link, image_links[index])
                    moves = await self.fetch_moves(link)
                    await self.add_moves_to_db(session, moves, index + 1)
                await ctx.send("Successfully added moves to the database")

    @commands.is_owner()
    @commands.command()
    async def removedb(self, ctx):
        if ctx.channel.id in self.allowed_channels:
            os.remove('/home/frizen/framedata.db')
            await ctx.send("Successfully removed the database")

    @commands.command()
    async def fd(self, ctx, character, *, move):
        if ctx.channel.id in self.allowed_channels:
            with Session(self.engine) as session:
                character = await self.find_character(session, character)
                self.last_character = character
                movelist = await self.get_list_of_moves(session, character)
                move_id = await self.get_move_id(movelist, move)
                self.other_options_ids = await self.get_best_matches(movelist, move)
                move = await self.get_move_by_id(session, move_id, character)
                embed = await self.move_embed(move, character)
                message = await ctx.send(embed=embed)
                self.last_message = message.id
                await message.add_reaction('❌')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji = payload.emoji.name
        message_id = payload.message_id
        if message_id == self.last_message:
            if payload.member.id != 1004010832411250748:
                with Session(self.engine) as session:
                    numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
                    if emoji == "❌":
                        channel = self.bot.get_channel(payload.channel_id)
                        other_options = [await self.get_move_by_id(session, moveid, self.last_character) for moveid in self.other_options_ids]
                        embed = await self.others_embed(other_options)
                        message = await channel.send(embed=embed)
                        self.last_message = message.id
                        for number in numbers:
                            await message.add_reaction(number)

                    if emoji in numbers:
                        channel = self.bot.get_channel(payload.channel_id)
                        new_move = await self.get_move_by_id(session, self.other_options_ids[numbers.index(emoji)], self.last_character)
                        embed = await self.move_embed(new_move, self.last_character)
                        await channel.send(embed=embed)
