import sys 
import json
import random
from typing import Any, NoReturn

import discord 
from discord.ext import commands, tasks


class QuadBot(commands.Bot):
    _CONFIG_FILE = "config.json"
    _LABRADORATORY_ID = 1175185230118781189
    _GAME_CHAT_ID = 1123822985120321536 

    def __init__(self, 
                 prefix: str | set[str], 
                 intents: discord.Intents, 
                 config_file: str = _CONFIG_FILE) -> None:
        super().__init__(prefix, intents=intents)
        
        self._setup_data(config_file)


    # TODO: setup SQLite database instead of using JSON as a glorified db
    def _setup_data(self, config_file: str) -> None:
        config = self.load_json(config_file)

        self.options: dict[str, Any] = config["options"]
        self.emoji_codes: dict[str, str] = config["emoji_codes"]
        self.error_messages: list[str] = config["error_messages"]
        self.reject_messages: list[str] = config["reject_messages"]

        self.statuses: list[discord.CustomActivity] = [
            discord.CustomActivity(name=status) for status in config["statuses"]
        ]


    def load_json(self, file: str) -> dict | NoReturn:
        try:
            with open(file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Unable to open file: {file}. Exiting...", file=sys.stderr)
            exit(1)
        

    def get_error_msg(self) -> str:
        return random.choice(self.error_messages)


    def get_reject_msg(self) -> str:
        return random.choice(self.reject_messages)


    @tasks.loop()
    async def randomize_status(self) -> None:
        activity = random.choice(self.statuses)
        print(f"Setting presence to {activity}")
        await self.change_presence(activity=activity)


