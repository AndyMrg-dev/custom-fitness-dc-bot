import random
import asyncio
import datetime
import discord
from discord.ext import commands
from config import RONNIE_CLEAR_QUOTES, RONNIE_KICK_QUOTES, RONNIE_BAN_QUOTES, RONNIE_MUTE_QUOTES

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def _log(self, guild: discord.Guild, embed: discord.Embed):
        log_id = self.bot.db["config"].get("mod_log_channel")
        if log_id and (ch := guild.get_channel(log_id)):
            await ch.send(embed=embed)

    @commands.command(name='timer', aliases=['interval', 'rounds'])
    async def interval_timer(self, ctx: commands.Context, rounds: int = 3, round_time: int = 180, rest_time: int = 60):
        if rounds <= 0 or round_time <= 0 or rest_time < 0:
            return await ctx.send("🛑 Rounds and times must be greater than 0!")

        msg = await ctx.send(f"🥊 **Interval Timer Initialized:** {rounds} Rounds ({round_time}s work / {rest_time}s rest)")
        await asyncio.sleep(3)

        for i in range(1, rounds + 1):
            # Work Phase
            embed = discord.Embed(title=f"🥊 Round {i} / {rounds} - WORK!", description=f"⏱️ Left: `{round_time}`s", color=0xe74c3c)
            await msg.edit(content=f"🔔 {ctx.author.mention} **Round {i} START!**", embed=embed)

            left = round_time
            while left > 0:
                step = min(5, left)
                await asyncio.sleep(step)
                left -= step
                if left > 0 and left % 5 == 0:
                    embed.description = f"⏱️ Left: `{left}`s"
                    try: await msg.edit(embed=embed)
                    except discord.HTTPException: pass

            # Rest Phase
            if i < rounds:
                embed = discord.Embed(title=f"🔔 Round {i} Complete - REST!", description=f"🥤 Rest: `{rest_time}`s", color=0xf1c40f)
                await msg.edit(content=f"🥤 {ctx.author.mention} **REST TIME!**", embed=embed)

                left = rest_time
                while left > 0:
                    step = min(5, left)
                    await asyncio.sleep(step)
                    left -= step
                    if left > 0 and left % 5 == 0:
                        embed.description = f"🥤 Rest: `{left}`s"
                        try: await msg.edit(embed=embed)
                        except discord.HTTPException: pass

        embed = discord.Embed(title="🏆 Workout Finished!", description=f"Completed all {rounds} rounds!", color=0x2ecc71)
        await msg.edit(content=f"🎉 {ctx.author.mention} **DONE!**", embed=embed)

    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int = 5):
        if amount <= 0:
            return await ctx.send("Amount must be greater than 0!")

        deleted = await ctx.channel.purge(limit=amount + 1)
        count = len(deleted) - 1
        
        msg = await ctx.send(f"🧹 **{random.choice(RONNIE_CLEAR_QUOTES)}** ({count} messages purged)")
        
        log = discord.Embed(title="🧹 Purged Messages", description=f"Channel: {ctx.channel.mention}\nAmount: {count}\nMod: {ctx.author.mention}", color=0xe67e22)
        await self._log(ctx.guild, log)
        await msg.delete(delay=3)

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Not enough effort"):
        if member == ctx.author:
            return await ctx.send("Can't kick yourself!")

        await member.kick(reason=reason)
        embed = discord.Embed(title="🥾 Member Kicked", description=f"**{random.choice(RONNIE_KICK_QUOTES)}**\n\nUser: {member.display_name}\nReason: {reason}", color=0xe67e22)
        await ctx.send(embed=embed)
        await self._log(ctx.guild, embed)

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Violation"):
        if member == ctx.author:
            return await ctx.send("Can't ban yourself!")

        await member.ban(reason=reason)
        embed = discord.Embed(title="🔨 Member Banned", description=f"**{random.choice(RONNIE_BAN_QUOTES)}**\n\nUser: {member.display_name}\nReason: {reason}", color=0xe74c3c)
        await ctx.send(embed=embed)
        await self._log(ctx.guild, embed)

    @commands.command(name='mute', aliases=['timeout'])
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, minutes: int, *, reason: str = "Cooling off"):
        if minutes <= 0:
            return await ctx.send("Duration must be at least 1 minute!")

        await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
        embed = discord.Embed(title="🤫 Timeout Applied", description=f"**{random.choice(RONNIE_MUTE_QUOTES)}**\n\nUser: {member.display_name}\nDuration: {minutes}m\nReason: {reason}", color=0xf1c40f)
        await ctx.send(embed=embed)
        await self._log(ctx.guild, embed)

    @commands.command(name='unmute', aliases=['untimeout'])
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"🔊 Timeout cleared for **{member.display_name}**!")

async def setup(bot):
    await bot.add_cog(Moderation(bot))