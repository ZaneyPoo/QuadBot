import sys 
import json
import random
from enum import Enum
from typing import NoReturn

import discord 
from discord.ext import commands

class ReactType(Enum):
    REACTION = "reaction"
    REPLY = "reply"
    CALLBACK = "callback"


class ReactHook:
    def __init__(self, hook: str, react_type: str, content: str, enabled: bool = True) -> None:
        self.hook = hook

        if react_type == "reaction":
            self.react_type = ReactType.REACTION
        elif react_type == "reply":
            self.react_type = ReactType.REPLY
        else:
            self.react_type = ReactType.CALLBACK

        self.content = content # TODO: Make this automatically instantiate an Emoji object if has colons
        self.enabled = enabled



class Chatter:
    def __init__(self, 
                 bot: commands.Bot,
                 username: str, 
                 aliases: list[str] = [],
                 elo: int = 0,
                 react_hooks: list[ReactHook] = [],
                 react_modifier: int = 100) -> None:
        self.username = username
        
        self.user = discord.utils.get(bot.users, name=username)
        self.aliases = aliases

        if not self.user is None:
            self.aliases.append(self.user.display_name)

        self.elo = elo
        self.react_hooks = react_hooks
        self.react_modifier = react_modifier



class QuadBot(commands.Bot):
    _CONFIG_FILE = "config.json"
    _CHATTERS_FILE = "chatters.json"
    _LABRADORATORY_ID = 1175185230118781189
    _GAME_CHAT_ID = 1123822985120321536 

    def __init__(self, 
                 prefix: str | set[str], 
                 intents: discord.Intents, 
                 config_file: str = _CONFIG_FILE,
                 chatters_file: str = _CHATTERS_FILE) -> None:
        super().__init__(prefix, intents=intents)
        
        self._setup_data(config_file)
        self._setup_chatters(chatters_file)


    # TODO: setup SQLite database instead of using JSON as a glorified db
    def _setup_data(self, config_file: str) -> None:
        config = self.load_json(config_file)

        self.options: dict[str, bool] = config["options"]
        self.emoji_codes: dict[str, str] = config["emoji_codes"]
        self.error_messages: list[str] = config["error_messages"]
        self.reject_messages: list[str] = config["reject_messages"]

        self.statuses: list[discord.CustomActivity] = [
            discord.CustomActivity(name=status) for status in config["statuses"]
        ]

        react_hooks = config["react_hooks"]

        # self.global_react_hooks = [ReactHook(**react_hooks[key]) for key in react_hooks.keys()]


    def _setup_chatters(self, chatters_file: str) -> None:
        chatters = self.load_json(chatters_file)


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


    #def get_chatter(self, realname: str) -> dict:
    #    return self.chatters[realname]


    async def randomize_presence(self) -> None:
        activity = random.choice(self.statuses)
        print(f"Setting presence to {activity}")
        await self.change_presence(activity=activity)


