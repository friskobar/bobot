import discord
import re
import datetime as dt
from discord import app_commands
from discord.ext import commands
from cogs.notcogs.utils import validate_server, log_action
from cogs.notcogs.config import Action

class Moderation(commands.Cog):
    def __init__(self, _bot: discord.Bot):
        self.bot = _bot
    @commands.Cog.listener()
    async def on_ready(self):
        print("Cogged moderation")
    @app_commands.command(name="clean", description="Cleans the channel from a certain member.")
    async def clean(self, i: discord.Interaction, offender: discord.Member, count: int, reason: str):
        valid = await validate_server(i)
        if not valid:
            return

        await i.response.send_message("Cleaning...", ephemeral=True)
        
        checker = lambda m: m.author == offender
        try:
            await i.channel.purge(limit=count, check=checker, bulk=True)
        except Exception as e:
            await i.channel.send_message(f"Couldn't clean: {str(e)}")
        else:
            await i.channel.send("Cleaned.")
            await log_action(self.bot, i.user, reason, Action.CLEAN, offender, {"Count": count})
    @app_commands.command(name="timeout", description="Times out a member for a duration")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, i: discord.Interaction, offender: discord.Member, duration: str, reason: str):
        valid = await validate_server(i)
        if not valid:
            return
        
        parts = re.findall(r"(\d+)\s*([dhm])", duration.lower())

        days = hours = minutes = 0

        for value, unit in parts:
            if unit == "d":
                days += int(value)
            elif unit == "h":
                hours += int(value)
            elif unit == "m":
                minutes += int(value)
        try:
            await offender.timeout(dt.timedelta(days=days, hours=hours, minutes=minutes))
        except Exception as e:
            await i.channel.send(f"Failed to timeout {offender.mention}. {str(e)}")
        else:
            await i.response.send_message(f"Timed {offender.mention} out for **{str(days)} days {str(hours)} hours and {str(minutes)} minutes**")
            await log_action(i.user, reason, Action.TIMEOUT, offender, {"Duration": duration})
    @app_commands.command(name="untimeout", description="Removes timeout from a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def untimeout(self, i: discord.Interaction, offender: discord.Member, reason: str):
        valid = await validate_server(i)
        if not valid:
            return

        try:
            await offender.timeout(None) # None actually removes the timeout
        except Exception as e:
            await i.channel.send(f"Failed to remove {offender.mention}'s timeout. {str(e)}")
        else:
            await i.response.send_message(f"Successfully removed {offender.mention}'s timeout.")
            await log_action(i.user, reason, Action.UNTIMEOUT, offender)
    @app_commands.command(name="kick", description="Kicks a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def kick(self, i: discord.Interaction, offender: discord.Member, reason: str):
        valid = await validate_server(i)
        if not valid:
            return
        
        try:
            await offender.kick(reason=reason)
        except Exception as e:
            await i.channel.send(f"Failed to kick {offender.mention}. {str(e)}")
        else:
            await i.response.send_message(f"Successfully kicked {offender.mention}.")
            await log_action(i.user, reason, Action.KICK, offender)

async def setup(_bot: discord.Bot):
    await _bot.add_cog(Moderation(_bot))
