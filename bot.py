from discord.ext import tasks

import os
import json
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
display_channel_raw = os.getenv("DISPLAY_CHANNEL_ID")
command_channel_raw = os.getenv("COMMAND_CHANNEL_ID")

if not TOKEN:
    raise ValueError("Missing DISCORD_TOKEN environment variable")
if not display_channel_raw:
    raise ValueError("Missing DISPLAY_CHANNEL_ID environment variable")
if not command_channel_raw:
    raise ValueError("Missing COMMAND_CHANNEL_ID environment variable")

DISPLAY_CHANNEL_ID = int(display_channel_raw)
COMMAND_CHANNEL_ID = int(command_channel_raw)

DATA_FILE = "boss_timers.json"
MESSAGE_ID_FILE = "display_message.json"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

BOSSES = {
    "croms manikin": {
        "display": "Crom's Manikin",
        "group": "ENDGAME",
        "respawn_minutes": 96 * 60,
        "window_minutes": 24 * 60,
        "aliases": ["manikin", "crom", "croms", "crom's manikin"],
    },
    "dhiothu": {
        "display": "Dhiothu",
        "group": "ENDGAME",
        "respawn_minutes": 34 * 60,
        "window_minutes": 28 * 60,
        "aliases": ["dino", "dhio", "d2", "dhiothu"],
    },
    "bloodthorn": {
        "display": "Bloodthorn",
        "group": "ENDGAME",
        "respawn_minutes": 34 * 60,
        "window_minutes": 28 * 60,
        "aliases": ["bt", "bloodthorn"],
    },
    "gelebron": {
        "display": "Gelebron",
        "group": "ENDGAME",
        "respawn_minutes": 32 * 60,
        "window_minutes": 28 * 60,
        "aliases": ["gele", "gelebron"],
    },
    "proteus": {
        "display": "Proteus",
        "group": "ENDGAME",
        "respawn_minutes": 18 * 60,
        "window_minutes": 15,
        "aliases": ["prot", "base", "prime", "proteus"],
    },
    "necromancer": {
        "display": "Necromancer",
        "group": "MIDRAID",
        "respawn_minutes": 22 * 60,
        "window_minutes": 16 * 60,
        "aliases": ["necro", "necromancer"],
    },
    "mordris": {
        "display": "Mordris",
        "group": "MIDRAID",
        "respawn_minutes": 20 * 60,
        "window_minutes": 16 * 60,
        "aliases": ["mord", "mordy", "mordris"],
    },
    "hrungnir": {
        "display": "Hrungnir",
        "group": "MIDRAID",
        "respawn_minutes": 22 * 60,
        "window_minutes": 16 * 60,
        "aliases": ["hrung", "muk", "hrungnir"],
    },
    "aggragoth": {
        "display": "Aggragoth",
        "group": "MIDRAID",
        "respawn_minutes": 20 * 60,
        "window_minutes": 16 * 60,
        "aliases": ["aggy", "aggragoth"],
    },
    "215": {
        "display": "215",
        "group": "EDL",
        "respawn_minutes": 2 * 60 + 14,
        "window_minutes": 5,
        "aliases": ["215", "unox"],
    },
    "210": {
        "display": "210",
        "group": "EDL",
        "respawn_minutes": 2 * 60 + 5,
        "window_minutes": 5,
        "aliases": ["210"],
    },
    "205": {
        "display": "205",
        "group": "EDL",
        "respawn_minutes": 1 * 60 + 57,
        "window_minutes": 4,
        "aliases": ["205"],
    },
    "200": {
        "display": "200",
        "group": "EDL",
        "respawn_minutes": 1 * 60 + 48,
        "window_minutes": 5,
        "aliases": ["200"],
    },
    "195": {
        "display": "195",
        "group": "EDL",
        "respawn_minutes": 1 * 60 + 29,
        "window_minutes": 4,
        "aliases": ["195"],
    },
    "190": {
        "display": "190",
        "group": "EDL",
        "respawn_minutes": 1 * 60 + 21,
        "window_minutes": 3,
        "aliases": ["190"],
    },
    "185": {
        "display": "185",
        "group": "EDL",
        "respawn_minutes": 1 * 60 + 12,
        "window_minutes": 3,
        "aliases": ["185"],
    },
    "180": {
        "display": "180",
        "group": "DL",
        "respawn_minutes": 1 * 60 + 28,
        "window_minutes": 3,
        "aliases": ["180", "snorri"],
    },
    "170": {
        "display": "170",
        "group": "DL",
        "respawn_minutes": 1 * 60 + 18,
        "window_minutes": 3,
        "aliases": ["170"],
    },
    "165": {
        "display": "165",
        "group": "DL",
        "respawn_minutes": 1 * 60 + 13,
        "window_minutes": 3,
        "aliases": ["165"],
    },
    "160": {
        "display": "160",
        "group": "DL",
        "respawn_minutes": 1 * 60 + 8,
        "window_minutes": 3,
        "aliases": ["160"],
    },
    "155": {
        "display": "155",
        "group": "DL",
        "respawn_minutes": 1 * 60 + 3,
        "window_minutes": 3,
        "aliases": ["155"],
    },
    "pyrus": {
        "display": "Pyrus",
        "group": "FROZEN",
        "respawn_minutes": 58,
        "window_minutes": 3,
        "aliases": ["py", "pyrus"],
    },
    "grom": {
        "display": "Grom",
        "group": "FROZEN",
        "respawn_minutes": 48,
        "window_minutes": 3,
        "aliases": ["grom"],
    },
    "chained": {
        "display": "Chained",
        "group": "FROZEN",
        "respawn_minutes": 43,
        "window_minutes": 3,
        "aliases": ["chain", "chained"],
    },
    "woody": {
        "display": "Woody",
        "group": "FROZEN",
        "respawn_minutes": 38,
        "window_minutes": 3,
        "aliases": ["woody"],
    },
    "swampie": {
        "display": "Swampie",
        "group": "FROZEN",
        "respawn_minutes": 33,
        "window_minutes": 3,
        "aliases": ["swampy", "swampie"],
    },
    "eye": {
        "display": "Eye",
        "group": "FROZEN",
        "respawn_minutes": 28,
        "window_minutes": 3,
        "aliases": ["eye"],
    },
    "redbane": {
        "display": "Redbane",
        "group": "FROZEN",
        "respawn_minutes": 20,
        "window_minutes": 5,
        "aliases": ["redbane"],
    },
    "coppinger": {
        "display": "Coppinger",
        "group": "METEORIC",
        "respawn_minutes": 20,
        "window_minutes": 5,
        "aliases": ["copp", "coppinger"],
    },
    "rockbelly": {
        "display": "Rockbelly",
        "group": "METEORIC",
        "respawn_minutes": 15,
        "window_minutes": 5,
        "aliases": ["rockbelly"],
    },
    "goretusk": {
        "display": "Goretusk",
        "group": "METEORIC",
        "respawn_minutes": 20,
        "window_minutes": 5,
        "aliases": ["goretusk"],
    },
    "bonehead": {
        "display": "Bonehad",
        "group": "METEORIC",
        "respawn_minutes": 15,
        "window_minutes": 5,
        "aliases": ["bonehad", "bonehead"],
    },
    "doomclaw": {
        "display": "Doomclaw",
        "group": "METEORIC",
        "respawn_minutes": 7,
        "window_minutes": 5,
        "aliases": ["doomclaw"],
    },
    "falgren": {
        "display": "Falgren",
        "group": "WARDEN",
        "respawn_minutes": 45,
        "window_minutes": 5,
        "aliases": ["falg", "falgren"],
    },
}

