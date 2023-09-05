from .SteamDB import SteamDB


async def setup(bot):
    await bot.add_cog(SteamDB(bot))