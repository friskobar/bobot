import os
import discord

class Client(discord.Client):
    async def on_ready(self):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send("BOBOT IS UP PREPARE THOU ASSES")

intents = discord.Intents.default()

client = Client(intents=intents)
client.run(os.environ['TOKEN'])