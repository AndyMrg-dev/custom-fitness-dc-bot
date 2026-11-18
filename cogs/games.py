import random
import discord
from discord.ext import commands
from config import RONNIE_QUOTES

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _record_win(self, winner_id: str, loser_id: str):
        fights = self.bot.db.setdefault("fights", {})
        
        for uid in (winner_id, loser_id):
            if uid not in fights:
                fights[uid] = {"wins": 0, "losses": 0}

        fights[winner_id]["wins"] += 1
        fights[loser_id]["losses"] += 1
        self.bot.save_data()

    @commands.command(name='quote')
    async def ronnie_quote(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🗣️ Ronnie says...",
            description=f"*{random.choice(RONNIE_QUOTES)}*",
            color=0x3498db
        )
        embed.set_footer(text="LIGHTWEIGHT BABY!")
        await ctx.send(embed=embed)

    @commands.command(name='fight')
    async def fight(self, ctx: commands.Context, opponent: discord.Member):
        if opponent == ctx.author:
            return await ctx.send("You can't fight yourself, hit the heavy bag!")
        if opponent.bot:
            return await ctx.send("Bots don't bleed, pick a human!")

        events = [
            (f"{ctx.author.mention} landed a clean **Right Cross** KO in R1!", ctx.author, opponent),
            (f"{ctx.author.mention} locked in a tight **Guillotine**!", ctx.author, opponent),
            (f"{opponent.mention} caught you with a brutal counter hook!", opponent, ctx.author),
            (f"{opponent.mention} dominated the clinch and took the decision.", opponent, ctx.author),
            (f"{ctx.author.mention} chopped them down with **Low Kicks**!", ctx.author, opponent)
        ]

        text, winner, loser = random.choice(events)
        self._record_win(str(winner.id), str(loser.id))

        embed = discord.Embed(
            title="🥊 Fight Club Match",
            description=f"{ctx.author.display_name} vs {opponent.display_name}\n\n💥 {text}",
            color=0x2ecc71 if winner == ctx.author else 0xe74c3c
        )
        embed.set_footer(text="YEAH BUDDY!")
        await ctx.send(embed=embed)

    @commands.command(name='stats')
    async def fight_stats(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        stats = self.bot.db.get("fights", {}).get(str(target.id), {"wins": 0, "losses": 0})
        
        wins, losses = stats["wins"], stats["losses"]
        total = wins + losses
        ratio = (wins / total * 100) if total else 0.0

        embed = discord.Embed(title=f"📊 Record: {target.display_name}", color=0xf1c40f)
        embed.add_field(name="Fights", value=str(total), inline=True)
        embed.add_field(name="Wins", value=str(wins), inline=True)
        embed.add_field(name="Losses", value=str(losses), inline=True)
        embed.add_field(name="Winrate", value=f"{ratio:.1f}%", inline=False)
        embed.set_footer(text="LIGHTWEIGHT BABY!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))