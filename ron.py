import os
import json
import asyncio
import discord
from discord.ext import commands

DATA_FILE = "bot_data.json"

def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"macros": {}, "fights": {}, "config": {"mod_log_channel": None}}

def save_db(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!ron ", intents=intents, help_command=None)
bot.db = load_db()
bot.save_data = lambda: save_db(bot.db)

@bot.event
async def on_ready():
    print(f"💪 Online as {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name="!ron help | LIGHTWEIGHT BABY!"))

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("🛑 Missing arguments! Check `!ron help`.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ You don't have permission for this, Champ!")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("🛑 Invalid input format. Check parameter types.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"Unhandled error in {ctx.command}: {error}")

@bot.command(name='help')
async def custom_help(ctx: commands.Context):
    embed = discord.Embed(
        title="💪 Ronnie Coleman Bot Commands",
        description="All commands and modules at a glance.",
        color=0x3498db
    )
    embed.add_field(
        name="🏋️ Fitness & Nutrition",
        value=(
            "`!ron calc <m/f> <weight> <height> <age> <bf%>`\n"
            "`!ron add <cals> <protein> [meal]`\n"
            "`!ron macros [@member]`\n"
            "`!ron workout [fullbody/2split/bag]`\n"
            "`!ron supps`"
        ),
        inline=False
    )
    embed.add_field(
        name="🛡️ Moderation & Utilities",
        value=(
            "`!ron timer [rounds] [work_sec] [rest_sec]`\n"
            "`!ron clear <amount>`\n"
            "`!ron kick <@member> [reason]`\n"
            "`!ron ban <@member> [reason]`\n"
            "`!ron mute <@member> <minutes> [reason]`\n"
            "`!ron unmute <@member>`"
        ),
        inline=False
    )
    embed.add_field(
        name="🥊 Games & Fun",
        value=(
            "`!ron quote`\n"
            "`!ron fight <@opponent>`\n"
            "`!ron stats [@member]`"
        ),
        inline=False
    )
    embed.set_footer(text="YEAH BUDDY! AIN'T NUTHIN' BUT A PEANUT!")
    await ctx.send(embed=embed)

async def main():
    async with bot:
        for cog in ['cogs.moderation', 'cogs.fitness', 'cogs.games']:
            try:
                await bot.load_extension(cog)
                print(f"✅ Loaded: {cog}")
            except Exception as e:
                print(f"❌ Failed loading {cog}: {e}")
        
        await bot.start('DISCORD BOT TOKEN HERE')

if __name__ == "__main__":
    asyncio.run(main())