#!/usr/bin/env python3
import asyncio 
import os 
import sys 

from dotenv import load_dotenv
import discord 
from discord.ext import commands

from cogs import qbot_core

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "?"

if TOKEN is None:
    print("Unable to load DISCORD_TOKEN environment variable. Exiting...",
          file=sys.stderr)
    sys.exit(10)


class QuadBot(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(qbot_core.QCore(self))


async def main() -> None:
    intents = discord.Intents.all()

    quadbot = QuadBot(PREFIX, intents=intents)
    await quadbot.start(TOKEN)


asyncio.run(main())
