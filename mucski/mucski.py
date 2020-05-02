import discord
import random
import math
import asyncio
from .adminutils import AdminUtils
from .games import Games
from .pet import Pet
from .shop import Shop

from redbot.core import checks, commands, Config
from redbot.core.utils.chat_formatting import box, humanize_timedelta, pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from datetime import datetime, timedelta
from redbot.core.utils.predicates import MessagePredicate

#randomstuff
from .randomstuff import worklist
from .randomstuff import searchlist
from .randomstuff import bad_location

class Mucski(AdminUtils, Pet, Shop, Games, commands.Cog):
    def __init__(self, bot):
        self.conf = Config.get_conf(self, 82838559382, force_registration=True)
        defaults = {
            "cookies": 0,
            "daily_stamp": 0,
            "steal_stamp": 0,
            "work_stamp": 0,
            "pet_stamp": 0,
            "pets": {
                "name": "None",
                "hunger": 0,
                "happiness": 0,
                "owned": "None",
            },
            "items": [],
        }
        self.conf.register_user(**defaults)

    @AdminUtils.cookie.command()
    async def balance(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        cookie = await self.conf.user(member).cookies()
        await ctx.send(f"{member.name} has {cookie} cookies.")
    
    @AdminUtils.cookie.command()
    async def profile(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        now = datetime.utcnow().replace(microsecond=0)
        cookie = await self.conf.user(member).cookies()
        daily_stamp = await self.conf.user(member).daily_stamp()
        daily_stamp = datetime.fromtimestamp(daily_stamp)
        daily = daily_stamp - now
        steal_stamp = await self.conf.user(member).steal_stamp()
        steal_stamp = datetime.fromtimestamp(steal_stamp)
        steal = steal_stamp - now
        pet = await self.conf.user(member).pet()
        e = discord.Embed(timestamp=datetime.utcnow())
        e.set_author(name=f"{member.name}'s profile", icon_url=member.avatar_url)
        e.set_thumbnail(url=member.avatar_url)
        e.add_field(name="Cookies owned", value=cookie)
        if now < daily_stamp:
            e.add_field(name="Daily on cooldown", value="YES")
            e.add_field(name="Cooldown remaining", value=humanize_timedelta(timedelta=daily))
        else:
            e.add_field(name="Daily on cooldown", value="NO")
        if now < steal_stamp:
            e.add_field(name="Steal on cooldown", value="YES")
            e.add_field(name="Cooldown remaining", value=humanize_timedelta(timedelta=steal))
        else:
            e.add_field(name="Steal on cooldown", value="NO")
        if pet is None:
            e.add_field(name="Pet", value="None")
        else:
            e.add_field(name="Pet", value=f"{pet}")
        await ctx.send(embed=e)
    
    @AdminUtils.cookie.command(name="cookieboards", aliases=['lb', 'cb'])
    async def cookieboards(self, ctx):
        userinfo = await self.conf.all_users()
        if not userinfo:
            await ctx.send("Start playig by working, searching, scouting, or claiming your first daily, before you brag.")
        sorted_acc = sorted(userinfo.items(), key = lambda x: x[1]['cookies'], reverse=True)[:50]
        text_list = []
        for i, (user_id, account) in enumerate(sorted_acc, start=1):
            user_id = ctx.guild.get_member(user_id)
            if len(user_id.display_name) < 15:
                text_list.append(f"#{i:2}. {user_id.display_name:<15} {account['cookies']:>14} 🍪")
            else:
                text_list.append(f"#{i:2}. {user_id.display_name[:13]:<13}.. {account['cookies']:>14} 🍪")
        text = '\n'.join(text_list)
        page_list = []
        for page_num, page in enumerate(pagify(text, delims=["\n"], page_length=1500), start=1):
            e = discord.Embed(color = await ctx.bot.get_embed_color(location=ctx.channel), description = box(f"Cookieboards", lang="prolog") + (box(page, lang="md")))
            e.set_footer(text = f"Page {page_num}/{math.ceil(len(text) / 1500)}")
        page_list.append(e)
        return await menu(ctx, page_list, DEFAULT_CONTROLS)
    
    @AdminUtils.cookie.command()
    async def work(self, ctx):
        work_stamp = await self.conf.user(ctx.author).work_stamp()
        work_stamp = datetime.fromtimestamp(work_stamp)
        work_timer = timedelta(minutes=5)
        now = datetime.utcnow().replace(microsecond=0)
        next_stamp = work_timer + now
        remaining = work_stamp - now
        if now < work_stamp:
            return await ctx.send(f"Yo, I'm not made out of money, wait {humanize_timedelta(timedelta=remaining)}")
        r = random.choice(list(worklist.keys()))
        await ctx.send(worklist[r])
        pred = MessagePredicate.lower_equal_to(r, ctx)
        try:
            await ctx.bot.wait_for("message", timeout=7, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send("Too lazy to put in any effort eh? No cookies for you!")
        cookie = await self.conf.user(ctx.author).cookies()
        earned = random.randint(50,500)
        cookie += earned
        await self.conf.user(ctx.author).cookies.set(cookie)
        await ctx.send(f"Well done. You earned ``{earned}`` cookies for your hard work")
        await self.conf.user(ctx.author).work_stamp.set(next_stamp.timestamp())
    
    @AdminUtils.cookie.command()
    async def search(self, ctx):
        r = random.sample(list(searchlist.keys()), 3)
        await ctx.send("🔎 Choose a location to search for cookies 🔎")
        await ctx.send(f"``{r[0]}``  ``{r[1]}``  ``{r[2]}``")
        pred = MessagePredicate.lower_contained_in(r, ctx)
        try:
            msg = await ctx.bot.wait_for("message", timeout=7, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send("Yeah.. Maybe try picking a location next time?")
        if msg.content.lower() in bad_location:
            return await ctx.send(searchlist[msg.content.lower()])
        cookie = await self.conf.user(ctx.author).cookies()
        earned = random.randint(20,200)
        cookie += earned
        await self.conf.user(ctx.author).cookies.set(cookie)
        await ctx.send(searchlist[msg.content.lower()].format(earned))
            
    @AdminUtils.cookie.command()
    async def scout(self, ctx):
        pass
      
    @AdminUtils.cookie.command()
    async def daily(self, ctx):
        now = datetime.utcnow().replace(microsecond=0)
        daily_stamp = await self.conf.user(ctx.author).daily_stamp()
        daily_stamp = datetime.fromtimestamp(daily_stamp)
        daily_timer = timedelta(hours=12)
        next_stamp = daily_timer + now
        remaining = daily_stamp - now
        if now < daily_stamp:
            return await ctx.send(f"Yeah .. which part of daily you didn't understand? Wait {humanize_timedelta(timedelta=remaining)}")
        cookie = await self.conf.user(ctx.author).cookies()
        cookie += 1000
        await self.conf.user(ctx.author).cookies.set(cookie)
        await ctx.send("Claimed your 1000 daily cookies, woo!")
        await self.conf.user(ctx.author).daily_stamp.set(next_stamp.timestamp())
        
    @AdminUtils.cookie.command()
    async def give(self, ctx, amount, member: discord.Member):
        sender = await self.conf.user(ctx.author).cookies()
        try:
            amount = int(amount)
        except ValueError:
            if amount == "all":
                amount = sender
            else:
                amount = None
                msg = "Try it with an actual amount this time."
        finally:
            if amount is not None:
                if amount >= 0:
                    if sender <= 0:
                        msg = "Nope."
                        return
                    sender -= amount
                    await self.conf.user(ctx.author).cookies.set(sender)
                    receiver = await self.conf.user(member).cookies()
                    receiver += amount
                    if receiver <= 0:
                        msg = "Excuse you, are you trying to steal from me?!"
                        return
                    await self.conf.user(member).cookies.set(receiver)
                    msg = f"``{ctx.author.name}`` sent ``{amount}`` cookies to ``{member.name}`` 🍪🎉"
                else:
                    msg = "Yeah .. go trick someone else!"
        await ctx.send(msg)