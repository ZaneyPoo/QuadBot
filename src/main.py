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
    prefix = PROD_PREFIX if "QUADBOT_TESTING" in os.environ else TEST_PREFIX
    print(f"Setting prefix to '{prefix}'", file=sys.stderr)


    quadbot = QuadBot(prefix, intents=discord.Intents.all())

    @quadbot.listen()
    async def on_ready() -> None:
        await quadbot.wait_until_ready()
        quadbot.randomize_status.change_interval(
            minutes=quadbot.options["status_update_interval_mins"]
        )
        quadbot.randomize_status.start()

    async with quadbot:
        await load_extensions(quadbot)
        await quadbot.start(TOKEN)


asyncio.run(main())
