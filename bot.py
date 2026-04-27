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
EVENT_FILE = "current_event.json"
EVENT_TIMER_FILE = "event_timers.json"
SERVER_RESET_FILE = "server_reset.json"


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
        "north": {
        "display": "North",
        "group": "RING",
        "respawn_minutes": 3 * 60 + 35,
        "window_minutes": 50,
        "aliases": ["northring", "north"],
    },
    "center": {
        "display": "Center",
        "group": "RING",
        "respawn_minutes": 3 * 60 + 35,
        "window_minutes": 50,
        "aliases": ["centre", "centrering", "centerring", "center"],
    },
    "south": {
        "display": "South",
        "group": "RING",
        "respawn_minutes": 3 * 60 + 35,
        "window_minutes": 50,
        "aliases": ["southring", "south"],
    },
    "east": {
        "display": "East",
        "group": "RING",
        "respawn_minutes": 3 * 60 + 35,
        "window_minutes": 50,
        "aliases": ["eastring", "east"],
    },
}

GROUP_ORDER = ["ENDGAME", "MIDRAID", "EDL", "DL", "FROZEN", "METEORIC", "WARDEN", "RING"]

boss_timers = {}
display_message_id = None
pinged_bosses = set()
active_alert_messages = {}
current_event_text = None
event_timer_data = {"active": False, "bosses": {}}
server_reset_data = {}


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


def get_server_reset_time():
    if not server_reset_data or "reset_time" not in server_reset_data:
        return None
    return datetime.fromisoformat(server_reset_data["reset_time"])


def format_server_downtime():
    if not server_reset_data:
        return None
    return server_reset_data.get("est_downtime")


def parse_datetime_string(text: str):
    return datetime.strptime(text.strip(), "%m/%d/%Y %H%M").replace(tzinfo=timezone.utc)

def load_data():
    global boss_timers, display_message_id, active_alert_messages, current_event_text, event_timer_data, server_reset_data

    boss_timers = load_json(DATA_FILE, {})
    msg_data = load_json(MESSAGE_ID_FILE, {})
    display_message_id = msg_data.get("message_id")

    active_alert_messages = load_json(ALERTS_FILE, {})

    event_data = load_json(EVENT_FILE, {})
    current_event_text = event_data.get("text")

    event_timer_data = load_json(EVENT_TIMER_FILE, {"active": False, "bosses": {}})
    if "active" not in event_timer_data:
        event_timer_data = {"active": False, "bosses": {}}
    if "bosses" not in event_timer_data or not isinstance(event_timer_data.get("bosses"), dict):
        event_timer_data["bosses"] = {}

    server_reset_data = load_json(SERVER_RESET_FILE, {})

def save_event():
    save_json(EVENT_FILE, {"text": current_event_text})


def save_event_timers():
    save_json(EVENT_TIMER_FILE, event_timer_data)


def save_server_reset():
    save_json(SERVER_RESET_FILE, server_reset_data)


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


def parse_event_timer_to_minutes(text: str) -> int:
    cleaned = text.lower().strip().replace(" ", "")

    # For respawn events, plain numbers mean hours.
    if cleaned.isdigit():
        return int(cleaned) * 60

    if cleaned.endswith("hrs"):
        cleaned = cleaned[:-3] + "h"
    elif cleaned.endswith("hr"):
        cleaned = cleaned[:-2] + "h"
    elif cleaned.endswith("hours"):
        cleaned = cleaned[:-5] + "h"
    elif cleaned.endswith("hour"):
        cleaned = cleaned[:-4] + "h"

    return parse_duration_to_minutes(cleaned)


def format_event_timer(minutes: int) -> str:
    if minutes % 60 == 0:
        return f"{minutes // 60}h"
    hours, mins = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def get_event_timer_minutes(boss_key: str):
    if not event_timer_data.get("active"):
        return None
    bosses = event_timer_data.get("bosses", {})
    return bosses.get(boss_key)


def set_boss_timer_from_event(boss_key: str, event_minutes: int):
    boss = BOSSES[boss_key]
    open_time = now_utc() + timedelta(minutes=event_minutes)
    kill_time = open_time - timedelta(minutes=boss["respawn_minutes"])
    boss_timers[boss_key] = kill_time.isoformat()
    pinged_bosses.discard(boss_key)
    save_timers()
    return kill_time


