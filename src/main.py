#!/usr/bin/env python3
import asyncio 
import os 
import sys 

import discord 
from discord.ext import commands

from quadbot import QuadBot
# TODO: Consider turning this into a function that returns the correct prefix
#       based on some conditions (msg is in the test guild, etc.)
PROD_PREFIX = '?'
TEST_PREFIX = '~'

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    print("Unable to load DISCORD_TOKEN environment variable. Exiting...",
          file=sys.stderr)
    sys.exit(10)


async def load_extensions(bot: commands.Bot) -> None:
    for filename in os.listdir("src/cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main() -> None:
    prefix = TEST_PREFIX if "-t" in sys.argv else PROD_PREFIX
    print(f"Setting prefix to '{prefix}'", file=sys.stderr)


    quadbot = QuadBot(prefix, intents=discord.Intents.all())

    @quadbot.event
    async def on_ready() -> None:
        await quadbot.randomize_presence()

    async with quadbot:
        await load_extensions(quadbot)
        await quadbot.start(TOKEN)


asyncio.run(main())
