#!/usr/bin/env python3
import asyncio 
import os 
import sys 

from dotenv import load_dotenv
import discord 
from discord.ext import commands

from quadbot import QuadBot
PREFIX = "?"

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    print("Unable to load DISCORD_TOKEN environment variable. Exiting...",
          file=sys.stderr)
    sys.exit(10)


async def load_extensions(bot: commands.Bot) -> None:
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main() -> None:
    quadbot = QuadBot(PREFIX, intents=discord.Intents.all())
    async with quadbot:
        await load_extensions(quadbot)
        await quadbot.start(TOKEN)


asyncio.run(main())
