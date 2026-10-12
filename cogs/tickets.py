import discord
import uuid
from discord import app_commands
from discord.ext import commands
from cogs.notcogs.utils import validate_server, log_action
from cogs.notcogs.config import Action, ticket_perms

class Tickets(commands.Cog):
    def __init__(self, _bot: discord.Bot):
        self.bot = _bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cogged tickets")

    @app_commands.command(name="openticket", description="Opens a ticket. Do not misuse. 120s cooldown")
    @app_commands.checks.cooldown(1, 120, key=lambda i: i.user.id)
    async def openticket(self, i: discord.Interaction):
        # no server validation check required here since this code considers the local scope
        role = i.guild.get_role(ticket_perms)
        await i.response.send_message("Creating ticket...", ephemeral=True)
        ticket_cat = discord.utils.get(i.guild.categories, name="Tickets") # relies on 'Tickets' name instead of id, since are we really going to have more than one 'Tickets' category?
        channel = await ticket_cat.create_text_channel("ticket-"+str(uuid.uuid4())[0:5], overwrites={i.guild.default_role: discord.PermissionOverwrite(view_channel=False), i.user: discord.PermissionOverwrite(view_channel=True), role: discord.PermissionOverwrite(view_channel=True)})
        await channel.send(f"Ticket opened by {i.user.mention}.")
        await i.followup.send(f"Created <#{channel.id}>", ephemeral=True)

    @app_commands.command(name="closeticket", description="Closes a ticket")
    async def closeticket(self, i: discord.Interaction, reason: str):
        role = i.guild.get_role(ticket_perms)
        if role not in i.user.roles:
            await i.response.send_message("you dont have the role for it", ephemeral=True)
            return

        if i.channel.name.startswith("ticket-"):
            await i.channel.send("Closing this ticket...")
            await log_action(self.bot, i.user, reason, Action.CLOSE_TICKET, "N/A", {"Ticket Name": i.channel.name})
            await i.channel.delete() # add a few checks or something, maybe make it so theres some sort of logs

async def setup(_bot: discord.Bot):
    await _bot.add_cog(Tickets(_bot))
