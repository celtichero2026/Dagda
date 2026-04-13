import os
import json
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands, tasks
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
display_channel_raw = os.getenv("DISPLAY_CHANNEL_ID")
command_channel_raw = os.getenv("COMMAND_CHANNEL_ID")
guild_id_raw = os.getenv("GUILD_ID")

if not TOKEN:
    raise ValueError("Missing DISCORD_TOKEN environment variable")
if not display_channel_raw:
    raise ValueError("Missing DISPLAY_CHANNEL_ID environment variable")
if not command_channel_raw:
    raise ValueError("Missing COMMAND_CHANNEL_ID environment variable")
if not guild_id_raw:
    raise ValueError("Missing GUILD_ID environment variable")

DISPLAY_CHANNEL_ID = int(display_channel_raw)
COMMAND_CHANNEL_ID = int(command_channel_raw)
GUILD_ID = int(guild_id_raw)

DATA_FILE = "boss_timers.json"
MESSAGE_ID_FILE = "display_message.json"
ALERTS_FILE = "boss_alerts.json"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

role_endgame_raw = os.getenv("ROLE_ENDGAME_ID")
role_midraid_raw = os.getenv("ROLE_MIDRAID_ID")
role_215_raw = os.getenv("ROLE_215_ID")
role_edl_raw = os.getenv("ROLE_EDL_ID")
role_dl_raw = os.getenv("ROLE_DL_ID")
role_frozen_raw = os.getenv("ROLE_FROZEN_ID")
role_meteoric_raw = os.getenv("ROLE_METEORIC_ID")
role_warden_raw = os.getenv("ROLE_WARDEN_ID")

ROLE_ENDGAME_ID = int(role_endgame_raw) if role_endgame_raw else None
ROLE_MIDRAID_ID = int(role_midraid_raw) if role_midraid_raw else None
ROLE_215_ID = int(role_215_raw) if role_215_raw else None
ROLE_EDL_ID = int(role_edl_raw) if role_edl_raw else None
ROLE_DL_ID = int(role_dl_raw) if role_dl_raw else None
ROLE_FROZEN_ID = int(role_frozen_raw) if role_frozen_raw else None
ROLE_METEORIC_ID = int(role_meteoric_raw) if role_meteoric_raw else None
ROLE_WARDEN_ID = int(role_warden_raw) if role_warden_raw else None

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
        "display": "Bonehead",
        "group": "METEORIC",
        "respawn_minutes": 15,
        "window_minutes": 5,
        "aliases": ["bonehead"],
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
pinged_bosses = set()
active_alert_messages = {}


def get_ping_role_id(boss_key: str):
    boss = BOSSES[boss_key]
    group = boss["group"]

    if boss_key == "215":
        return ROLE_215_ID
    if group == "ENDGAME":
        return ROLE_ENDGAME_ID
    if group == "MIDRAID":
        return ROLE_MIDRAID_ID
    if group == "EDL":
        return ROLE_EDL_ID
    if group == "DL":
        return ROLE_DL_ID
    if group == "FROZEN":
        return ROLE_FROZEN_ID
    if group == "METEORIC":
        return ROLE_METEORIC_ID
    if group == "WARDEN":
        return ROLE_WARDEN_ID

    return None


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
    except json.JSONDecodeError:
        print(f"JSON decode error in {path}, using fallback.")
        return fallback


def load_data():
    global boss_timers, display_message_id, active_alert_messages
    boss_timers = load_json(DATA_FILE, {})
    msg_data = load_json(MESSAGE_ID_FILE, {})
    display_message_id = msg_data.get("message_id")
    active_alert_messages = load_json(ALERTS_FILE, {})


def save_timers():
    save_json(DATA_FILE, boss_timers)


def save_display_message_id():
    save_json(MESSAGE_ID_FILE, {"message_id": display_message_id})


def save_alert_messages():
    save_json(ALERTS_FILE, active_alert_messages)


def find_boss_key(user_input: str):
    cleaned = user_input.lower().strip()

    for key, boss in BOSSES.items():
        if cleaned == key or cleaned in boss["aliases"]:
            return key

    return None


