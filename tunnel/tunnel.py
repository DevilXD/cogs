from redbot.core import commands, checks
import discord


# start of awesome script

class Tunnel(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def tunnel(self, ctx, *, message):
		channel = self.bot.get_channel(779860372190396447)
		await channel.send(f"{ctx.author.mention} sennt {message}")