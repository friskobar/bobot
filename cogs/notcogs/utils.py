import discord
import datetime as dt
from cogs.notcogs.config import servers
from cogs.notcogs.config import Action
from cogs.notcogs.config import Channels

async def validate_server(i: discord.Interaction) -> bool:
    if i.guild.id in servers:
        return True
    else:
        return False
    
async def log_action(bot: discord.Bot, actor: discord.Member, reason: str, action: config.Action, target: discord.Member, extra: dict = {}) -> None:
    em = discord.Embed(title=action.name,
                       color=discord.Color.from_rgb(10, 10, 12),
                       timestamp=dt.datetime.now()
                       )

    em.set_footer(text=f"{actor.id} | {actor.global_name}")
    em.add_field(name="Offender", value=f"{target.global_name} ({target.id})")
    em.add_field(name="Reason", value=reason)
    if extra != {}:
        for key, value in extra.items():
            em.add_field(name=key, value=value)

    for id in Channels.log:
        await bot.get_channel(id).send("Log", embeds=[em])
