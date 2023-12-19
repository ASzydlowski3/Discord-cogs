import discord
from redbot.core import Config, commands
import asyncio
import re
import json

import os
from bs4 import BeautifulSoup
import aiohttp
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, DeclarativeBase, relationship
from fuzzywuzzy import process, fuzz


class MortalFD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channels = [1003996397739188294, 1173952046043512894]
        self.engine = create_engine('sqlite:///home/frizen/framedatamk.db', echo=True)

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
        category = Column(String)
        subcategory = Column(String)
        parent_command = Column(String)
        move_name = Column(String)
        command = Column(String)
        hit_damage = Column(String)
        block_damage = Column(String)
        fblock_damage = Column(String)
        block_type = Column(String)
        startup = Column(String)
        active = Column(String)
        recovery = Column(String)
        cancel = Column(String)
        hit_advantage = Column(String)
        block_advantage = Column(String)
        fblock_advantage = Column(String)
        properties = Column(String)
        notes = Column(String)

    engine = create_engine('sqlite:///home/frizen/framedatamk.db', echo=True)
    Base.metadata.create_all(engine)

    async def fetch_url(self, url):
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url) as response:
                return await response.text(encoding='ISO-8859-1')

    async def get_links(self):
        data = await self.fetch_url('https://mk1.kombatakademy.com/characters/')
        soup = BeautifulSoup(data, "html.parser")
        roster = soup.find("div", class_="character-roster").find_all("div", class_="character-roster-portrait")
        roster.pop()
        roster = [char.get('style').split('/')[-1].split('.')[0] for char in roster]
        links = [f'https://mk1.kombatakademy.com/move-list/?character={char}&date=11-09-2023' for char in roster]
        image_links = [f'https://mk1.kombatakademy.com/images/characters/square/{char}.png' for char in roster]
        return links, image_links

    async def add_characters_to_db(self, session, link, image_link):
        name = link.split('=')[-2].split('&')[0].capitalize()
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
            if '(Air)' in move['move_name']:
                move['command'] = '(Air) ' + move['command']
            new_move = self.Move(
                character_id=char_id,
                category=move['category'],
                subcategory=move['subcategory'],
                parent_command=move['parent_command'],
                move_name=move['move_name'],
                command=move['command'],
                hit_damage=move['hit_damage'],
                block_damage=move['block_damage'],
                fblock_damage=move['fblock_damage'],
                block_type=move['block_type'],
                startup=move['startup'],
                active=move['active'],
                recovery=move['recovery'],
                cancel=move['cancel'],
                hit_advantage=move['hit_advantage'],
                block_advantage=move['block_advantage'],
                fblock_advantage=move['fblock_advantage'],
                properties=move['properties'],
                notes=move['notes']
            )
            move_objects.append(new_move)

        if move_objects:
            session.add_all(move_objects)
            session.commit()

    async def fetch_moves(self, link):
        data = await self.fetch_url(link)
        soup = BeautifulSoup(data, "html.parser")
        moves = soup.find_all('script')[2]
        moves = re.findall(r'\{([^}]*)\}', str(moves))
        moves_json = [json.loads("{" + s + "}") for s in moves]
        return moves_json

    async def get_list_of_moves(self, session, char_name):
        character = session.query(self.Character).filter(self.Character.name == char_name).first()
        movelist = [move.command for move in character.moves]
        return movelist

    async def find_character(self, session, char_name):
        characters = session.query(self.Character).all()
        character_names = [character.name for character in characters]
        found_character = process.extractOne(char_name, character_names)
        return found_character[0]

    async def get_move_id(self, movelist, searched_move):
        modified_movelist = [move.replace("/", "").replace("+", "", 1).replace(" ", "").replace(",", "").lower() for move in movelist]
        searched_move = searched_move.replace("/", "").replace("+", "", 1).replace(" ", "").replace(",", "").lower()
        best_match = 0
        move_id = None

        for count, move in enumerate(modified_movelist):
            move_match = fuzz.ratio(searched_move, move)

            if move_match > best_match:
                best_match = move_match
                move_id = count
        return move_id

    async def get_move_by_id(self, session, move_id, char_name):
        character = session.query(self.Character).filter(self.Character.name == char_name).first()
        move = character.moves[move_id]
        return move

    async def create_embed(self, move, character):
        embed = discord.Embed(color=0x00ffff, title=character.replace('-', " "), url=move.character.link)
        embed.set_thumbnail(
            url=move.character.thumbnail)
        embed.add_field(name="Category", value=move.category, inline=True)
        embed.add_field(name="Subcategory", value=move.subcategory, inline=True)
        embed.add_field(name="Parent Command", value=move.parent_command, inline=True)
        embed.add_field(name="Move Name", value=move.move_name, inline=True)
        embed.add_field(name="Command", value=move.command, inline=True)
        embed.add_field(name="Hit Damage", value=move.hit_damage, inline=True)
        embed.add_field(name="Block Damage", value=move.block_damage, inline=True)
        embed.add_field(name="Block Type", value=move.block_type, inline=True)
        embed.add_field(name="Startup", value=move.startup, inline=True)
        embed.add_field(name="Active", value=move.active, inline=True)
        embed.add_field(name="Recovery", value=move.recovery, inline=True)
        embed.add_field(name="Cancel", value=move.cancel, inline=True)
        embed.add_field(name="Hit Advantage", value=move.hit_advantage, inline=True)
        embed.add_field(name="Block Advantage", value=move.block_advantage, inline=True)
        embed.add_field(name="Flawless Block", value=move.fblock_advantage, inline=True)
        embed.add_field(name="Properties", value=move.properties, inline=True)
        embed.add_field(name="Notes", value=move.notes, inline=True)
        return embed

    @commands.is_owner()
    @commands.command()
    async def fetchfdmk(self, ctx):
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
    async def removedbmk(self, ctx):
        if ctx.channel.id in self.allowed_channels:
            os.remove('/home/frizen/framedatamk.db')
            await ctx.send("Successfully removed the database")

    @commands.command()
    async def mk(self, ctx, character, *, move):
        if ctx.channel.id in self.allowed_channels:
            try:
                with Session(self.engine) as session:
                    character = await self.find_character(session, character)
                    movelist = await self.get_list_of_moves(session, character)
                    move_id = await self.get_move_id(movelist, move)
                    move = await self.get_move_by_id(session, move_id, character)
                    embed = await self.create_embed(move, character)
                    await ctx.send(embed=embed)
            except AttributeError:
                await ctx.send("Move not found")
