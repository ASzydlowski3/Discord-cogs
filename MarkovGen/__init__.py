from .MarkovGen import MarkovGen


async def setup(bot):
    await bot.add_cog(MarkovGen(bot))