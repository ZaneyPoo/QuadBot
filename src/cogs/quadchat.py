from collections.abc import Callable
from dataclasses import dataclass
import discord
from discord.ext import commands
from quadbot import QuadBot
import re

ANTI_SNAKE_TEMPLATE = (
"""
**Before**: 
{before}

**After**:
{after}
""".strip())


@dataclass(kw_only=True)
class Hook:
    pattern: str 
    modifier: Callable[..., bool] = lambda: True 
    enabled: bool = True

    async def trigger(self, msg: discord.Message) -> None:
        ...


@dataclass(kw_only=True)
class ReplyHook(Hook):
    response: str

    async def trigger(self, msg: discord.Message) -> None:
        await msg.reply(self.response)


@dataclass(kw_only=True)
class ReactHook(Hook):
    response: str | discord.Emoji

    async def trigger(self, msg: discord.Message) -> None:
        await msg.add_reaction(self.response)


HOOKS = [
    ReplyHook(pattern="balls", response="balls"),
    ReactHook(pattern="skull", response=chr(0x1f480)),
]


class QuadReact(commands.Cog):
    def __init__(self, bot: QuadBot) -> None:
        self.bot = bot
        self._init_hooks()


    def _init_hooks(self) -> None:
        self.hooks = {hook.pattern: hook for hook in HOOKS}
        self.hook_pattern = re.compile('|'.join(trigger for trigger in self.hooks.keys()))


    @commands.command()
    async def add_react(self, 
                        ctx: commands.Context,
                        pattern: str) -> None:
        ...


    @commands.Cog.listener()
    async def on_hook_trigger(self, msg: discord.Message, hook: Hook) -> None:
        if not hook.enabled or not hook.modifier():
            print(f"Hook {hook} failed modifier check or is not enabled!")
            return 

        await hook.trigger(msg)


    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        print(f"Got message: {msg.content}")
        if msg.author.bot: # gtfo if user is a bot
            return

        if (matches := self.hook_pattern.findall(msg.content)):
            print(f"Found matches for hooks: {matches}")
            for match in matches:
                print(f"Dispatching hook for {match}")
                self.bot.dispatch("hook_trigger", msg, self.hooks[match])


class QuadChat(commands.Cog):
    # TODO: Define shutdown command to save variable values to config.json
    def __init__(self, bot: QuadBot) -> None:
        self.bot = bot
        self.edited_msg: dict[str, str] | None = None


    @commands.command()
    async def stats(self, 
                    ctx: commands.Context, 
                    member: discord.Member | None = None) -> None:
        ...


    @commands.hybrid_command(
        name = "antisnake",
        description = "Begone stupid snake!!!",
        aliases = [
            "as", 
            "us", 
            "unsnake", 
            "nosnek",
            "unsnek",
            "unsanke",
            "nosanke",
        ]
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

        
    @commands.Cog.listener()
    async def on_message(self, ctx: commands.Context) -> None:
        if ctx.author.bot:
            return


    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        print("Message edit:")
        print(f"Before: {before.content}\n After: {after.content}")
        self.edited_msg = {"before": before.content, "after": after.content}


    @commands.Cog.listener()
    async def on_cog_command_error(self, ctx: commands.Context, err: commands.CommandError) -> None:
        if isinstance(err, commands.CommandNotFound):
            print(f"{err}: Unknown command.")
            await ctx.reply(self.bot.get_error_msg())


    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Loaded QuadChat cog!")


async def setup(bot: QuadBot) -> None:
    await bot.add_cog(QuadReact(bot), override=True)
    await bot.add_cog(QuadChat(bot), override=True)


