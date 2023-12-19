from .MortalFD import MortalFD


async def setup(bot):
    await bot.add_cog(MortalFD(bot))