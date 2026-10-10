import discord

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    @commands.command()
    async def hey(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(f"hey vro")    