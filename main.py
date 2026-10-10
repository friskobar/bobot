import os
import re
import datetime as dt
import discord
import config
from discord.ext import commands
from discord.ext.commands import has_permissions

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
bot.remove_command('help')

############################ SEPARATE BELOW INTO A NEW FILE LATER ############################

async def log_action(actor: discord.Member, reason: str, action: config.Action, target: discord.Member) -> None:
    em = discord.Embed(title=action.name,
                       color=discord.Color.from_rgb(10, 10, 12),
                       timestamp=dt.datetime.now()
                       )

    em.set_footer(text=f"{actor.id} | {actor.global_name}")
    em.add_field(name="Offender", value=f"{target.global_name} ({target.id})")
    em.add_field(name="Reason", value=reason)

    for id in config.Channels.log:
        await bot.get_channel(id).send(embeds=[em])

# ensures that the server this command is ran on is one of ours; should prevent a wide variety of exploits involving custom permissions
async def validate_server(i: discord.Interaction) -> bool:
    if i.guild.id in config.servers:
        return True
    else:
        return False
    

############################ SEPARATE ABOVE INTO A NEW FILE LATER ############################

@bot.event
async def on_ready():
    print("bobot is on")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="misterbob on YouTube"))
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="bob")
async def ping(i: discord.Interaction):
    await i.response.send_message("bob")

@bot.tree.command(name="help")
async def help(i: discord.Interaction):
    desc = """
    1. __**/timeout [@offender] [duration] [reason]**__
        - Duration must be in the format `Xd Xh Xm` where X is the duration of the unit of time.
        - For example, `1d 10h 15m` as the duration will set the user's timeout to be *one day, ten hours and fifteen minutes*.
        - Discord's API has a 28 day maximum time for a timeout, so exceeding that will probably fallback to 28 days. Failing to mention a proper duration will not time the user out.

    2. __**/untimeout [@offender] [reason]**__
        - Removes timeout from a user.

    3. __**/kick [@offender] [reason]**__
        - Kicks a user from the server.
    
    """
    help_embed = discord.Embed(
        title="Help",
        description=desc
    )

    await i.response.send_message(embeds=[help_embed])
    
@bot.tree.command(name="timeout", description="Times out a member for a duration")
@has_permissions(moderate_members=True)
async def timeout(i: discord.Interaction, offender: discord.Member, duration: str, reason: str):
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
        await i.channel.send(f"Failed to timeout {member.mention}. {str(e)}")
    else:
        await i.response.send_message(f"Timed {offender.mention} out for **{str(days)} days {str(hours)} hours and {str(minutes)} minutes**")
        await log_action(i.user, reason, config.Action.TIMEOUT, offender)


@bot.tree.command(name="untimeout", description="Removes timeout from a member")
@has_permissions(moderate_members=True)
async def untimeout(i: discord.Interaction, offender: discord.Member, reason: str):
    valid = await validate_server(i)
    if not valid:
        return


    try:
        await offender.timeout(None) # None actually removes the timeout
    except Exception as e:
        await i.channel.send(f"Failed to remove {offender.mention}'s timeout. {str(e)}")
    else:
        await i.response.send_message(f"Successfully removed {offender.mention}'s timeout.")
        await log_action(i.user, reason, config.Action.UNTIMEOUT, offender)


@bot.tree.command(name="kick", description="Kicks a member")
@has_permissions(kick_members=True)
async def kick(i: discord.Interaction, offender: discord.Member, reason: str):
    valid = await validate_server(i)
    if not valid:
        return
    
    try:
        await offender.kick(reason=reason)
    except Exception as e:
        await i.channel.send("Failed to kick {offender.mention}. {str(e)}")
    else:
        await i.response.send_message(f"Successfully kicked {offender.mention}.")
        await log_action(i.user, reason, config.Action.KICK, offender)
        

@bot.event
async def on_command_error(ctx: discord.CommandsContext, err: discord.Error):
    if isinstance(err, discord.ext.commands.errors.CommandNotFound): # ignore errors which are commandnotfound errors (useless)
        return
    for id in config.Channels.log:
        await bot.get_channel(id).send(f"An error occured in {ctx.channel.name}:\n\n```{str(err)}```")


bot.run(os.environ["TOKEN"])
