import discord
import json
import re
import uuid
import datetime as dt
from discord import app_commands
from discord.ext import commands
from cogs.notcogs.utils import validate_server, log_action
from cogs.notcogs import config
from cogs.notcogs.config import Action

class Moderation(commands.Cog):
    def __init__(self, _bot: discord.Bot):
        self.bot = _bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cogged moderation")
    
    @commands.Cog.listener()
    async def on_message_delete(self, m: discord.Message):
        if m.channel.id in config.Channels.log:
            for user in config.log_notif:
                await bot.get_user(user).send(f"**__WARNING!__** This message was deleted from the <#{message.channel.id}> log channel. The log:\n\n{message.content}", embeds=message.embeds)
        else: #if not on the log channel, regularly log the delete
            em = discord.Embed(title = "Message deleted.",
                                color=discord.Color.from_rgb(10,10,12),
                                timestamp=dt.datetime.now()
                                )
            em.add_field(name="Content", value=f"{m.content}")
            em.add_field(name="Owner", value=f"{m.author.mention}")
            for c in config.Channels.log:
                channel = m.guild.get_channel(c)
                print(channel)
                if channel == None:
                    print("isnone")
                    continue # this is me checking if we have a logs channel setup on the server
                #i did check if it was a TextChannel but i guess python doesnt have composition
                await channel.send("Message Deleted", embeds=[em])
        print("Message deleted!")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before:discord.Message, after:discord.Message):
        if before.author.id == self.bot.application_id:
            print("author is ME")
            return
        em = discord.Embed(title = "Message edit.",
                            color=discord.Color.from_rgb(10,10,12),
                            timestamp=dt.datetime.now()
                            )
        em.add_field(name="Before", value=f"{before.content}")
        em.add_field(name="After", value=f"{after.content}")
        em.add_field(name="Owner", value=f"{before.author.mention}")
        for c in config.Channels.log:
            channel = before.guild.get_channel(c)
            if channel == None:
                continue
            await channel.send("Message Edited", embeds=[em])
        print("postmessageedit")
            


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
            await log_action(self.bot, i.user, reason, Action.TIMEOUT, offender, {"Duration": duration})

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
            await log_action(self.bot, i.user, reason, Action.UNTIMEOUT, offender)

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
            await log_action(self.bot, i.user, reason, Action.KICK, offender)


    @app_commands.command(name="warnings", description="List warnings of a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(self, i: discord.Interaction, member: discord.Member):
        em = discord.Embed(title="Warnings",
                        color=discord.Color.from_rgb(10, 10, 12),
                        timestamp=dt.datetime.now()
                        )

        
        with open("warns.json", "r+") as f:
            w_users = json.loads(f.read())


        for user in w_users:
            if not user:
                continue
            
            key = str(member.id)
            if key in user:
                for warning in user[key]:
                    for k, v in warning.items():
                        em.add_field(name=k, value=v)

        await i.response.send_message("List of warnings", embeds=[em])
                

    @app_commands.command(name="warn", description="Warns a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, i: discord.Interaction, offender: discord.Member, reason: str):
        valid = await validate_server(i)
        if not valid:
            return

        
        warn_id = str(uuid.uuid4())
        exists = False
        
        with open("warns.json", "r+") as f:
            w_users = json.loads(f.read())

        for user in w_users:
            if not user:
                continue

            key = str(offender.id)
            if key in user:
                user[key].append({warn_id: reason})
                exists = True
                break


        if not exists:
            w_users.append({str(offender.id): [{warn_id: reason}]})

        with open("warns.json", "w") as f:
            s = json.dumps(w_users, indent=4)
            f.write(s)

        await i.response.send_message(f"Warned {offender.mention} for:\n> {reason}\n\nWarn ID: {warn_id}")
        await offender.send(f"You've been warned for:\n> {reason}")
        await log_action(self.bot, i.user, reason, Action.WARN, offender, {"Warn ID": warn_id})
        
    @app_commands.command(name="unwarn", description="Unwarns a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unwarn(self, i: discord.Interaction, offender: discord.Member, warn_id: str, reason: str):
        valid = await validate_server(i)
        if not valid:
            return

        with open("warns.json", "r") as f:
            w_users = json.load(f)

        found = False

        for user in w_users:
            if not user:
                continue

            warnings = user.get(str(offender.id))

            if warnings is not None:
                found = True

                user[str(offender.id)] = [
                    warning
                    for warning in warnings
                    if warn_id not in warning
                ]

                break

        with open("warns.json", "w") as f:
            json.dump(w_users, f, indent=4)


        if not found:
            await i.response.send_message("No such warning exists.")
        else:
            await i.response.send_message("Removed.")
            await log_action(self.bot, i.user, reason, Action.UNWARN, offender, {"Warn ID": warn_id})


async def setup(_bot: discord.Bot):
    await _bot.add_cog(Moderation(_bot))
