import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Optional, Union
import typing
import discord
from discord.app_commands import describe
from discord.ext import commands
from quadbot import QuadBot
import re

discord.utils.setup_logging(level=logging.DEBUG)

_ANTI_SNAKE_EMBED_TEMPLATE = (
"""
**Before**: 
{before}

**After**:
{after}
""".strip())


@dataclass(kw_only=True)
class ChatHook:
    pattern: str 
    target: discord.Member | discord.User | Literal["global"] = "global"
    modifier: Callable[..., bool] = lambda: True 
    enabled: bool = True

    async def trigger(self, msg: discord.Message) -> None:
        ...


    def embed_field(self, embed: discord.Embed) -> discord.Embed:
        return embed.add_field(
            name=f"{str(self)}",
            value='\n'.join([f"**{key}:** {value}" for key, value in vars(self).items()]),
            inline=False
        )


# TODO: Can I fix all this code duplication?
@dataclass(kw_only=True)
class ReplyHook(ChatHook):
    response: str

    async def trigger(self, msg: discord.Message) -> None:
        await msg.reply(self.response)


    def __str__(self) -> str:
        target = "anyone" if self.target == "global" else self.target.mention
        return f"Reply with \"{self.response}\" if I see the pattern \"{self.pattern}\" from {target}"


@dataclass(kw_only=True)
class ReactHook(ChatHook):
    response: discord.Emoji | str

    async def trigger(self, msg: discord.Message) -> None:
        await msg.add_reaction(self.response)


    def __str__(self) -> str:
        target = "anyone" if self.target == "global" else self.target.mention
        return f"React with \"{self.response}\" if I see the pattern \"{self.pattern}\" from {target}"


@dataclass(kw_only=True)
class EventHook(ChatHook):
    event_name: str
    bot: commands.Bot

    async def trigger(self, msg: discord.Message) -> None:
        self.bot.dispatch(self.event_name, msg)


    def __str__(self) -> str:
        target = "anyone" if self.target == "global" else self.target.mention
        return f"Trigger event \"{self.event_name}\" if I see the pattern \"{self.pattern}\" from {target}"


class AddCHFlags(commands.FlagConverter):
    """
    blah
    """
    type_: Literal["reply", "reaction"] = (
        commands.flag(name="type", 
                      description="The type of ChatHook to add [reply | reaction]")
    )
    pattern: str = (
        commands.flag(description="The pattern to search for.")
    )
    response: Union[discord.Emoji, str] = (
        commands.flag(description="The sentence or emoji that QuadBot should react with")
    )
    target: Union[discord.Member, discord.User, Literal["global"]] = (
        commands.flag(description="The user to match for or \"global\" to match everyone")
    )
    use_regex: bool = (
        commands.flag(name="regex", 
                      description="Whether or not the pattern uses regular expressions",
                      default=False)
    )
    

