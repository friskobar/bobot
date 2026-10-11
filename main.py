import os
import asyncio
import re
import discord
from discord.ext import commands
from discord import app_commands

class Bot(commands.Bot):
    async def setup_hook(self) -> None:
        print("Setupping")
        await load_cogs(self)
    async def on_ready(self):
        print("BOBOT IS ON PREPARE THOU ASSES")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="misterbob on YouTube"))


client = Bot(command_prefix=".", intents=discord.Intents.all())
client.remove_command("help")

#load all cogs
async def load_cogs(c: discord.Bot): # c stands for Client
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await c.load_extension(f"cogs.{filename[:-3]}")

@client.command()
async def sync(ctx):
    print("Syncing")
    try:
        synced = await client.tree.sync()
        print(f"synced {len(synced)} commands")
        await ctx.send(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)

client.run(os.environ["TOKEN"])
