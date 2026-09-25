# Ronnie Coleman Bot

This is a Ronnie Coleman-themed Discord bot built for my server, featuring calorie and protein tracking, macro estimations, custom training plans, a boxing interval timer, basic moderation, and a mini-game.

 Commands

 Fitness and nutrition

| Command | What it does |
| --- | --- |
| `!ron calc <m/f> <weight_kg> <height_cm> <age> <bf_percent>` | Estimates daily calories for cutting, maintaining and bulking, plus a protein target |
| `!ron add <calories> <protein> [meal name]` | Adds a meal to your totals for today |
| `!ron macros [@member]` | Shows today's calories and protein for you or someone else |
| `!ron workout [plan]` | Posts a training plan: `fullbody`, `2split` (upper/lower) or `bag` (heavy bag drills) |
| `!ron supps` | Lists a basic daily supplement stack |

`calc` uses the Katch-McArdle formula with a moderate activity factor of 1.55. Cutting is the estimate minus 500 kcal, bulking is plus 300 kcal, and the protein target is 2.2 g per kg of body weight. Because the formula works from lean body mass, the result depends on weight and body fat percentage. Height and age are checked but don't change the numbers. Treat all of it as a rough starting point.

Your daily totals reset automatically when the date changes on the machine the bot runs on. Example: `!ron add 650 45 chicken and rice`.

 Moderation and utilities

| Command | Required permission | What it does |
| --- | --- | --- |
| `!ron timer [rounds] [work_sec] [rest_sec]` | none | Interval timer with live countdown, defaults to 3 rounds of 180 s work and 60 s rest |
| `!ron clear [amount]` | Manage Messages | Deletes the given number of messages (default 5) |
| `!ron kick <@member> [reason]` | Kick Members | Kicks a member |
| `!ron ban <@member> [reason]` | Ban Members | Bans a member |
| `!ron mute <@member> <minutes> [reason]` | Moderate Members | Puts a member in timeout |
| `!ron unmute <@member>` | Moderate Members | Ends a timeout early |

`timer` is also available as `interval` or `rounds`, `mute` as `timeout`, and `unmute` as `untimeout`. Every moderation action comes with a Ronnie quote.

 Games and fun

| Command | What it does |
| --- | --- |
| `!ron quote` | Random Ronnie quote |
| `!ron fight <@opponent>` | Starts a fighting mini game |
| `!ron stats [@member]` | Shows wins, losses and win rate |

 Setup

You need Python 3.10 or newer and `discord.py` 2.x.

 1. Create the bot in Discord

Open the [Discord Developer Portal](https://discord.com/developers/applications), create an application and add a bot to it. Copy the bot token from the Bot page, and keep it to yourself. On the same page, switch on both privileged intents, **Server Members Intent** and **Message Content Intent**. The bot won't start without them.

To invite it, open the OAuth2 URL generator, select the `bot` scope and give it these permissions: Send Messages, Embed Links, Read Message History, Manage Messages, Kick Members, Ban Members and Moderate Members. For kicks, bans and timeouts to work, the bot's role also has to sit above the members it should act on in the server's role list.

 2. Install and configure

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
pip install -U discord.py
```

The bot reads its token from the `DISCORD_TOKEN` environment variable. Never write the token into the code or commit it to the repository.

On Linux and macOS:

```bash
export DISCORD_TOKEN="your-token-here"
```

On Windows (PowerShell):

```powershell
$env:DISCORD_TOKEN = "your-token-here"
```

 3. Run it

```bash
python ron.py
```

Start it from the project folder, because the bot loads its modules and `config.py` relative to the working directory. When everything is fine, the console shows one "Loaded" line per module and then that the bot is online.

 Project layout

```
ron.py            bot setup, help command, module loading
config.py         Ronnie quotes
cogs/
  fitness.py      calc, add, macros, workout, supps
  games.py        quote, fight, stats
  moderation.py   timer, clear, kick, ban, mute, unmute
bot_data.json     created at runtime
```

 Data and the mod log

The bot stores everything in `bot_data.json` next to `ron.py`: daily macro totals, fight records and one setting. The file is created the first time someone uses `add` or `fight`, and it contains Discord user IDs, so it is not part of the repository.

To have moderation actions posted to a log channel, set `mod_log_channel` in that file to the channel's ID (enable Developer Mode in Discord, then right-click the channel and choose Copy Channel ID). If the file doesn't exist yet, create it with this content:

```json
{
  "macros": {},
  "fights": {},
  "config": {
    "mod_log_channel": 123456789012345678
  }
}
```

Restart the bot afterwards. Without a log channel, the moderation commands simply skip the logging.

 Troubleshooting

The bot logs in but ignores commands: The Message Content Intent is probably off in the Developer Portal. Also check that you're using the `!ron ` prefix, including the space.

PrivilegedIntentsRequired on startup: Enable both the Server Members Intent and the Message Content Intent on the Bot page.

A module fails to load: The console prints a "Failed loading" line with the reason. The three cog files have to be in the `cogs/` folder, and `config.py` has to be next to `ron.py`.

Kick, ban or mute does nothing: The bot lacks the permission, or its role sits below the target member's highest role.
