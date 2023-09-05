from .MemeFetcher import MemeFetcher


async def setup(bot):
    await bot.add_cog(MemeFetcher(bot))