import os
from discord.ext import commands

# TODO: Setup logger


class QuadDev(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def reload_all(self, ctx: commands.Context) -> None:
        """
        [Admin only] Reload all cogs.
        """
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                print(f"Reloading cog: {filename}")
                await self.bot.reload_extension("cogs.{filename[:-3]}")


    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        """
        [Admin only] Sync slash commands.
        """
        print(f"Syncing guild: {ctx.guild}")
        synced = await self.bot.tree.sync(guild=ctx.guild)
        await ctx.reply(f"Synced {len(synced)} commands in guild \"{ctx.guild}\".")
        for cmd in synced:
            print(f"Synced command {cmd}")


    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Loaded QuadDev cog!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QuadDev(bot))