GROUP_ORDER = ["ENDGAME", "MIDRAID", "EDL", "DL", "FROZEN", "METEORIC", "WARDEN"]

boss_timers = {}
display_message_id = None


def now_utc():
    return datetime.now(timezone.utc)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return fallback


def load_data():
    global boss_timers, display_message_id
    boss_timers = load_json(DATA_FILE, {})
    msg_data = load_json(MESSAGE_ID_FILE, {})
    display_message_id = msg_data.get("message_id")


def save_timers():
    save_json(DATA_FILE, boss_timers)


def save_display_message_id():
    save_json(MESSAGE_ID_FILE, {"message_id": display_message_id})


def find_boss_key(user_input: str):
    cleaned = user_input.lower().strip()
    for key, boss in BOSSES.items():
        if cleaned == key or cleaned in boss["aliases"]:
            return key
    return None


def set_boss_timer_now(boss_key: str):
    kill_time = now_utc()
    boss_timers[boss_key] = kill_time.isoformat()
    save_timers()
    return kill_time


def set_boss_timer_from_open_close(boss_key: str, open_minutes: int, close_minutes: int):
    """
    open_minutes = minutes until open from now
    close_minutes = minutes until close from now
    We store kill_time, so we back-calculate from the open time.
    """
    boss = BOSSES[boss_key]
    open_time = now_utc() + timedelta(minutes=open_minutes)
    close_time = now_utc() + timedelta(minutes=close_minutes)

    expected_window = boss["window_minutes"]
    actual_window = int((close_time - open_time).total_seconds() // 60)

    if actual_window != expected_window:
        raise ValueError(
            f"{boss['display']} requires a {expected_window} minute window, "
            f"but open/close values give {actual_window} minutes."
        )

    kill_time = open_time - timedelta(minutes=boss["respawn_minutes"])
    boss_timers[boss_key] = kill_time.isoformat()
    save_timers()
    return kill_time


def get_open_close_times(boss_key: str):
    kill_time = datetime.fromisoformat(boss_timers[boss_key])
    boss = BOSSES[boss_key]
    open_time = kill_time + timedelta(minutes=boss["respawn_minutes"])
    close_time = open_time + timedelta(minutes=boss["window_minutes"])
    return open_time, close_time


def format_remaining(target: datetime):
    seconds = int((target - now_utc()).total_seconds())
    if seconds <= 0:
        return "due"
    hours, rem = divmod(seconds, 3600)
    minutes = rem // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def parse_duration_to_minutes(text: str) -> int:
    """
    Accepts:
    90
    90m
    2h
    2h30m
    1d2h15m
    """
    cleaned = text.lower().replace(" ", "")
    if cleaned.isdigit():
        return int(cleaned)

    total = 0
    number = ""

    for ch in cleaned:
        if ch.isdigit():
            number += ch
            continue

        if not number:
            raise ValueError(f"Invalid duration: {text}")

        value = int(number)
        number = ""

        if ch == "d":
            total += value * 1440
        elif ch == "h":
            total += value * 60
        elif ch == "m":
            total += value
        else:
            raise ValueError(f"Invalid duration: {text}")

    if number:
        total += int(number)

    return total


def build_board_text():
    lines = ["**Boss Windows**", ""]

    grouped = {group: [] for group in GROUP_ORDER}

    for key, boss in BOSSES.items():
        if key in boss_timers:
            open_time, close_time = get_open_close_times(key)
            open_str = format_remaining(open_time)
            close_str = format_remaining(close_time)
        else:
            open_str = "-"
            close_str = "-"

        grouped[boss["group"]].append(
            f"**{boss['display']}** open `{open_str}` | close `{close_str}`"
        )

    for group in GROUP_ORDER:
        lines.append(f"__{group}__")
        lines.extend(grouped[group])
        lines.append("")

    lines.append(f"Updated: {now_utc().strftime('%H:%M UTC')}")
    return "\n".join(lines)


def build_info_text():
    lines = ["Boss Timers", ""]

    for group in GROUP_ORDER:
        lines.append(group)
        for key, boss in BOSSES.items():
            if boss["group"] != group:
                continue

            if key in boss_timers:
                open_time, close_time = get_open_close_times(key)
                lines.append(
                    f"- {boss['display']}: open {format_remaining(open_time)} | close {format_remaining(close_time)}"
                )
            else:
                lines.append(f"- {boss['display']}: open - | close -")
        lines.append("")

    lines.append(f"Updated: {now_utc().strftime('%H:%M UTC')}")
    return "\n".join(lines)


async def update_display_board():
    global display_message_id

    channel = bot.get_channel(DISPLAY_CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(DISPLAY_CHANNEL_ID)

    content = build_board_text()

    if display_message_id:
        try:
            msg = await channel.fetch_message(display_message_id)
            await msg.edit(content=content)
            return
        except discord.NotFound:
            pass

    msg = await channel.send(content)
    display_message_id = msg.id
    save_display_message_id()

@tasks.loop(seconds=60)  # refresh every 60 seconds
async def auto_refresh_board():
    await update_display_board()
    
@bot.event
async def on_ready():
    load_data()
    await bot.tree.sync()
    await update_display_board()

    if not auto_refresh_board.is_running():
        auto_refresh_board.start()

    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.channel.id != COMMAND_CHANNEL_ID:
        return

    content = message.content.strip().lower()
    boss_key = find_boss_key(content)

    if not boss_key:
        return

    set_boss_timer_now(boss_key)
    open_time, close_time = get_open_close_times(boss_key)
    await message.channel.send(
        f"{BOSSES[boss_key]['display']} open in {format_remaining(open_time)} | closes in {format_remaining(close_time)}"
    )
    await update_display_board()


@bot.tree.command(name="wipe", description="Reset all boss timers")
async def wipe(interaction: discord.Interaction):
    global boss_timers
    boss_timers = {}
    save_timers()
    await update_display_board()
    await interaction.response.send_message("All boss timers have been reset.")


@bot.tree.command(name="set", description="Manually set a boss using open and close times from now")
@app_commands.describe(
    boss="Boss name or alias",
    open="Time until open, like 2h, 90m, or 1d2h",
    close="Time until close, like 2h15m or 95m"
)
async def set_timer(interaction: discord.Interaction, boss: str, open: str, close: str):
    boss_key = find_boss_key(boss)
    if not boss_key:
        await interaction.response.send_message("Boss not found.", ephemeral=True)
        return

    try:
        open_minutes = parse_duration_to_minutes(open)
        close_minutes = parse_duration_to_minutes(close)
    except ValueError as e:
        await interaction.response.send_message(str(e), ephemeral=True)
        return

    if close_minutes < open_minutes:
        await interaction.response.send_message("Close time cannot be earlier than open time.", ephemeral=True)
        return

    try:
        set_boss_timer_from_open_close(boss_key, open_minutes, close_minutes)
    except ValueError as e:
        await interaction.response.send_message(str(e), ephemeral=True)
        return

    open_time, close_time = get_open_close_times(boss_key)
    await update_display_board()
    await interaction.response.send_message(
        f"{BOSSES[boss_key]['display']} set: open in {format_remaining(open_time)} | closes in {format_remaining(close_time)}"
    )


@bot.tree.command(name="info", description="DM yourself the current boss timers")
async def info(interaction: discord.Interaction):
    info_text = build_info_text()

    try:
        await interaction.user.send(f"```{info_text}```")
        await interaction.response.send_message("Sent you a DM with all boss timers.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(
            "I couldn't DM you. Your DMs may be closed.",
            ephemeral=True
        )


bot.run(TOKEN)
