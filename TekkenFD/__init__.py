from .TekkenFD import TekkenFD


async def setup(bot):
    await bot.add_cog(TekkenFD(bot))