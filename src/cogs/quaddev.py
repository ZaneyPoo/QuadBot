import os
import logging
import discord
from discord.ext import commands

# TODO: Setup logger
discord.utils.setup_logging(level=logging.DEBUG)

COG_STATS_TEMPLATE = (
"""
**App Commands**:
{app_cmds}
**Commands**:
{cmds}
**Listeners**:
{listeners}
""".strip())

def format_cog_list(bot: commands.Bot) -> discord.Embed:
    cogs = '\n'.join([cog for cog in bot.cogs.keys()])
    return discord.Embed(
        title="Currently loaded Cogs:",
        description=cogs
    )


def format_cog_stats(cog: commands.Cog) -> discord.Embed:
    stats = {
        "app_cmds": '\n'.join([str(app_cmd) for app_cmd in cog.walk_app_commands()]),
        "cmds": '\n'.join([str(cmd) for cmd in cog.walk_commands()]),
        "listeners": '\n'.join([str(listener) for listener in cog.get_listeners()]),
    }
    return discord.Embed(
        title=f"Cog: {cog.qualified_name}",
        description=COG_STATS_TEMPLATE.format(**stats)
    )


class QuadDev(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def reload_all(self, _: commands.Context) -> None:
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


    @commands.command()
    @commands.is_owner()
    async def inspect(self, 
                      ctx: commands.Context, 
                      cog_name: str) -> None:
        """
        [Admin only] Give a detailed look at a specific Cog
        """
        cog = self.bot.get_cog(cog_name)

        if cog is None:
            await ctx.reply(f"Unable to find cog: {cog_name}")
            return

        embed = format_cog_stats(cog)
        await ctx.reply(embed=embed)


    @commands.command()
    @commands.is_owner()
    async def show_cogs(self, ctx: commands.Context) -> None:
        """
        [Admin only] Return a list of the Bot's currently loaded cogs
        """
        embed = format_cog_list(self.bot)
        await ctx.reply(embed=embed)


    @commands.Cog.listener()
    async def on_cog_command_error(self, ctx: commands.Context, err: commands.CommandError) -> None:
        await ctx.reply(f"Error: {err}")


    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Loaded QuadDev cog!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QuadDev(bot), override=True)
