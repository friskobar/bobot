import os
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready():
    print("BOBOT IS ON BITCHES PREPARE THOU ASSES")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="ping")
async def ping(i: discord.Interaction):
    await i.response.send_message("bong")

bot.run(os.environ["TOKEN"])