async def delete_alert_message_for_boss(boss_key: str):
    if boss_key not in active_alert_messages:
        return

    channel = bot.get_channel(DISPLAY_CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(DISPLAY_CHANNEL_ID)

    message_id = active_alert_messages.get(boss_key)

    try:
        msg = await channel.fetch_message(message_id)
        await msg.delete()
        print(f"Deleted alert message for {boss_key}: {message_id}")
    except discord.NotFound:
        print(f"Alert message already missing for {boss_key}: {message_id}")
    except Exception as e:
        print(f"Failed deleting alert for {boss_key}: {e}")

    active_alert_messages.pop(boss_key, None)
    save_alert_messages()


async def clear_all_alert_messages():
    for boss_key in list(active_alert_messages.keys()):
        await delete_alert_message_for_boss(boss_key)


def set_boss_timer_now(boss_key: str):
    kill_time = now_utc()
    boss_timers[boss_key] = kill_time.isoformat()
    pinged_bosses.discard(boss_key)
    save_timers()
    return kill_time


def set_boss_timer_from_open(boss_key: str, open_minutes: int):
    boss = BOSSES[boss_key]
    open_time = now_utc() + timedelta(minutes=open_minutes)
    kill_time = open_time - timedelta(minutes=boss["respawn_minutes"])
    boss_timers[boss_key] = kill_time.isoformat()
    pinged_bosses.discard(boss_key)
    save_timers()
    return kill_time


def get_open_close_times(boss_key: str):
    kill_time = datetime.fromisoformat(boss_timers[boss_key])
    boss = BOSSES[boss_key]
    open_time = kill_time + timedelta(minutes=boss["respawn_minutes"])
    close_time = open_time + timedelta(minutes=boss["window_minutes"])
    return open_time, close_time


def is_in_window(boss_key: str) -> bool:
    if boss_key not in boss_timers:
        return False

    open_time, close_time = get_open_close_times(boss_key)
    current = now_utc()
    return open_time <= current <= close_time


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


def build_board_embed():
    ALWAYS_SHOW = {
        "croms manikin",
        "dhiothu",
        "bloodthorn",
        "gelebron",
        "proteus",
        "necromancer",
        "mordris",
        "hrungnir",
        "aggragoth",
    }

    has_active = any(is_in_window(k) for k in boss_timers)
    color = discord.Color.red() if has_active else discord.Color.teal()

    embed = discord.Embed(
        title="⏳ Active Boss Times ⏳",
        color=color
    )

    grouped = {group: [] for group in GROUP_ORDER}

    sorted_bosses = sorted(
        BOSSES.items(),
        key=lambda item: (
            get_open_close_times(item[0])[0]
            if item[0] in boss_timers
            else datetime.max.replace(tzinfo=timezone.utc)
        )
    )

    for key, boss in sorted_bosses:
        has_timer = key in boss_timers
        should_show = key in ALWAYS_SHOW or has_timer

        if not should_show:
            continue

        if has_timer:
            open_time, close_time = get_open_close_times(key)
            open_seconds = (open_time - now_utc()).total_seconds()
            close_seconds = (close_time - now_utc()).total_seconds()

            if open_seconds > 0:
                if open_seconds <= 300:
                    status = f"⚠️ {format_remaining(open_time)}"
                    prefix = "🟡 "
                else:
                    status = format_remaining(open_time)
                    prefix = ""
            elif close_seconds > 0:
                status = f"🔥 OPEN NOW • {format_remaining(close_time)} left"
                prefix = "🟢 "
            else:
                status = "EXPIRED"
                prefix = "🔴 "
        else:
            status = "-"
            prefix = ""

        grouped[boss["group"]].append(
            f"{prefix}{boss['display']:<16} • {status}"
        )

    for group in GROUP_ORDER:
        if not grouped[group]:
            continue

        embed.add_field(
            name=f"✦ {group}",
            value="```" + "\n".join(grouped[group]) + "```",
            inline=False
        )

    embed.set_footer(text=f"Game Time: {now_utc().strftime('%H:%M UTC')}")
    return embed

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

    embed = build_board_embed()

    if display_message_id:
        try:
            msg = await channel.fetch_message(display_message_id)
            await msg.edit(content=None, embed=embed)
            print(f"Board edited successfully: {display_message_id}")
            return
        except discord.NotFound:
            print("Stored display message not found. Creating a new one.")
        except Exception as e:
            print(f"Edit existing board failed: {e}")

    msg = await channel.send(embed=embed)
    display_message_id = msg.id
    save_display_message_id()
    print(f"Created new display message: {display_message_id}")


async def check_due_boss_pings():
    channel = bot.get_channel(DISPLAY_CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(DISPLAY_CHANNEL_ID)

    current = now_utc()

    for boss_key in list(boss_timers.keys()):
        if boss_key not in BOSSES:
            continue

        open_time, close_time = get_open_close_times(boss_key)
        seconds_until_open = (open_time - current).total_seconds()

        # delete lingering alert after window ends
        if current > close_time and boss_key in active_alert_messages:
            await delete_alert_message_for_boss(boss_key)
            pinged_bosses.discard(boss_key)
            continue

        # create 1-minute-before alert and leave it through the window
        if 0 <= seconds_until_open <= 120 and boss_key not in active_alert_messages:
            role_id = get_ping_role_id(boss_key)
            boss_name = BOSSES[boss_key]["display"]

            message_text = f"{boss_name} is due in 1 minute."
            if role_id:
                message_text = f"<@&{role_id}> 🚨 {boss_name} is due. 🚨"

            try:
                msg = await channel.send(message_text)
                active_alert_messages[boss_key] = msg.id
                save_alert_messages()
                pinged_bosses.add(boss_key)
                print(f"Created alert message for {boss_key}: {msg.id}")
            except Exception as e:
                print(f"Failed creating alert for {boss_key}: {e}")


@tasks.loop(minutes=1)
async def auto_refresh_board():
    try:
        await update_display_board()
        await check_due_boss_pings()
        print("Board refreshed")
    except Exception as e:
        print(f"Auto refresh error: {e}")


@auto_refresh_board.before_loop
async def before_auto_refresh_board():
    await bot.wait_until_ready()


async def setup_hook():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)


bot.setup_hook = setup_hook


@bot.event
async def on_ready():
    load_data()

    try:
        await update_display_board()
        await check_due_boss_pings()
        print("Initial board update complete")
    except Exception as e:
        print(f"Initial board update error: {e}")

    if not auto_refresh_board.is_running():
        auto_refresh_board.start()
        print("Auto refresh started")

    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.guild is None:
        return

    if message.channel.id != COMMAND_CHANNEL_ID:
        return

    content = message.content.strip().lower()
    boss_key = find_boss_key(content)

    if not boss_key:
        return

    await delete_alert_message_for_boss(boss_key)
    set_boss_timer_now(boss_key)

    open_time, close_time = get_open_close_times(boss_key)

    await message.channel.send(
        f"{BOSSES[boss_key]['display']} open in {format_remaining(open_time)} | closes in {format_remaining(close_time)}"
    )

    try:
        await update_display_board()
    except Exception as e:
        print(f"Immediate update after message failed: {e}")


def in_command_channel(interaction: discord.Interaction) -> bool:
    return interaction.channel_id == COMMAND_CHANNEL_ID


@bot.tree.command(
    name="wipe",
    description="Reset all boss timers",
    guild=discord.Object(id=GUILD_ID),
)
async def wipe(interaction: discord.Interaction):
    global boss_timers, pinged_bosses

    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    boss_timers = {}
    pinged_bosses = set()
    save_timers()
    await clear_all_alert_messages()

    try:
        await update_display_board()
    except Exception as e:
        print(f"Board update after wipe failed: {e}")

    await interaction.response.send_message(
        "All boss timers have been reset.",
        ephemeral=True,
    )


@bot.tree.command(
    name="reset",
    description="Reset one boss timer",
    guild=discord.Object(id=GUILD_ID),
)
@app_commands.describe(
    boss="Boss name or alias",
)
async def reset_boss(interaction: discord.Interaction, boss: str):
    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    boss_key = find_boss_key(boss)
    if not boss_key:
        await interaction.response.send_message(
            "Boss not found.",
            ephemeral=True,
        )
        return

    if boss_key not in boss_timers:
        await interaction.response.send_message(
            f"{BOSSES[boss_key]['display']} does not currently have an active timer.",
            ephemeral=True,
        )
        return

    del boss_timers[boss_key]
    pinged_bosses.discard(boss_key)
    save_timers()
    await delete_alert_message_for_boss(boss_key)

    try:
        await update_display_board()
    except Exception as e:
        print(f"Board update after reset failed: {e}")

    await interaction.response.send_message(
        f"{BOSSES[boss_key]['display']} timer has been reset.",
        ephemeral=True,
    )


@bot.tree.command(
    name="set",
    description="Manually set a boss using only the open time from now",
    guild=discord.Object(id=GUILD_ID),
)
@app_commands.describe(
    boss="Boss name or alias",
    open="Time until open, like 2h, 90m, or 1d2h",
)
async def set_timer(interaction: discord.Interaction, boss: str, open: str):
    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    boss_key = find_boss_key(boss)
    if not boss_key:
        await interaction.response.send_message("Boss not found.", ephemeral=True)
        return

    try:
        open_minutes = parse_duration_to_minutes(open)
    except ValueError as e:
        await interaction.response.send_message(str(e), ephemeral=True)
        return

    await delete_alert_message_for_boss(boss_key)

    try:
        set_boss_timer_from_open(boss_key, open_minutes)
    except Exception as e:
        await interaction.response.send_message(
            f"Failed to set timer: {e}",
            ephemeral=True,
        )
        return

    open_time, close_time = get_open_close_times(boss_key)

    try:
        await update_display_board()
    except Exception as e:
        print(f"Board update after set failed: {e}")

    await interaction.response.send_message(
        f"{BOSSES[boss_key]['display']} set: open in {format_remaining(open_time)} | closes in {format_remaining(close_time)}",
        ephemeral=True,
    )


@bot.tree.command(
    name="info",
    description="DM yourself the current boss timers",
    guild=discord.Object(id=GUILD_ID),
)
async def info(interaction: discord.Interaction):
    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    info_text = build_info_text()

    try:
        await interaction.user.send(f"```{info_text}```")
        await interaction.response.send_message(
            "Sent you a DM with all boss timers.",
            ephemeral=True,
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "I couldn't DM you. Your DMs may be closed.",
            ephemeral=True,
        )


bot.run(TOKEN)
