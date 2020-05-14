import discord
from discord.utils import get
from redbot.core import commands

class ColorRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    color_roles = [
        "Black",
        "Yellow",
        "Orange",
        "Red",
        "Blue",
        "Purple",
        "Cyan",
        "Green",
    ]
    
    @commands.command()
    async def color(self, ctx, color: str):
        if self.color_roles in ctx.author.roles:
            for role in ctx.author.roles:
                role = get(ctx.guild, name=color)
                await self.bot.remove_role(ctx.author, role)
                await self.bot.add_role(ctx.author, role)
                await ctx.send("Gave role {} to {}".format(color, ctx.author))
        else:
            await ctx.send("No such role")