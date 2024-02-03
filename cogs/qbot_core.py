import sys
import asyncio 
import json
import random
import discord
from discord.ext import commands

class QCore(commands.Cog):
    # TODO: Define shutdown command to save variable values to config.json
    def __init__(self, bot: commands.Bot) -> None:
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
        except FileNotFoundError:
            print("Fatal error: unable to find config.json file!", file=sys.stderr)
            exit(1)
        
        self.bot = bot
        self.cmd_options = config["cmd_options"] 
        self.users = config["users"]
        self.realnames = config["realnames"]
        self.emoji_codes: dict = config["emoji_codes"]
        self.error_messages: list[str] = config["error_messages"]
        self.reject_messages: list[str] = config["reject_messages"]

        self.statuses: list = [discord.CustomActivity(name=status) for status in config["statuses"]]


    def get_error_msg(self) -> str:
        return random.choice(self.error_messages)


    def get_reject_msg(self) -> str:
        return random.choice(self.reject_messages)


    def get_real_name(self, username: str) -> str:
        # TODO: Implement me!!
        return self.realnames[username]


    async def randomize_presence(self) -> None:
        activity = random.choice(self.statuses)
        print(f"Setting presence to {activity}")
        await self.bot.change_presence(activity=activity)


    @commands.command()
    async def get_react_hook(self, 
                  ctx: commands.Context,
                  user: str) -> None:
        try:
            hook = self.users[user.lower()]["react_hooks"]
            await ctx.reply(f"```\nHook name:\n{user}\nValue:{hook}\n```")
        except KeyError:
            await ctx.reply(f"Unknown user: {user}")


    @commands.command()
    async def get_elo(self, 
                      ctx: commands.Context,
                      user: str) -> None:
        try:
            elo = self.users[user.lower()]["elo"]
            await ctx.reply(f"{user}'s ELO: {elo}")
        except KeyError:
            await ctx.reply(f"Unknown user: {user}")


    @commands.command()
    async def show_all(self, ctx: commands.Context) -> None:
        await ctx.reply(f"```\n{self.users}\n```")


    @commands.command()
    async def unsnake(self, ctx: commands.Context) -> None:
        if ctx.message.reference is None:
            await ctx.reply("Unable to unsnake message. No message is being replied to")

        
    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        if msg.author == self.bot.user:
            return


    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        print("Message edit:")
        print(f"Before: {before.content}\n After: {after.content}")
        author = self.get_real_name(before.author.name)
        self.users[author]["edited_msg"]["before"] = before.content 
        self.users[author]["edited_msg"]["after"] = after.content


    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, err: commands.CommandError) -> None:
        if isinstance(err, commands.CommandNotFound):
            print("Unknown command.")
            await ctx.reply(self.get_error_msg())


    @commands.Cog.listener()
    async def on_command(self) -> None:
        await self.randomize_presence()