class QuadReact(commands.Cog):
    def __init__(self, bot: QuadBot) -> None:
        self.bot = bot
        self._init_chathooks()


    def _init_chathooks(self) -> None:
        default_hooks = [
            ReplyHook(
                pattern="balls", 
                response="balls"
            ),
            ReactHook(
                pattern="skull", 
                response=chr(0x1f480)
            ),
            EventHook(
                pattern=r"\w+\+\+|<@!?\d+> \+\+", # Matches for a name or mention followed by ++
                event_name="elo_increment", 
                bot=self.bot
            ),
            EventHook(
                pattern=r"\w+\-\-|<@!?\d+> \-\-", # Matches for a name or mention followed by --
                event_name="elo_decrement", 
                bot=self.bot
            ),
        ]
        self.chathooks: dict[str, ChatHook] = {chathook.pattern: chathook for chathook in default_hooks}
        self.compiled_patterns: list[re.Pattern] = [re.compile(key) for key in self.chathooks.keys()]


    def add_chathook_pattern(self, chathook: ChatHook) -> None:
        self.compiled_patterns.append(re.compile(chathook.pattern))
        self.chathooks.update({chathook.pattern: chathook})
            

    # FIXME: I don't know why but the flag converter doesn't display the descriptions 
    #        inside the help message for the command
    @commands.command()
    async def add_hook(self, ctx: commands.Context, *, flags: AddCHFlags) -> None:
        print(f"Flags: {flags}")
        if not flags.use_regex:
            flags.pattern = re.escape(flags.pattern)

        try: 
            re.compile(flags.pattern)
        except re.error as err:
            await ctx.reply(f"Invalid regex: {err}")
            return

        if flags.target != "global" and flags.target.bot:
            await ctx.reply(f"Cannot use a bot as the target for a ChatHook")
            return

        match flags.type_:
            case "reply":
                flags.response = typing.cast(str, flags.response)
                chathook = ReplyHook(pattern=flags.pattern, 
                                     response=flags.response,
                                     target=flags.target)

            case "reaction":
                flags.response = typing.cast(discord.Emoji, flags.response)
                chathook = ReactHook(pattern=flags.pattern,
                                     response=flags.response,
                                     target=flags.target)

        self.add_chathook_pattern(chathook)
        await ctx.reply("ChatHook added successfully")


    # TODO: add command specific error handling
    @add_hook.error
    async def add_hook_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        print(error)


    @commands.command()
    async def show_hooks(self, 
                         ctx: commands.Context,
                         verbose: Optional[bool] = False) -> None:
        """
        Show the currently active ChatHooks
        """
        embed = discord.Embed(
            title="Current ChatHooks"
        )
        if verbose:
            for hook in self.chathooks.values():
                embed = hook.embed_field(embed)
        else:
            # TODO: Fix this ridiculous one liner 
            embed.description = '\n'.join([f"{i}. {str(hook)}" for i, hook in enumerate(self.chathooks.values(), start=1)])
        await ctx.reply(embed=embed)


    @commands.Cog.listener()
    async def on_chathook_trigger(self, msg: discord.Message, chathook: ChatHook) -> None:
        if not chathook.enabled:
            print(f"ChatHook {chathook} is not enabled!")
            return 

        if chathook.target != "global" and str(msg.author) != str(chathook.target):
            print(f"Message author doesn't match ChatHook target: {chathook.target}")
            return 

        if not chathook.modifier():
            print(f"ChatHook {chathook} failed modifier check!")
            return 

        await chathook.trigger(msg)


    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        if msg.author.bot: # don't search if user is a bot
            return

        prefix = tuple(await self.bot.get_prefix(msg))
        if msg.content.startswith(prefix): # don't search if this is a command
            return

        print(f"Scanning for patterns: {self.compiled_patterns}")
        for pattern in self.compiled_patterns:
            match = pattern.match(msg.content)
            
            if match:
                print(f"Dispatching ChatHook for {match}")
                self.bot.dispatch("chathook_trigger", msg, self.chathooks[match.re.pattern])


    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Loaded QuadReact cog!")



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
            description=_ANTI_SNAKE_EMBED_TEMPLATE.format(**self.edited_msg)
        )
        await ctx.reply(embed=embed)


    # TODO: Hook this up to ELO system once DB is hooked up
    @commands.Cog.listener()
    async def on_elo_increment(self, msg: discord.Message) -> None:
        # Is there a sane way for me to pass in the name of the target without rescanning?
        print("++")


    # TODO: Hook this up to ELO system once DB is hooked up
    @commands.Cog.listener()
    async def on_elo_decrement(self, msg: discord.Message) -> None:
        # Is there a sane way for me to pass in the name of the target without rescanning?
        print("--")


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
    async def on_command_error(self, ctx: commands.Context, err: commands.CommandError) -> None:
        if isinstance(err, commands.CommandNotFound):
            print(f"{err}: Unknown command.")
            await ctx.reply(self.bot.get_error_msg())
        else:
            print(err)


    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Loaded QuadChat cog!")


async def setup(bot: QuadBot) -> None:
    await bot.add_cog(QuadReact(bot), override=True)
    await bot.add_cog(QuadChat(bot), override=True)


