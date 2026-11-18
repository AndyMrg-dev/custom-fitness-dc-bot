import datetime
import discord
from discord.ext import commands


class Fitness(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='calc')
    async def calculate_target(self, ctx, gender: str, weight: float, height: float, age: int, bf: float):
        gender = gender.lower()
        if gender not in ['m', 'f', 'male', 'female']:
            return await ctx.send("🛑 Gender must be `m` or `f`!\nSyntax: `!ron calc <m/f> <weight_kg> <height_cm> <age> <bf_percent>`")

        if weight <= 0 or height <= 0 or age <= 0 or not (0 <= bf <= 60):
            return await ctx.send("🛑 Invalid physical parameters provided!")

        # Katch-McArdle, Aktivitätsfaktor 1.55
        lbm = weight * (1 - bf / 100)
        tdee = (370 + 21.6 * lbm) * 1.55

        cut = int(tdee - 500)
        maintain = int(tdee)
        bulk = int(tdee + 300)
        protein = int(weight * 2.2)

        embed = discord.Embed(
            title="🧮 Daily Targets",
            description=f"Stats for **{ctx.author.display_name}** ({gender.upper()}, {weight}kg, {height}cm, {age}y, {bf}% BF):",
            color=0x9b59b6
        )
        embed.add_field(name="📉 Cut", value=f"**{cut}** kcal", inline=True)
        embed.add_field(name="⚖️ Maintain", value=f"**{maintain}** kcal", inline=True)
        embed.add_field(name="📈 Bulk", value=f"**{bulk}** kcal", inline=True)
        embed.add_field(name="🥩 Daily Protein Target", value=f"**{protein}g**", inline=False)
        embed.set_footer(text="LIGHTWEIGHT BABY!")
        await ctx.send(embed=embed)

    @commands.command(name='add')
    async def add_macros(self, ctx, calories: int, protein: int, *, meal_name="Meal"):
        if calories < 0 or protein < 0:
            return await ctx.send("🛑 Values must be positive!")

        uid = str(ctx.author.id)
        today = str(datetime.date.today())

        # neuer Tag -> Zähler zurücksetzen
        entry = self.bot.db["macros"].get(uid)
        if not entry or entry.get("date") != today:
            self.bot.db["macros"][uid] = {"date": today, "calories": 0, "protein": 0}

        total = self.bot.db["macros"][uid]
        total["calories"] += calories
        total["protein"] += protein
        self.bot.save_data()

        embed = discord.Embed(
            title="🍗 Meal Logged",
            description=f"Added **{meal_name}**:\n🔥 +{calories} kcal | 🥩 +{protein}g Protein",
            color=0x2ecc71
        )
        embed.add_field(name="📊 Today's Total", value=f"🔥 **{total['calories']}** kcal | 🥩 **{total['protein']}g** Protein", inline=False)
        embed.set_footer(text="KEEP FEEDING THE MUSCLES!")
        await ctx.send(embed=embed)

    @commands.command(name='macros')
    async def show_macros(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        today = str(datetime.date.today())

        data = self.bot.db["macros"].get(str(target.id), {})
        if data.get("date") == today:
            cals = data.get("calories", 0)
            protein = data.get("protein", 0)
        else:
            cals = protein = 0

        embed = discord.Embed(title=f"📊 Daily Macros: {target.display_name}", color=0x3498db)
        embed.add_field(name="🔥 Calories", value=f"**{cals}** kcal", inline=True)
        embed.add_field(name="🥩 Protein", value=f"**{protein}g**", inline=True)
        embed.set_footer(text="YEAH BUDDY!")
        await ctx.send(embed=embed)

    @commands.command(name='log')
    async def log_set(self, ctx, exercise: str, weight: float, reps: int):
        if weight <= 0 or reps <= 0:
            return await ctx.send("🛑 Weight and reps must be greater than 0!")

        self.bot.sql.log_workout(ctx.author.id, ctx.author.display_name, exercise, weight, reps)

        embed = discord.Embed(
            title="🏋️ Set Logged",
            description=f"**{ctx.author.display_name}** logged **{exercise.capitalize()}**",
            color=0xe67e22
        )
        embed.add_field(name="⚖️ Weight", value=f"**{weight} kg**", inline=True)
        embed.add_field(name="🔁 Reps", value=f"**{reps}**", inline=True)
        embed.add_field(name="📊 Volume", value=f"**{weight * reps:.1f} kg**", inline=True)
        embed.set_footer(text="LIGHTWEIGHT BABY!")
        await ctx.send(embed=embed)

    @commands.command(name='pr')
    async def show_prs(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        stats = self.bot.sql.get_user_fitness_stats(target.id)

        if not stats:
            return await ctx.send(f"📭 No lifts logged for **{target.display_name}** yet.")

        embed = discord.Embed(title=f"🏆 Personal Records: {target.display_name}", color=0xf1c40f)
        for exercise, max_w, volume, sets in stats:
            embed.add_field(
                name=f"💪 {exercise.capitalize()}",
                value=f"PR: **{max_w} kg** | Sets: **{sets}** | Volume: **{volume:.0f} kg**",
                inline=False
            )
        embed.set_footer(text="YEAH BUDDY!")
        await ctx.send(embed=embed)

    @commands.command(name='top')
    async def show_leaderboard(self, ctx, *, exercise: str):
        leaders = self.bot.sql.get_exercise_leaderboard(exercise)

        if not leaders:
            return await ctx.send(f"📭 No records found for **{exercise}** yet.")

        embed = discord.Embed(title=f"👑 Leaderboard: {exercise.capitalize()}", color=0xe74c3c)
        medals = ["🥇", "🥈", "🥉"]
        for i, (name, best_w, volume) in enumerate(leaders):
            rank = medals[i] if i < 3 else f"#{i + 1}"
            embed.add_field(
                name=f"{rank} {name}",
                value=f"PR: **{best_w} kg** | Volume: **{volume:.0f} kg**",
                inline=False
            )
        embed.set_footer(text="AIN'T NUTHIN' BUT A PEANUT!")
        await ctx.send(embed=embed)

    @commands.command(name='workout')
    async def workout(self, ctx, plan_type="fullbody"):
        plan = plan_type.lower()

        if plan in ["fullbody", "gk"]:
            embed = discord.Embed(title="🏋️ Fullbody Routine", color=0x3498db)
            embed.add_field(name="Plan", value="• Squats: 3x6-8\n• Bench Press: 3x6-8\n• Deadlifts: 3x5\n• Pull-Ups: 3xMax\n• OHP: 3x8-10", inline=False)
        elif plan in ["2split", "upperlower", "2er"]:
            embed = discord.Embed(title="💪 2-Day Split (Upper / Lower)", color=0x9b59b6)
            embed.add_field(name="Day A: Upper", value="Bench Press 4x8, Barbell Rows 4x8, OHP 3x10, Pull-Ups 3xMax, Arms 3x12", inline=False)
            embed.add_field(name="Day B: Lower", value="Squats 4x6, RDLs 4x8, Lunges 3x10, Calf Raises 4x15", inline=False)
        elif plan in ["bag", "heavybag", "muaythai", "boxing"]:
            embed = discord.Embed(title="🥊 Heavy Bag Drill Routine", color=0xf1c40f)
            embed.add_field(name="Rounds", value="• R1: Jab, Teep, Footwork\n• R2: Jab-Cross-Low Kick combos\n• R3: High pace & Clinch knees", inline=False)
        else:
            return await ctx.send("❓ Unknown plan! Options: `fullbody`, `2split`, `bag`")

        embed.set_footer(text="LIGHTWEIGHT BABY!")
        await ctx.send(embed=embed)

    @commands.command(name='supps')
    async def supps(self, ctx):
        embed = discord.Embed(title="💊 Daily Supplement Stack", color=0x1abc9c)
        embed.add_field(name="Essentials", value="• **Creatine (5g)**: Power output & ATP\n• **Magnesium (300-400mg)**: Recovery & sleep\n• **Ashwagandha**: Cortisol management", inline=False)
        embed.set_footer(text="Consistency beats intensity!")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fitness(bot))