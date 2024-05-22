#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import random
import time

from twitchio import ChannelInfo
from twitchio.ext import commands

# Change to the bot.py directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Bot(commands.Bot):
    """Instance of the bot containing all commands."""

    def __init__(self):
        self.config = {}
        self.config_location = "config.json"
        self.open_config()
        self.last_death = 0

        super().__init__(
            token=self.config["token"],
            prefix=self.config["prefix"],
            initial_channels=self.config["channels"],
            case_insensitive=True,
        )

    def open_config(self):
        """Load config from file."""
        with open(self.config_location, "r", encoding="utf-8") as current_config_file:
            self.config = json.load(current_config_file)

    def save_config(self):
        """Save config to file."""
        with open(self.config_location, "w", encoding="utf-8") as current_config_file:
            json.dump(
                self.config,
                current_config_file,
                indent=4,
                sort_keys=True,
                ensure_ascii=False,
            )

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")

    @commands.command()
    async def tot(self, ctx: commands.Context):
        """Death counter for multiple channels, counts by game title from twitch."""
        channel_name = ctx.channel.name
        channel_info = await self.fetch_channel(channel_name)
        current_game = channel_info.game_name

        # If no game is selected, skip
        if not current_game:
            return

        # Can only be run every 10 seconds
        if int(time.time()) - self.last_death < 11:
            await ctx.send("!tot wurde bereits in den letzten 10 Sekunden benutzt!")
            return

        # If channel does not exist in the config, add it.
        if not self.config["deaths"].get(channel_name):
            self.config["deaths"][channel_name] = {}

        # If the game does not exist for this channel, add it.
        if not self.config["deaths"][channel_name].get(current_game):
            self.config["deaths"][channel_name][current_game] = 0

        counter = self.config["deaths"][channel_name][current_game] + 1

        self.config["deaths"][channel_name][current_game] = counter
        self.last_death = int(time.time())

        response = (
            f"{channel_name} ist schon {counter} mal in {current_game} gestorben!"
        )
        self.save_config()
        await ctx.send(response)

    @commands.command(aliases=("knuddel", "knuddeln"))
    async def cuddle_attack(self, ctx: commands.Context):
        attack_type = random.choice(self.config["cuddle_attack"])
        target = ctx.message.content.split(" ")[1]
        response = attack_type.format(target=target, sender=ctx.author.name)
        await ctx.send(response)

    @commands.command()
    async def zufallshut(self, ctx: commands.Context):
        """Picks a random hat from the config."""
        one_hat = random.choice(self.config["hats"])

        await ctx.send(f"Für {ctx.author.name} zufällig ausgewählt: {one_hat}")

    @commands.command(aliases=("hüte", "huete"))
    async def hat_command(self, ctx: commands.Context):
        """Lists all available hats."""
        all_hats = ", ".join(self.config["hats"])
        response = f"Folgende Hüte stehen zur Auswahl: {all_hats}."
        await ctx.send(response)


def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
