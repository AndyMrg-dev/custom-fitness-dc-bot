# Ronnie Coleman Bot

A Ronnie Coleman-themed Discord bot featuring workout and PR tracking, calorie & protein tracking, macro calculations, training plans, a boxing interval timer, server moderation with warning logs, a little game, and a C# command-line admin tool for inspecting the SQLite database.

## Commands

### Fitness and nutrition

| Command | What it does | 
| ----- | ----- | 
| `!ron calc <m/f> <weight_kg> <height_cm> <age> <bf_percent>` | Estimates daily calories for cutting, maintaining and bulking, plus a protein target | 
| `!ron add <calories> <protein> [meal name]` | Adds a meal to your totals for today | 
| `!ron macros [@member]` | Shows today's calories and protein for you or someone else | 
| `!ron log <exercise> <weight_kg> <reps>` | Logs a workout set to the SQLite database and calculates set volume | 
| `!ron pr [@member]` | Shows personal records, total sets and total volume per exercise | 
| `!ron top <exercise>` | Shows the server leaderboard (top 5) for a specific exercise | 
| `!ron workout [plan]` | Posts a training plan: `fullbody`, `2split` (upper/lower) or `bag` (heavy bag drills) | 
| `!ron supps` | Lists a basic daily supplement stack | 

`calc` uses the Katch-McArdle formula with a moderate activity factor of 1.55. Cutting is the estimate minus 500 kcal, bulking is plus 300 kcal, and the protein target is 2.2 g per kg of body weight. Because the formula works from lean body mass, the result depends on weight and body fat percentage. Height and age are checked but don't change the numbers. Treat all of it as a rough starting point.

Your daily macro totals reset automatically when the date changes on the machine the bot runs on. Example: `!ron add 650 45 chicken and rice`.

Workout sets logged with `log` are stored permanently in SQLite (`bot_data.db`). Exercise names are normalized to lowercase so `Bench` and `bench` group together. If an exercise name has spaces, wrap it in quotes when logging: `!ron log "bench press" 100 5`. For the leaderboard (`!ron top bench press`), quotes aren't needed.

### Moderation and utilities

| Command | Required permission | What it does | 
| ----- | ----- | ----- | 
| `!ron timer [rounds] [work_sec] [rest_sec]` | none | Interval timer with live countdown, defaults to 3 rounds of 180 s work and 60 s rest | 
| `!ron clear [amount]` | Manage Messages | Deletes the given number of messages (default 5) | 
| `!ron warn <@member> [reason]` | Manage Messages | Logs a warning for a member in the SQLite database and shows their total warning count | 
| `!ron warnings <@member>` | Manage Messages | Lists all logged warnings for a member with timestamps and moderator IDs | 
| `!ron clearwarnings <@member>` | Administrator | Deletes all logged warnings for a member from the database | 
| `!ron kick <@member> [reason]` | Kick Members | Kicks a member | 
| `!ron ban <@member> [reason]` | Ban Members | Bans a member | 
| `!ron mute <@member> <minutes> [reason]` | Moderate Members | Puts a member in timeout | 
| `!ron unmute <@member>` | Moderate Members | Ends a timeout early | 

`timer` is also available as `interval` or `rounds`, `warnings` as `warns`, `clearwarnings` as `clearwarns`, `mute` as `timeout`, and `unmute` as `untimeout`. Moderation actions come with a Ronnie quote and are forwarded to the mod log channel if configured.

### Games and fun

| Command | What it does | 
| ----- | ----- | 
| `!ron quote` | Random Ronnie quote | 
| `!ron fight <@opponent>` | Starts a fight against another member. The outcome is random | 
| `!ron stats [@member]` | Shows wins, losses and win rate | 

## Setup

You need Python 3.10 or newer and `discord.py` 2.x. SQLite support uses Python's built-in `sqlite3` module, so no extra database packages are required.

### 1. Create the bot in Discord

Open the [Discord Developer Portal](https://discord.com/developers/applications), create an application and add a bot to it. Copy the bot token from the Bot page, and keep it to yourself. On the same page, switch on both privileged intents, **Server Members Intent** and **Message Content Intent**. The bot won't start without them.

To invite it, open the OAuth2 URL generator, select the `bot` scope and give it these permissions: Send Messages, Embed Links, Read Message History, Manage Messages, Kick Members, Ban Members and Moderate Members. For kicks, bans and timeouts to work, the bot's role also has to sit above the members it should act on in the server's role list.

### 2. Install and configure

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

### 3. Run it

```bash
python ron.py
```

Start it from the project folder, because the bot loads its modules, `database.py` and `config.py` relative to the working directory. When everything is fine, the console shows one "Loaded" line per module and then that the bot is online.

## Project layout

```text
ron.py              bot setup, help command, module loading
database.py         SQLite manager (users, workouts, moderation_logs)
config.py           Ronnie quotes
cogs/
  fitness.py        calc, add, macros, log, pr, top, workout, supps
  games.py          quote, fight, stats
  moderation.py   timer, clear, warn, warnings, clearwarnings, kick, ban, mute, unmute
admin_cli/
  Program.cs        C# console admin tool for querying bot_data.db
  admin_cli.csproj  .NET 8 project file (Microsoft.Data.Sqlite)
bot_data.db         SQLite database, created at runtime
bot_data.json       JSON storage, created at runtime
```

## Data and the mod log

The bot uses two local files next to `ron.py` to store data:

* **`bot_data.db` (SQLite):** Created automatically on startup by `database.py`. It stores relational data across three tables (`users`, `workouts`, and `moderation_logs`) with foreign keys enabled, powering the workout tracker (`log`, `pr`, `top`) and the warning system (`warn`, `warnings`, `clearwarnings`).

* **`bot_data.json` (JSON):** Stores daily macro totals, fight records and the mod log channel configuration. The file is created the first time someone uses `add` or `fight`.

Both files contain Discord user IDs and are excluded from the repository via `.gitignore`.

To have moderation actions (including `warn` and `clearwarnings`) posted to a log channel, set `mod_log_channel` in `bot_data.json` to the channel's ID (enable Developer Mode in Discord, then right-click the channel and choose Copy Channel ID). If the file doesn't exist yet, create it with this content:

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

## C# Admin CLI

The `admin_cli/` folder contains an optional C# console application that connects directly to `bot_data.db` via `Microsoft.Data.Sqlite`. It allows administrators to inspect and manage database records locally without running the Discord bot:

* List all registered users and their last activity timestamp
* View the exercise leaderboard ranked by personal record and total volume
* Check personal records, set counts and total volume for a specific user ID
* List all logged moderation warnings or clear warnings for a user ID

### Running the Admin CLI

Requires the **.NET 8 SDK**. From the repository root:

```bash
cd admin_cli
dotnet run
```

The tool automatically looks for `../bot_data.db` in the project root. Make sure `bot_data.db` has been created by starting `ron.py` (or running a database operation) at least once beforehand.

## Troubleshooting

The bot logs in but ignores commands: The Message Content Intent is probably off in the Developer Portal. Also check that you're using the `!ron ` prefix, including the space.

PrivilegedIntentsRequired on startup: Enable both the Server Members Intent and the Message Content Intent on the Bot page.

A module fails to load: The console prints a "Failed loading" line with the reason. The three cog files have to be in the `cogs/` folder, and `database.py` and `config.py` have to be next to `ron.py`.

Kick, ban or mute does nothing: The bot lacks the permission, or its role sits below the target member's highest role.

Admin CLI says database not found: Start the Python bot once so `bot_data.db` gets generated in the root folder, then run `dotnet run` inside `admin_cli/` again.