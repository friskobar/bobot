import discord
import uuid
import json
import pandas as pd
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
    async def openticket(self, i: discord.Interaction, reason:str):
        print(i.user.global_name + " tried to open a ticket.")
        # no server validation check required here since this code considers the local scope
        role = i.guild.get_role(ticket_perms)
        await i.response.send_message("Creating ticket...", ephemeral=True)
        ticket_uuid = str(uuid.uuid4())[0:7]
        ticket_cat = discord.utils.get(i.guild.categories, name="Tickets") # relies on 'Tickets' name instead of id, since are we really going to have more than one 'Tickets' category?
        channel = await ticket_cat.create_text_channel("ticket-"+ticket_uuid, overwrites={i.guild.default_role: discord.PermissionOverwrite(view_channel=False), i.user: discord.PermissionOverwrite(view_channel=True), role: discord.PermissionOverwrite(view_channel=True)})
        await channel.send(f"Ticket opened by {i.user.mention}.\nReason: " + reason)
        await i.followup.send(f"Created <#{channel.id}>", ephemeral=True)
        
        t_channels = json.loads(pd.read_json("tickets.json").to_json())
        backup = t_channels

        #info is stored as:
        #{
        #   "channel_id" : { # Storing tickets per channel id cause its easier to look em up
        #       "owner"     : vro,
        #       "ticket_id" : guh,
        #    }
        #
        user_id = str(i.user.id) #poly i hope youre having a great day when youre reviewing this code
        ticket_entry = {
            "owner"     : user_id,
            "ticket_id" : ticket_uuid
        }
        
        t_channels[channel.id] = ticket_entry
        
        with open("tickets.json", "w") as f:
            s = json.dumps(t_channels, indent=4)
            f.write(s)
        
        await log_action(self.bot, i.user, reason, Action.OPEN_TICKET, "N/A", {"Ticket ID: " : ticket_uuid, "Channel ID: " : str(channel.id)})

    @app_commands.command(name="closeticket", description="Closes a ticket")
    async def closeticket(self, i: discord.Interaction, reason: str):
        print(i.user.global_name + " tried to close a ticket.")
        role = i.guild.get_role(ticket_perms)
        if role not in i.user.roles:
            await i.response.send_message("you dont have the role for it", ephemeral=True)
            return
        #TODO 
        t_channels = json.loads(pd.read_json("tickets.json").to_json())
        
        if i.channel.name.startswith("ticket-"):
            await i.channel.send("Closing this ticket...")
            if t_channels[str(i.channel.id)]:
                owner = await i.guild.fetch_member(t_channels[str(i.channel.id)]["owner"])
                t_channels.pop(str(i.channel.id))
                try:
                    with open("tickets.json", "w") as f:
                        s = json.dumps(t_channels, indent=4)
                        f.write(s)
                except:
                    with open("tickets.json", "w") as f:
                        f.write(backup)
                if owner:
                    await log_action(self.bot, i.user, reason, Action.CLOSE_TICKET, "N/A", {"Ticket Name": i.channel.name, "Ticket Owner": owner.mention})
                else:
                    await log_action(self.bot, i.user, reason, Action.CLOSE_TICKET, "N/A", {"Ticket Name": i.channel.name, "Ticket Owner": "Couldn't find logs for this channel in tickets.json."}) #place log_action after delete. generally, you do first and log later.
            await i.channel.delete() # add a few checks or something, maybe make it so theres some sort of logs

async def setup(_bot: discord.Bot):
    await _bot.add_cog(Tickets(_bot))
