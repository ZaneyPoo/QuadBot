from collections.abc import Callable
from enum import Enum
from dataclasses import dataclass
from typing import Any
import discord
from discord.ext import commands
from quadbot import QuadBot

ANTI_SNAKE_TEMPLATE = (
"""
**Before**: 
{before}

**After**:
{after}
""".strip())


class HookType(Enum):
    REACTION = "reaction"
    REPLY = "reply"
    CALLBACK = "callback"


@dataclass
class ReactHook:
    """
    Data for reacting to messages in a customized way depending on various specified
    parameters. 

    :attr type_: The category 
    :attr trigger: The necessary pattern to trigger the hook
    :attr action: The action to take if the trigger is found in a message
    :attr modifier: Additional parameters that must be true in order for the hook to trigger
    """
    type_: HookType
    trigger: str
    action: discord.Emoji | str | Callable
    modifier: Callable[[Any], bool] | None = None 
    enabled: bool = True


class QuadChat(commands.Cog):
    # TODO: Define shutdown command to save variable values to config.json
    def __init__(self, bot: QuadBot) -> None:
        self.bot = bot
        self.edited_msg: dict[str, str] | None = None


    # @commands.command()
    # async def get_react_hook(self, 
    #               ctx: commands.Context,
    #               user: str) -> None:
    #     try:
    #         hook = self.bot.chatters[user.lower()]["react_hooks"]
    #         await ctx.reply(f"```\nHook name:\n{user}\nValue:{hook}\n```")
    #     except KeyError:
    #         await ctx.reply(f"Unknown user: {user}")


    # @commands.command()
    # async def get_elo(self, 
    #                   ctx: commands.Context,
    #                   user: str) -> None:
    #     try:
    #         elo = self.bot.chatters[user.lower()]["elo"]
    #         await ctx.reply(f"{user}'s ELO: {elo}")
    #     except KeyError:
    #         await ctx.reply(f"Unknown user: {user}")


    #@commands.command()
    #async def show_all(self, ctx: commands.Context) -> None:
    #    await ctx.reply(f"```\n{self.bot.chatters}\n```")


    # @commands.command()
    # async def show_aliases(self, 
    #                        ctx:commands.Context,
    #                        user: str | None = None) -> None:
    #     await ctx.reply(f"```\n{self.bot.aliases}\n```")


    @commands.command()
    async def stats(self, 
                    ctx: commands.Context, 
                    member: discord.Member | None = None) -> None:
        ...


    @commands.hybrid_command(
        name = "antisnake",
        description = "Begone stupid snake!!!",
        aliases=["as", "us", "unsnake", "nosnek"]
    )
    async def antisnake(self, ctx: commands.Context) -> None:
        if self.edited_msg is None:
            await ctx.reply("No recently edited messages :sob:")
            return
        
        embed = discord.Embed(
            title=":x: :snake: Antisnake! :x: :snake:",
            description=ANTI_SNAKE_TEMPLATE.format(**self.edited_msg)
        )
        await ctx.reply(embed=embed)

        
    # # commands.command(name="++")
    # async def plusplus(self, 
    #                    ctx: commands.Context, 
    #                    member: discord.User | discord.Member) -> None:
    #     chatter = self.bot.chatters[self.bot.get_real_name(member.name)]
    #     chatter["elo"] += 1
    #     await ctx.reply(f"{member.name} now has an ELO of {chatter['elo']}!")


    # # @commands.command(hidden=True, disabled=True)
    # async def minusminus(self, 
    #                      ctx: commands.Context, 
    #                      member: discord.User | discord.Member) -> None:
    #     chatter = self.bot.chatters[self.bot.get_real_name(member.name)]
    #     chatter["elo"] -= 1
    #     await ctx.reply(f"{member.name} now has an ELO of {chatter['elo']}!")


    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        if msg.author.bot: # gtfo if user is a bot
            return

        # if (parts := msg.content.partition("++"))[1] == "++":
        #     print(f"{parts[0]} plusplus")
        #     ctx = await self.bot.get_context(msg)
        #     await self.plusplus(ctx, msg.author)

        # elif (parts := msg.content.partition("--"))[1] == "--":
        #     print(f"{parts[0]} minusminus")
        #     ctx = await self.bot.get_context(msg)
        #     await self.minusminus(ctx, msg.author)



    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        print("Message edit:")
        print(f"Before: {before.content}\n After: {after.content}")
        self.edited_msg = {"before": before.content, "after": after.content}


    @commands.Cog.listener()
    async def on_command(self) -> None:
        await self.bot.randomize_presence()


    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, err: commands.CommandError) -> None:
        if isinstance(err, commands.CommandNotFound):
            print("Unknown command.")
            await ctx.reply(self.bot.get_error_msg())


async def setup(bot: QuadBot) -> None:
    await bot.add_cog(QuadChat(bot))
