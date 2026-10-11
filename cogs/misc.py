import discord
from discord import app_commands
from discord.ext import commands
from cogs.notcogs.utils import validate_server, log_action
from cogs.notcogs.config import Action

class Misc(commands.Cog):
    def __init__(self, _bot: discord.Bot):
        self.bot = _bot
    @commands.Cog.listener()
    async def on_ready(self):
        print("Cogged misc")
    @app_commands.command(name="bing", description="Bing")
    async def clean(self, i: discord.Interaction):
        await i.response.send_message("bong")
    @app_commands.command(name="help", description="Shows all commands.")
    async def help(self, i: discord.Interaction):
        desc = """
        1. __**/timeout [@offender] [duration] [reason]**__
            - Duration must be in the format `Xd Xh Xm` where X is the duration of the unit of time.
            - For example, `1d 10h 15m` as the duration will set the user's timeout to be *one day, ten hours and fifteen minutes*.
            - Discord's API has a 28 day maximum time for a timeout, so exceeding that will probably fallback to 28 days. Failing to mention a proper duration will not time the user out.

        2. __**/untimeout [@offender] [reason]**__
            - Removes timeout from a user.

        3. __**/kick [@offender] [reason]**__
            - Kicks a user from the server.
        
        4. __**/clean [@offender] [count] [reason]**__
            - Cleans `count` messages from a channel from a user.
            - Count is an integer.
        """
        help_embed = discord.Embed(
            title="Help",
            description=desc
        )

        await i.response.send_message(embeds=[help_embed])

async def setup(_bot: discord.Bot):
    await _bot.add_cog(Misc(_bot))