def parse_eventstart_pairs(text: str):
    parts = text.split()
    if not parts:
        raise ValueError("Use: /eventstart dhio 20h bt 20h gele 20h")

    if len(parts) % 2 != 0:
        raise ValueError("Event timers must be boss/timer pairs, like: dhio 20h bt 20h")

    if len(parts) // 2 > 9:
        raise ValueError("You can set up to 9 bosses in one /eventstart command.")

    parsed = {}

    for i in range(0, len(parts), 2):
        boss_alias = parts[i]
        timer_text = parts[i + 1]

        boss_key = find_boss_key(boss_alias)
        if not boss_key:
            raise ValueError(f"Boss not found: {boss_alias}")

        minutes = parse_event_timer_to_minutes(timer_text)
        if minutes <= 0:
            raise ValueError(f"Invalid timer for {boss_alias}: {timer_text}")

        parsed[boss_key] = minutes

    return parsed


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
    }

    has_active = any(is_in_window(k) for k in boss_timers)
    color = discord.Color.red() if has_active else discord.Color.teal()

    embed = discord.Embed(
        title="⏳ Active Boss Times ⏳",
        color=color
    )

    if current_event_text:
        embed.add_field(
            name="📰 Current Events",
            value=current_event_text,
            inline=False
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
                expired_for = now_utc() - close_time
                total_seconds = int(expired_for.total_seconds())
                hours, rem = divmod(total_seconds, 3600)
                minutes = rem // 60
                if hours > 0:
                    expired_text = f"{hours}h {minutes}m ago"
                else:
                    expired_text = f"{minutes}m ago"
                status = f"EXPIRED • {expired_text}"
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

    reset_time = get_server_reset_time()
    if reset_time:
        seconds_until_reset = int((reset_time - now_utc()).total_seconds())
        if seconds_until_reset > 0:
            status = format_remaining(reset_time)
        else:
            status = "DUE"

        server_text = f"🛠 Server Reset • {status}"
        downtime = format_server_downtime()
        if downtime:
            server_text += f"\nEst. down time: {downtime}"

        embed.add_field(
            name="Server Reset",
            value=server_text,
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

        # create 3-minute-before alert and leave it through the window
        if 120 < seconds_until_open <= 180 and boss_key not in active_alert_messages:
            role_id = get_ping_role_id(boss_key)
            boss_name = BOSSES[boss_key]["display"]

            message_text = f"{boss_name} is due in 3 minutes."
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

    reset_time = get_server_reset_time()
    if reset_time:
        seconds_until_reset = (reset_time - current).total_seconds()

        if 0 <= seconds_until_reset <= 180 and not server_reset_data.get("alert_sent"):
            downtime = format_server_downtime()
            message_text = "🛠 Server Reset Due."
            if downtime:
                message_text += f" Est. down time: {downtime}"

            try:
                await channel.send(message_text)
                server_reset_data["alert_sent"] = True
                save_server_reset()
                print("Server reset alert sent")
            except Exception as e:
                print(f"Failed server reset alert: {e}")


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

    event_minutes = get_event_timer_minutes(boss_key)
    if event_minutes is not None:
        set_boss_timer_from_event(boss_key, event_minutes)
        await message.channel.send(
            f"{BOSSES[boss_key]['display']} set | Event {format_event_timer(event_minutes)}"
        )
    else:
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

def get_bosses_in_group(group_name: str):
    normalized = group_name.strip().upper()
    return [key for key, boss in BOSSES.items() if boss["group"] == normalized]

@bot.tree.command(
    name="clear",
    description="Clear all timers in one boss section",
    guild=discord.Object(id=GUILD_ID),
)
@app_commands.describe(
    section="Boss section: endgame, midraid, edl, dl, frozen, meteoric, warden, ring",
)
async def clear_section(interaction: discord.Interaction, section: str):
    global boss_timers, pinged_bosses

    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    section_name = section.strip().upper()

    if section_name not in GROUP_ORDER:
        await interaction.response.send_message(
            f"Invalid section. Use one of: {', '.join(GROUP_ORDER).lower()}",
            ephemeral=True,
        )
        return

    bosses_to_clear = get_bosses_in_group(section_name)
    cleared_any = False

    for boss_key in bosses_to_clear:
        if boss_key in boss_timers:
            del boss_timers[boss_key]
            cleared_any = True

        pinged_bosses.discard(boss_key)
        await delete_alert_message_for_boss(boss_key)

    save_timers()

    try:
        await update_display_board()
    except Exception as e:
        print(f"Board update after clear failed: {e}")

    if cleared_any:
        await interaction.response.send_message(
            f"Cleared all timers in **{section_name}**.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            f"No active timers found in **{section_name}**.",
            ephemeral=True,
        )

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

    user = interaction.user

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

    channel = bot.get_channel(COMMAND_CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(COMMAND_CHANNEL_ID)

    await channel.send(
        f"⚠️ **Boss timers wiped by {user.mention}**"
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
    description="Set a boss timer",
    guild=discord.Object(id=GUILD_ID),
)
@app_commands.describe(
    boss="Boss name or alias",
    open="Optional time until open, like 2h, 90m, or 1d2h",
)
async def set_timer(interaction: discord.Interaction, boss: str, open: str = None):
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

    await delete_alert_message_for_boss(boss_key)

    event_minutes = get_event_timer_minutes(boss_key)
    if event_minutes is not None:
        try:
            set_boss_timer_from_event(boss_key, event_minutes)
        except Exception as e:
            await interaction.response.send_message(
                f"Failed to set event timer: {e}",
                ephemeral=True,
            )
            return

        try:
            await update_display_board()
        except Exception as e:
            print(f"Board update after event set failed: {e}")

        await interaction.response.send_message(
            f"{BOSSES[boss_key]['display']} set | Event {format_event_timer(event_minutes)}",
            ephemeral=False,
        )
        return

    try:
        if open is None:
            set_boss_timer_now(boss_key)
        else:
            open_minutes = parse_duration_to_minutes(open)
            set_boss_timer_from_open(boss_key, open_minutes)
    except ValueError as e:
        await interaction.response.send_message(str(e), ephemeral=True)
        return
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
        f"{BOSSES[boss_key]['display']} open in {format_remaining(open_time)} | closes in {format_remaining(close_time)}",
        ephemeral=False,
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

@bot.tree.command(
    name="when",
    description="Show when a boss opens or closes in your local time",
    guild=discord.Object(id=GUILD_ID),
)
@app_commands.describe(
    boss="Boss name or alias",
)
async def when(interaction: discord.Interaction, boss: str):
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

    boss_name = BOSSES[boss_key]["display"]
    open_time, close_time = get_open_close_times(boss_key)
    current = now_utc()

    if open_time <= current <= close_time:
        unix_close = int(close_time.timestamp())

        embed = discord.Embed(
            title=boss_name,
            description="🔥 OPEN NOW",
            color=discord.Color.red(),
        )
        embed.add_field(
            name="Closes",
            value=f"<t:{unix_close}:F>\n(<t:{unix_close}:R>)",
            inline=False,
        )
    else:
        unix_open = int(open_time.timestamp())

        embed = discord.Embed(
            title=boss_name,
            description="⏳ Not open yet",
            color=discord.Color.teal(),
        )
        embed.add_field(
            name="Opens",
            value=f"<t:{unix_open}:F>\n(<t:{unix_open}:R>)",
            inline=False,
        )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )

@bot.tree.command(
    name="eventmessage",
    description="Set the current event text",
    guild=discord.Object(id=GUILD_ID),
)
@app_commands.describe(
    text="Current event text to show on the display board",
)
async def event_message(interaction: discord.Interaction, text: str):
    global current_event_text

    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    current_event_text = text
    save_event()

    try:
        await update_display_board()
    except Exception as e:
        print(f"Board update after event message failed: {e}")

    await interaction.response.send_message(
        f"Current event set to:\n{text}",
        ephemeral=True,
    )


@bot.tree.command(
    name="eventstart",
    description="Start respawn event mode for up to 9 bosses",
    guild=discord.Object(id=GUILD_ID),
)
@app_commands.describe(
    timers="Boss/timer pairs, like: dhio 20h bt 20h gele 20h crom 30h",
)
async def event_start(interaction: discord.Interaction, timers: str):
    global event_timer_data

    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    try:
        parsed = parse_eventstart_pairs(timers)
    except ValueError as e:
        await interaction.response.send_message(str(e), ephemeral=True)
        return

    event_timer_data = {
        "active": True,
        "bosses": parsed,
    }
    save_event_timers()

    boss_list = ", ".join(
        f"{BOSSES[boss_key]['display']} ({format_event_timer(minutes)})"
        for boss_key, minutes in parsed.items()
    )

    await interaction.response.send_message(
        f"Respawn event started.\n{boss_list}",
        ephemeral=False,
    )


@bot.tree.command(
    name="eventstop",
    description="Stop respawn event mode and resume normal boss windows",
    guild=discord.Object(id=GUILD_ID),
)
async def event_stop(interaction: discord.Interaction):
    global event_timer_data

    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    event_timer_data = {"active": False, "bosses": {}}
    save_event_timers()

    await interaction.response.send_message(
        "Respawn event ended. Normal timers resumed.",
        ephemeral=False,
    )


@bot.tree.command(
    name="eventclear",
    description="Clear the current event text",
    guild=discord.Object(id=GUILD_ID),
)
async def event_clear(interaction: discord.Interaction):
    global current_event_text

    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    current_event_text = None
    save_event()

    try:
        await update_display_board()
    except Exception as e:
        print(f"Board update after event clear failed: {e}")

    await interaction.response.send_message(
        "Current event cleared.",
        ephemeral=True,
    )

@bot.tree.command(
    name="serverset",
    description="Set the server reset date and time",
    guild=discord.Object(id=GUILD_ID),
)
@app_commands.describe(
    when="Format: M/D/YYYY HHMM (example: 4/16/2026 0900)",
    downtime="Optional estimated downtime, like 2-3 hrs",
)
async def server_set(interaction: discord.Interaction, when: str, downtime: str = None):
    global server_reset_data

    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    try:
        reset_time = parse_datetime_string(when)
    except ValueError:
        await interaction.response.send_message(
            "Invalid date/time format. Use: YYYY-MM-DD HH:MM",
            ephemeral=True,
        )
        return

    server_reset_data = {
        "reset_time": reset_time.isoformat(),
        "est_downtime": downtime,
        "alert_sent": False,
    }
    save_server_reset()

    try:
        await update_display_board()
    except Exception as e:
        print(f"Board update after server set failed: {e}")

    await interaction.response.send_message(
        f"Server reset set for {when} UTC.",
        ephemeral=True,
    )


@bot.tree.command(
    name="serverinfo",
    description="Show the current server reset info",
    guild=discord.Object(id=GUILD_ID),
)
async def server_info(interaction: discord.Interaction):
    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    reset_time = get_server_reset_time()
    if not reset_time:
        await interaction.response.send_message(
            "No server reset is currently set.",
            ephemeral=True,
        )
        return

    unix_reset = int(reset_time.timestamp())
    downtime = format_server_downtime()

    embed = discord.Embed(
        title="Server Reset",
        color=discord.Color.orange(),
    )
    embed.add_field(
        name="Scheduled",
        value=f"<t:{unix_reset}:F>\n(<t:{unix_reset}:R>)",
        inline=False,
    )

    if downtime:
        embed.add_field(
            name="Est. Downtime",
            value=downtime,
            inline=False,
        )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )


@bot.tree.command(
    name="serverclear",
    description="Clear the current server reset",
    guild=discord.Object(id=GUILD_ID),
)
async def server_clear(interaction: discord.Interaction):
    global server_reset_data

    if not in_command_channel(interaction):
        await interaction.response.send_message(
            "Use this command in the configured command channel.",
            ephemeral=True,
        )
        return

    server_reset_data = {}
    save_server_reset()

    try:
        await update_display_board()
    except Exception as e:
        print(f"Board update after server clear failed: {e}")

    await interaction.response.send_message(
        "Server reset cleared.",
        ephemeral=True,
    )

@bot.tree.command(
    name="help",
    description="Show timer bot commands",
    guild=discord.Object(id=GUILD_ID),
)
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="⚔️ TIMER BOT COMMANDS",
        color=0x00D4AA
    )

    embed.description = (
        f"**Post commands here:** <#{COMMAND_CHANNEL_ID}>\n\n"
        f"Enter boss name in channel to set boss"
    )

    embed.add_field(
        name="Boss Timers",
        value=(
            "`/set boss:[name] open:[time]` → set timer\n\n"
            "`/reset boss:[name]` → remove one timer\n\n"
            "`/clear section:[group]` → clear a section\n\n"
            "`/wipe` → ⚠️ clear ALL timers"
        ),
        inline=False,
    )

    embed.add_field(
        name="Info",
        value=(
            "`/when boss:[name]` → shows your local time\n\n"
            "`/info` → DM full timer list"
        ),
        inline=False,
    )

    embed.add_field(
        name="Event",
        value=(
            "`/eventmessage text:[message]` → set event banner\n\n"
            "`/eventclear` → remove event banner\n\n"
            "`/eventstart timers:[dhio 20h bt 20h]` → start respawn event mode\n\n"
            "`/eventstop` → stop respawn event mode"
        ),
        inline=False,
    )

    embed.add_field(
        name="Server Reset",
        value=(
            "`/serverset when:[MM/DD/YYYY HHMM] downtime:[optional]`\n\n"
            "`/serverinfo` → view reset\n\n"
            "`/serverclear` → remove reset"
        ),
        inline=False,
    )

    embed.add_field(
        name="Time Format",
        value=(
            "`30m` = minutes\n"
            "`2h` = hours\n"
            "`1d` = days\n"
            "combo works → `1d2h30m`"
        ),
        inline=False,
    )

    embed.set_footer(text="Use /when to check your local boss times")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(
    name="bosswindows",
    description="Show boss open and close windows",
    guild=discord.Object(id=GUILD_ID),
)
async def bosswindows(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Boss Windows",
        color=0x00D4AA
    )

    embed.description = (
        f"**View Active Boss times here:**\n"
        f"<#{DISPLAY_CHANNEL_ID}>"
    )

    embed.add_field(
        name="ENDGAME",
        value=(
            "Crom's Manikin — Open: 96h | Close: 120h\n"
            "Dhiothu — Open: 34h | Close: 62h\n"
            "Bloodthorn — Open: 34h | Close: 62h\n"
            "Gelebron — Open: 32h | Close: 60h\n"
            "Proteus — Open: 18h | Close: 18h 15m"
        ),
        inline=False,
    )

    embed.add_field(
        name="MIDRAID",
        value=(
            "Necromancer — Open: 22h | Close: 38h\n"
            "Mordris — Open: 20h | Close: 36h\n"
            "Hrungnir — Open: 22h | Close: 38h\n"
            "Aggragoth — Open: 20h | Close: 36h"
        ),
        inline=False,
    )

    embed.add_field(
        name="EDL",
        value=(
            "215 — Open: 2h 14m | Close: 2h 19m\n"
            "210 — Open: 2h 5m | Close: 2h 10m\n"
            "205 — Open: 1h 57m | Close: 2h 1m\n"
            "200 — Open: 1h 48m | Close: 1h 53m\n"
            "195 — Open: 1h 29m | Close: 1h 33m\n"
            "190 — Open: 1h 21m | Close: 1h 24m\n"
            "185 — Open: 1h 12m | Close: 1h 15m"
        ),
        inline=False,
    )

    embed.add_field(
        name="DL",
        value=(
            "180 — Open: 1h 28m | Close: 1h 31m\n"
            "170 — Open: 1h 18m | Close: 1h 21m\n"
            "165 — Open: 1h 13m | Close: 1h 16m\n"
            "160 — Open: 1h 8m | Close: 1h 11m\n"
            "155 — Open: 1h 3m | Close: 1h 6m"
        ),
        inline=False,
    )

    embed.add_field(
        name="FROZEN",
        value=(
            "Pyrus — Open: 58m | Close: 1h 1m\n"
            "Grom — Open: 48m | Close: 51m\n"
            "Chained — Open: 43m | Close: 46m\n"
            "Woody — Open: 38m | Close: 41m\n"
            "Swampie — Open: 33m | Close: 36m\n"
            "Eye — Open: 28m | Close: 31m\n"
            "Redbane — Open: 20m | Close: 25m"
        ),
        inline=False,
    )

    embed.add_field(
        name="METEORIC / WARDEN",
        value=(
            "Coppinger — Open: 20m | Close: 25m\n"
            "Rockbelly — Open: 15m | Close: 20m\n"
            "Goretusk — Open: 20m | Close: 25m\n"
            "Bonehead — Open: 15m | Close: 20m\n"
            "Doomclaw — Open: 7m | Close: 12m\n\n"
            "Falgren — Open: 45m | Close: 50m"
        ),
        inline=False,
    )

    embed.add_field(
        name="RINGS",
        value="North / Center / South / East — Open: 3h 35m | Close: 4h 25m",
        inline=False,
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run(TOKEN)
