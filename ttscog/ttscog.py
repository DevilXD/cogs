from redbot.core import commands, checks, Config
from .helper import helper
from .custom import FFmpegPCMAudio
from io import BytesIO
import discord
import traceback

from gtts import gTTS


class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Config.get_conf(self, 828282859272, force_registration=True)
        default_guild = {
            "channel": ""
        }
        self.db.register_guild(**default_guild)
        self._locks = set()

    @commands.command()
    async def connect(self, ctx, channel=None):
        await helper.connect(ctx, channel)
        
    @commands.command()
    async def disconnect(self, ctx):
        await helper.disconnect(ctx)
        
    @commands.command()
    async def setttschan(self, ctx, channel: discord.TextChannel):
        await self.db.guild(ctx.guild).channel.set(channel.id)
        await ctx.send(f"TTS channel has been set to {channel.name}")
        
    #@commands.command()
    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        channel = await self.db.guild(msg.guild).channel()
        #channel = 830384640568066069
        if msg.channel.id != channel:
            return
        # channel = self.bot.get_channel(channel)
    
        if msg.author in self._locks:
            # their message being processed
            return
        try:
            self._locks.append(msg.author)
            
            vc = msg.voice_client # We use it more then once, so make it an easy variable
            if not vc:
                # We are not currently in a voice channel
                await mag.channel.send("I need to be in a voice channel to do this, please use the connect command.")
                return
            
            # Lets prepare our text, and then save the audio file
            fp = BytesIO()
            tts = gTTS(text=f"{msg.author.name} said {text}", lang="en")
            tts.write_to_fp(fp)
            fp.seek(0)
            # tts.save("text.mp3")
            
            try:
                # Lets play that mp3 file in the voice channel
                vc.play(FFmpegPCMAudio(fp.read(), pipe = True), after=lambda e: print(f"Finished playing: {e}"))
            
                # Lets set the volume to 1
                vc.source = discord.PCMVolumeTransformer(vc.source)
                vc.source.volume = 1
            except:
                await msg.channel.send("An error occured.")
        finally:
            await self._locks.discard(msg.author)
        bot.process_commands(msg)