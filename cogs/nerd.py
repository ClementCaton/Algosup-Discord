import discord

from discord.ext import commands

from classes.discordbot import DiscordBot

class Nerd(commands.Cog, name="nerd"):
    """
        He do be deserving it tho.

        Require intents: 
			- message_content
		
		Require bot permission:
			- read_messages
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

        self.target = "219156294974570497"
        self.EMOJI = '🤓'

    def help_custom(self) -> tuple[str, str, str]:
        emoji = self.EMOJI
        label = "Nerd"
        description = "For when someone is being a nerd."
        return emoji, label, description

    @commands.Cog.listener("on_message")
    async def on_receive_message(self, message: discord.Message) -> None:
        if not message.author.bot and message.author.id == self.target:
            await message.add_reaction(self.EMOJI)