# discord_selfbot.py — Infinity V4 SELFBOT (Discord Edition)
# Works in GROUP DMs and servers!
#
# ⚠️ WARNING: Selfbots violate Discord ToS — use at your own risk!
#
# INSTALL:
#   pip install discord.py-self aiohttp requests gtts
#
# RUN:
#   python discord_selfbot.py
#
# COMMANDS PREFIX: . (dot)
# Example: .gcnc INFINITY, .spam hello, .stopall

import asyncio
import json
import os
import time
import io
import logging
import requests
import aiohttp
import discord
discord.utils.BUILD_INFO = {"number": 9999, "id": "stable"}
from discord.ext import commands

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG — put your real user account tokens here
# ──────────────────────────────────────────────────────────────────────────────
# ACCOUNTS — Email aur Password daalo, token khud nikal lega! 🔥
ACCOUNTS = [
    {"email": "eeegggf63@gmail.com", "password": "hacker.x.777"},   # SLOT 1 — Primary
    {"email": "account2@gmail.com", "password": "password2"},   # SLOT 2
    {"email": "account3@gmail.com", "password": "password3"},   # SLOT 3
    {"email": "account4@gmail.com", "password": "password4"},   # SLOT 4
    {"email": "account5@gmail.com", "password": "password5"},   # SLOT 5
    {"email": "account6@gmail.com", "password": "password6"},   # SLOT 6
    {"email": "account7@gmail.com", "password": "password7"},   # SLOT 7
    {"email": "account8@gmail.com", "password": "password8"},   # SLOT 8
    {"email": "account9@gmail.com", "password": "password9"},   # SLOT 9
    {"email": "account10@gmail.com", "password": "password10"}, # SLOT 10
    {"email": "account11@gmail.com", "password": "password11"}, # SLOT 11
    {"email": "account12@gmail.com", "password": "password12"}, # SLOT 12
]

OWNER_ID       = 1444823246817067160   # ← apna Discord User ID dalo
COMMAND_PREFIX = "."                   # dot prefix — e.g. .gcnc, .spam
SUDO_FILE      = "sudo_selfbot.json"

ELEVENLABS_API_KEY   = "sk_e326b337242b09b451e8f18041fd0a7149cc895648e36538"
DOMAIN_EXPANSION_IMG = "https://i.imgur.com/6Gq9V1P.jpeg"

# ──────────────────────────────────────────────────────────────────────────────
# TEXT POOLS
# ──────────────────────────────────────────────────────────────────────────────
RAID_TEXTS = [
    "Infinity PAPA KA LUN CHUS ⃟♥️",  "Infinity PAPA KA LUN CHUS ⃟💔",
    "Infinity PAPA KA LUN CHUS ⃟❣️",  "Infinity PAPA KA LUN CHUS ⃟💕",
    "Infinity PAPA KA LUN CHUS ⃟💞",  "Infinity PAPA KA LUN CHUS ⃟💓",
    "Infinity PAPA KA LUN CHUS ⃟💗",  "Infinity PAPA KA LUN CHUS ⃟💖",
    "Infinity PAPA KA LUN CHUS ⃟💘",  "Infinity PAPA KA LUN CHUS ⃟💌",
    "Infinity PAPA KA LUN CHUS ⃟🩶",  "Infinity PAPA KA LUN CHUS ⃟🩷",
    "Infinity PAPA KA LUN CHUS ⃟🩵",  "Infinity PAPA KA LUN CHUS ⃟❤️‍🔥",
    "Infinity PAPA KA LUN CHUS ⃟❤️‍🩹", "Infinity BAAP H TERA RNDYKE❤️‍🔥",
]

INFINITY_TEXTS = [
    "🎀","💝","🔱","💘","💞","💢","❤️‍🔥","🌈","🪐","☄️",
    "⚡","🦚","🦈","🕸️","🍬","🧃","🗽","🪅","🎏","🎸",
    "📿","🏳️‍🌈","🌸","🎶","🎵","☃️","❄️","🕊️","🍷","🥂",
]

NCEMO_EMOJIS = [
    "💘","🪷","🎐","🫧","💥","💢","❤️‍🔥","☘️","🪐","☄️",
    "🪽","🦚","🦈","🕸️","🍬","🧃","🗽","🪅","🎏","🎸",
    "📿","🏳️‍🌈","🌸","🎶","🎵","☃️","❄️","🕊️","🍷","🥂",
]

DOMAIN_MODE_TEXTS = {
    "gcnc":     RAID_TEXTS,
    "ncemo":    NCEMO_EMOJIS,
    "ncbaap":   RAID_TEXTS,
    "infinity": INFINITY_TEXTS,
}

VOICE_CHARACTERS = {
    1:  {"name": "Urokodaki",  "voice_id": "VR6AewLTigWG4xSOukaG"},
    2:  {"name": "Kanae",      "voice_id": "EXAVITQu4vr4xnSDxMaL"},
    3:  {"name": "Uppermoon",  "voice_id": "AZnzlk1XvdvUeBnXmlld"},
    4:  {"name": "Tanjiro",    "voice_id": "VR6AewLTigWG4xSOukaG"},
    5:  {"name": "Nezuko",     "voice_id": "EXAVITQu4vr4xnSDxMaL"},
    6:  {"name": "Zenitsu",    "voice_id": "AZnzlk1XvdvUeBnXmlld"},
    7:  {"name": "Inosuke",    "voice_id": "VR6AewLTigWG4xSOukaG"},
    8:  {"name": "Muzan",      "voice_id": "AZnzlk1XvdvUeBnXmlld"},
    9:  {"name": "Shinobu",    "voice_id": "EXAVITQu4vr4xnSDxMaL"},
    10: {"name": "Giyu",       "voice_id": "VR6AewLTigWG4xSOukaG"},
}

# ──────────────────────────────────────────────────────────────────────────────
# EMAIL/PASSWORD → TOKEN LOGIN
# ──────────────────────────────────────────────────────────────────────────────
async def fetch_token(email: str, password: str, idx: int) -> str | None:
    """Login with email+password via Discord API and return the user token."""
    url = "https://discord.com/api/v9/auth/login"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyJ9",
    }
    payload = {
        "login": str(email).strip(),
        "password": str(password).strip(),
        "undelete": False,
        "captcha_key": None,
        "login_source": None,
        "gift_code_sku_id": None,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                data = await resp.json()
                if "token" in data:
                    print(f"✅ Slot {idx+1}: Login successful! ({email})")
                    return data["token"]
                elif "mfa" in data or data.get("mfa"):
                    print(f"⚠️ Slot {idx+1}: 2FA enabled on {email} — enter code:")
                    code_2fa = input(f"  2FA code for {email}: ").strip()
                    async with session.post(
                        "https://discord.com/api/v9/auth/mfa/totp",
                        json={"code": code_2fa, "ticket": data.get("ticket", "")},
                        headers=headers
                    ) as r2:
                        d2 = await r2.json()
                        if "token" in d2:
                            print(f"✅ Slot {idx+1}: 2FA login success! ({email})")
                            return d2["token"]
                        print(f"❌ Slot {idx+1}: 2FA failed: {d2}")
                        return None
                else:
                    err = data.get("message", str(data))
                    print(f"❌ Slot {idx+1}: Login failed for {email}: {err}")
                    return None
    except Exception as e:
        print(f"❌ Slot {idx+1}: Error logging in {email}: {e}")
        return None

# ──────────────────────────────────────────────────────────────────────────────
# PERSISTENT STATE
# ──────────────────────────────────────────────────────────────────────────────
def _load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except: pass
    return default

def _save_json(path, data):
    with open(path, "w") as f: json.dump(data, f)

SUDO_USERS: set = set(int(x) for x in _load_json(SUDO_FILE, []))
SUDO_USERS.add(OWNER_ID)

def save_sudo(): _save_json(SUDO_FILE, list(SUDO_USERS))

# ──────────────────────────────────────────────────────────────────────────────
# SHARED RUNTIME STATE
# ──────────────────────────────────────────────────────────────────────────────
all_clients:            list = []   # all selfbot client instances
group_tasks:            dict = {}   # {channel_id: [tasks]}
infinity_tasks:         dict = {}
spam_tasks:             dict = {}
react_tasks:            dict = {}
channel_nc_tasks:       dict = {}
domain_expansion_chats: dict = {}
slide_targets:          set  = set()
slidespam_targets:      set  = set()
current_running_command: str = None
delay         = 0.1
infinity_delay= 0.05

logging.basicConfig(level=logging.WARNING)  # less noise
log = logging.getLogger("InfinitySelfbot")

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def is_sudo(uid): return uid in SUDO_USERS
def is_owner(uid): return uid == OWNER_ID

def _cancel(store, key):
    if key in store:
        for t in store[key]: t.cancel()

async def safe_rename_guild(guild, name):
    try: await guild.edit(name=name)
    except: pass

async def safe_rename_channel(channel, name):
    try: await channel.edit(name=name[:100])
    except: pass

async def generate_elevenlabs(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"Accept":"audio/mpeg","Content-Type":"application/json","xi-api-key":ELEVENLABS_API_KEY}
    data = {"text":text,"model_id":"eleven_monolingual_v1","voice_settings":{"stability":0.5,"similarity_boost":0.8}}
    try:
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code == 200: return io.BytesIO(r.content)
    except: pass
    return None

# ──────────────────────────────────────────────────────────────────────────────
# BACKGROUND LOOPS — ALL CLIENTS FIRE SIMULTANEOUSLY, ZERO DELAY
# ──────────────────────────────────────────────────────────────────────────────

async def gc_nc_loop(guild_id: int, base: str, mode: str):
    """GC name changer — all accounts blast simultaneously."""
    texts = NCEMO_EMOJIS if mode == "ncemo" else RAID_TEXTS
    i = 0
    while True:
        try:
            tasks = []
            for c in all_clients:
                g = c.get_guild(guild_id)
                if g:
                    for _ in range(10):
                        tasks.append(safe_rename_guild(g, f"{base} {texts[i % len(texts)]}"))
                        i += 1
            if tasks: await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError: return
        except: pass

async def gc_ncbaap_loop(guild_id: int, base: str):
    """GOD LEVEL — all accounts, maximum blast."""
    i = 0
    while True:
        try:
            tasks = []
            for c in all_clients:
                g = c.get_guild(guild_id)
                if g:
                    for j in range(20):
                        tasks.append(safe_rename_guild(g, f"{base} {RAID_TEXTS[(i+j) % len(RAID_TEXTS)]}"))
            i += 20
            if tasks: await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError: return
        except: pass

async def gc_infinity_loop(guild_id: int, base: str):
    i = 0
    while True:
        try:
            tasks = []
            for c in all_clients:
                g = c.get_guild(guild_id)
                if g:
                    for j in range(10):
                        tasks.append(safe_rename_guild(g, f"{base} {INFINITY_TEXTS[(i+j) % len(INFINITY_TEXTS)]}"))
            i += 10
            if tasks: await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError: return
        except: pass

async def gc_infinity_godspeed_loop(guild_id: int, base: str):
    i = 0
    while True:
        try:
            tasks = []
            for c in all_clients:
                g = c.get_guild(guild_id)
                if g:
                    for j in range(25):
                        tasks.append(safe_rename_guild(g, f"{base} {INFINITY_TEXTS[(i+j) % len(INFINITY_TEXTS)]}"))
            i += 25
            if tasks: await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError: return
        except: pass

async def spam_loop(channel_id: int, guild_id, text: str):
    """All accounts blast 50 msgs at once — zero sleep."""
    while True:
        try:
            tasks = []
            for c in all_clients:
                ch = None
                if guild_id:
                    g = c.get_guild(guild_id)
                    ch = g.get_channel(channel_id) if g else None
                else:
                    ch = c.get_channel(channel_id)
                if ch:
                    tasks.extend([ch.send(text) for _ in range(50)])
            if tasks: await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError: return
        except: pass

async def channel_nc_loop(channel_id: int, guild_id: int, base: str, mode: str):
    """Channel name changer — all accounts rename simultaneously."""
    texts = NCEMO_EMOJIS if mode == "ncemo" else RAID_TEXTS
    i = 0
    while True:
        try:
            tasks = []
            for c in all_clients:
                g = c.get_guild(guild_id)
                ch = g.get_channel(channel_id) if g else None
                if ch:
                    for _ in range(8):
                        name = f"{base}-{texts[i % len(texts)]}".lower().replace(" ","-")[:100]
                        tasks.append(safe_rename_channel(ch, name))
                        i += 1
            if tasks: await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError: return
        except: pass

async def channel_ncbaap_loop(channel_id: int, guild_id: int, base: str):
    i = 0
    while True:
        try:
            tasks = []
            for c in all_clients:
                g = c.get_guild(guild_id)
                ch = g.get_channel(channel_id) if g else None
                if ch:
                    for j in range(15):
                        name = f"{base}-{RAID_TEXTS[(i+j) % len(RAID_TEXTS)]}".lower().replace(" ","-")[:100]
                        tasks.append(safe_rename_channel(ch, name))
            i += 15
            if tasks: await asyncio.gather(*tasks, return_exceptions=True)
        except asyncio.CancelledError: return
        except: pass

async def domain_expansion_loop(guild_id: int, base: str, mode: str):
    texts = DOMAIN_MODE_TEXTS.get(mode, RAID_TEXTS)
    i = 0
    while True:
        try:
            tasks = []
            for c in all_clients:
                g = c.get_guild(guild_id)
                if g:
                    tasks.append(safe_rename_guild(g, f"{base} {texts[i % len(texts)]}"))
            i += 1
            if tasks: await asyncio.gather(*tasks, return_exceptions=True)
            await asyncio.sleep(0.08)
        except asyncio.CancelledError: return
        except: await asyncio.sleep(0.3)

async def domain_expansion_watcher(guild_id: int, base: str):
    while True:
        try:
            await asyncio.sleep(3)
            for c in all_clients:
                g = c.get_guild(guild_id)
                if g and base.lower() not in (g.name or "").lower():
                    tasks = [safe_rename_guild(cc.get_guild(guild_id), f"{base} 😈♾️")
                             for cc in all_clients if cc.get_guild(guild_id)]
                    await asyncio.gather(*tasks, return_exceptions=True)
                    break
        except asyncio.CancelledError: return
        except: await asyncio.sleep(3)

# ──────────────────────────────────────────────────────────────────────────────
# SELFBOT CLIENT FACTORY
# ──────────────────────────────────────────────────────────────────────────────
def make_client(is_primary: bool) -> commands.Bot:
    client = commands.Bot(
        command_prefix=COMMAND_PREFIX,
        help_command=None,
        self_bot=True,
    )

    # ── ON READY ──────────────────────────────────────────────────────────────
    @client.event
    async def on_ready():
        all_clients.append(client)
        print(f"✅ Account online: {client.user} (primary={is_primary})")

    # ── ON MESSAGE — slide attacks ────────────────────────────────────────────
    @client.event
    async def on_message(message: discord.Message):
        if message.author == client.user:
            await client.process_commands(message)
            return
        uid = message.author.id
        if uid in slide_targets:
            tasks = [message.channel.send(t) for t in RAID_TEXTS[:5]]
            await asyncio.gather(*tasks, return_exceptions=True)
        if uid in slidespam_targets:
            tasks = [message.channel.send(t) for t in RAID_TEXTS]
            await asyncio.gather(*tasks, return_exceptions=True)

    # ──────────────────────────────────────────────────────────────────────────
    # Only primary account handles commands (prevents 12x replies)
    # ──────────────────────────────────────────────────────────────────────────
    if not is_primary:
        return client

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def sudo_only():
        async def pred(ctx): return is_sudo(ctx.author.id)
        return commands.check(pred)

    def owner_only():
        async def pred(ctx): return is_owner(ctx.author.id)
        return commands.check(pred)

    # ── CORE ──────────────────────────────────────────────────────────────────
    @client.command(name="start")
    async def start_cmd(ctx):
        await ctx.send(
            "⌬ ɪɴꜰɪɴɪᴛʏ ᴠ⁴ ꜱᴇʟꜰʙᴏᴛ\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"𝗦𝘆𝘀𝘁𝗲𝗺 𝗢𝗻𝗹𝗶𝗻𝗲 ✅\n"
            f"𝗔𝗰𝘁𝗶𝘃𝗲 𝗔𝗰𝗰𝗼𝘂𝗻𝘁𝘀 : {len(all_clients)}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"Type {COMMAND_PREFIX}help to see all commands"
        )

    @client.command(name="help")
    async def help_cmd(ctx):
        p = COMMAND_PREFIX
        text = (
            "╔═══════════════════════════╗\n"
            "║  ⌬  I N F I N I T Y  V 4  ║\n"
            "║  ◈  S E L F B O T  ◈      ║\n"
            "╚═══════════════════════════╝\n\n"
            "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
            "  💀  G C  N A M E  C H A N G E R\n"
            "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
            f"  ⌁ {p}gcnc <text>        » RAID style\n"
            f"  ⌁ {p}ncemo <text>       » Emoji style\n"
            f"  ⌁ {p}ncbaap <text>      » GOD LEVEL 👑\n"
            f"  ⌁ {p}stopgcnc  {p}stopncemo  {p}stopncbaap\n"
            f"  ⌁ {p}startallgc         » Run in all GCs\n\n"
            "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
            "  📢  C H A N N E L  N C\n"
            "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
            f"  ⌁ {p}cnc <text>         » RAID style\n"
            f"  ⌁ {p}cncemo <text>      » Emoji style\n"
            f"  ⌁ {p}cncbaap <text>     » GOD LEVEL 👑\n"
            f"  ⌁ {p}stopcnc\n\n"
            "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
            "  ♾️  I N F I N I T Y  N C\n"
            "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
            f"  ⌁ {p}infinity <text>\n"
            f"  ⌁ {p}infinityfast <text>\n"
            f"  ⌁ {p}infinitygodspeed <text>\n"
            f"  ⌁ {p}stopinfinity\n\n"
            "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
            "  😈  D O M A I N  E X P A N S I O N\n"
            "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
            f"  ⌁ {p}domainexpansiongcnc <text>\n"
            f"  ⌁ {p}domainexpansionncemo <text>\n"
            f"  ⌁ {p}domainexpansionncbaap <text>\n"
            f"  ⌁ {p}domainexpansioninfinity <text>\n"
            f"  ⌁ {p}stopdomainexpansion\n\n"
            "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
            "  💥  S P A M  &  S L I D E\n"
            "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
            f"  ⌁ {p}spam <text>        {p}unspam\n"
            f"  ⌁ {p}targetslide  (reply to msg)\n"
            f"  ⌁ {p}stopslide    (reply to msg)\n"
            f"  ⌁ {p}slidespam    (reply to msg)\n"
            f"  ⌁ {p}stopslidespam\n\n"
            "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
            "  🎵  V O I C E\n"
            "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
            f"  ⌁ {p}animevn <1-10> <text>\n"
            f"  ⌁ {p}voices\n\n"
            "◤━━━━━━━━━━━━━━━━━━━━━━━━◥\n"
            "  🤖  M A N A G E M E N T\n"
            "◣━━━━━━━━━━━━━━━━━━━━━━━━◢\n"
            f"  ⌁ {p}addsudo  {p}delsudo  {p}listsudo\n"
            f"  ⌁ {p}stopall  {p}status  {p}ping  {p}myid\n\n"
            f"╔══════════════════════════╗\n"
            f"║  ⚡ {len(all_clients)} Accounts  •  SUDO: Active  ║\n"
            "║  ♾️  Infinity V4 Selfbot  ║\n"
            "╚══════════════════════════╝"
        )
        await ctx.send(text)

    @client.command(name="ping")
    async def ping_cmd(ctx):
        s = time.time()
        msg = await ctx.send("🏓 Pinging...")
        await msg.edit(content=f"🏓 Pong! {int((time.time()-s)*1000)}ms")

    @client.command(name="myid")
    async def myid_cmd(ctx):
        await ctx.send(f"🆔 Your ID: `{ctx.author.id}`")

    # ── GC NAME CHANGER ───────────────────────────────────────────────────────
    @client.command(name="gcnc")
    @sudo_only()
    async def gcnc_cmd(ctx, *, text: str = ""):
        global current_running_command
        if not text: return await ctx.send("⚠️ Usage: .gcnc <text>")
        if not ctx.guild: return await ctx.send("❌ Server mein use karo!")
        current_running_command = f"gcnc:{text}"
        _cancel(group_tasks, ctx.guild.id)
        group_tasks[ctx.guild.id] = [asyncio.create_task(gc_nc_loop(ctx.guild.id, text, "gcnc"))]
        await ctx.send("🔄 GC Name Changer Started!")

    @client.command(name="ncemo")
    @sudo_only()
    async def ncemo_cmd(ctx, *, text: str = ""):
        global current_running_command
        if not text: return await ctx.send("⚠️ Usage: .ncemo <text>")
        if not ctx.guild: return await ctx.send("❌ Server mein use karo!")
        current_running_command = f"ncemo:{text}"
        _cancel(group_tasks, ctx.guild.id)
        group_tasks[ctx.guild.id] = [asyncio.create_task(gc_nc_loop(ctx.guild.id, text, "ncemo"))]
        await ctx.send("🎭 Emoji Name Changer Started!")

    @client.command(name="ncbaap")
    @sudo_only()
    async def ncbaap_cmd(ctx, *, text: str = ""):
        global current_running_command
        if not text: return await ctx.send("⚠️ Usage: .ncbaap <text>")
        if not ctx.guild: return await ctx.send("❌ Server mein use karo!")
        current_running_command = f"ncbaap:{text}"
        _cancel(group_tasks, ctx.guild.id)
        group_tasks[ctx.guild.id] = [asyncio.create_task(gc_ncbaap_loop(ctx.guild.id, text))]
        await ctx.send("👑🔥 GOD LEVEL NCBAAP ACTIVATED!")

    @client.command(name="stopgcnc")
    @sudo_only()
    async def stopgcnc_cmd(ctx):
        if ctx.guild and ctx.guild.id in group_tasks:
            _cancel(group_tasks, ctx.guild.id)
            del group_tasks[ctx.guild.id]
            await ctx.send("⏹ GC NC Stopped!")
        else: await ctx.send("❌ No active GC NC.")

    @client.command(name="stopncemo")
    @sudo_only()
    async def stopncemo_cmd(ctx): await stopgcnc_cmd(ctx)

    @client.command(name="stopncbaap")
    @sudo_only()
    async def stopncbaap_cmd(ctx): await stopgcnc_cmd(ctx)

    # ── INFINITY NC ───────────────────────────────────────────────────────────
    @client.command(name="infinity")
    @sudo_only()
    async def infinity_cmd(ctx, *, text: str = ""):
        global current_running_command
        if not text: return await ctx.send("⚠️ Usage: .infinity <text>")
        if not ctx.guild: return await ctx.send("❌ Server mein use karo!")
        current_running_command = f"infinity:{text}"
        _cancel(infinity_tasks, ctx.guild.id)
        infinity_tasks[ctx.guild.id] = [asyncio.create_task(gc_infinity_loop(ctx.guild.id, text))]
        await ctx.send("💀 Infinity Mode Activated!")

    @client.command(name="infinityfast")
    @sudo_only()
    async def infinityfast_cmd(ctx, *, text: str = ""):
        global current_running_command
        if not text: return await ctx.send("⚠️ Usage: .infinityfast <text>")
        if not ctx.guild: return await ctx.send("❌ Server mein use karo!")
        current_running_command = f"infinityfast:{text}"
        _cancel(infinity_tasks, ctx.guild.id)
        infinity_tasks[ctx.guild.id] = [asyncio.create_task(gc_infinity_loop(ctx.guild.id, text))]
        await ctx.send("⚡ Faster Infinity Activated!")

    @client.command(name="infinitygodspeed")
    @sudo_only()
    async def infinitygodspeed_cmd(ctx, *, text: str = ""):
        global current_running_command
        if not text: return await ctx.send("⚠️ Usage: .infinitygodspeed <text>")
        if not ctx.guild: return await ctx.send("❌ Server mein use karo!")
        current_running_command = f"infinitygodspeed:{text}"
        _cancel(infinity_tasks, ctx.guild.id)
        infinity_tasks[ctx.guild.id] = [asyncio.create_task(gc_infinity_godspeed_loop(ctx.guild.id, text))]
        await ctx.send("👑🔥 GOD SPEED Infinity ACTIVATED! 🚀")

    @client.command(name="stopinfinity")
    @sudo_only()
    async def stopinfinity_cmd(ctx):
        if ctx.guild and ctx.guild.id in infinity_tasks:
            _cancel(infinity_tasks, ctx.guild.id)
            del infinity_tasks[ctx.guild.id]
            await ctx.send("🛑 Infinity Stopped!")
        else: await ctx.send("❌ No active Infinity.")

    # ── CHANNEL NC ────────────────────────────────────────────────────────────
    @client.command(name="cnc")
    @sudo_only()
    async def cnc_cmd(ctx, *, text: str = ""):
        if not text: return await ctx.send("⚠️ Usage: .cnc <base-name>")
        if not ctx.guild: return await ctx.send("❌ Server mein use karo!")
        _cancel(channel_nc_tasks, ctx.channel.id)
        channel_nc_tasks[ctx.channel.id] = [asyncio.create_task(channel_nc_loop(ctx.channel.id, ctx.guild.id, text, "gcnc"))]
        await ctx.send(f"💀 Channel NC Started!")

    @client.command(name="cncemo")
    @sudo_only()
    async def cncemo_cmd(ctx, *, text: str = ""):
        if not text: return await ctx.send("⚠️ Usage: .cncemo <base-name>")
        if not ctx.guild: return await ctx.send("❌ Server mein use karo!")
        _cancel(channel_nc_tasks, ctx.channel.id)
        channel_nc_tasks[ctx.channel.id] = [asyncio.create_task(channel_nc_loop(ctx.channel.id, ctx.guild.id, text, "ncemo"))]
        await ctx.send(f"🎭 Emoji Channel NC Started!")

    @client.command(name="cncbaap")
    @sudo_only()
    async def cncbaap_cmd(ctx, *, text: str = ""):
        if not text: return await ctx.send("⚠️ Usage: .cncbaap <base-name>")
        if not ctx.guild: return await ctx.send("❌ Server mein use karo!")
        _cancel(channel_nc_tasks, ctx.channel.id)
        channel_nc_tasks[ctx.channel.id] = [asyncio.create_task(channel_ncbaap_loop(ctx.channel.id, ctx.guild.id, text))]
        await ctx.send(f"👑🔥 GOD LEVEL Channel NC ACTIVATED!")

    @client.command(name="stopcnc")
    @sudo_only()
    async def stopcnc_cmd(ctx):
        if ctx.channel.id in channel_nc_tasks:
            _cancel(channel_nc_tasks, ctx.channel.id)
            del channel_nc_tasks[ctx.channel.id]
            await ctx.send("⏹ Channel NC Stopped!")
        else: await ctx.send("❌ No active Channel NC.")

    # ── SPAM ──────────────────────────────────────────────────────────────────
    @client.command(name="spam")
    @sudo_only()
    async def spam_cmd(ctx, *, text: str = ""):
        global current_running_command
        if not text: return await ctx.send("⚠️ Usage: .spam <text>")
        cid = ctx.channel.id
        gid = ctx.guild.id if ctx.guild else None
        current_running_command = f"spam:{text}"
        _cancel(spam_tasks, cid)
        spam_tasks[cid] = [asyncio.create_task(spam_loop(cid, gid, text))]
        await ctx.send("💥 SPAM STARTED!")

    @client.command(name="unspam")
    @sudo_only()
    async def unspam_cmd(ctx):
        cid = ctx.channel.id
        if cid in spam_tasks:
            _cancel(spam_tasks, cid)
            del spam_tasks[cid]
            await ctx.send("🛑 Spam Stopped!")
        else: await ctx.send("❌ No active spam.")

    # ── SLIDE ─────────────────────────────────────────────────────────────────
    @client.command(name="targetslide")
    @sudo_only()
    async def targetslide_cmd(ctx):
        ref = ctx.message.reference
        if not ref: return await ctx.send("⚠️ Reply to a user's message!")
        msg = await ctx.channel.fetch_message(ref.message_id)
        slide_targets.add(msg.author.id)
        await ctx.send(f"🎯 Slide target set: `{msg.author.id}`")

    @client.command(name="stopslide")
    @sudo_only()
    async def stopslide_cmd(ctx):
        ref = ctx.message.reference
        if not ref: return await ctx.send("⚠️ Reply to a user's message!")
        msg = await ctx.channel.fetch_message(ref.message_id)
        slide_targets.discard(msg.author.id)
        await ctx.send(f"🛑 Slide stopped for: `{msg.author.id}`")

    @client.command(name="slidespam")
    @sudo_only()
    async def slidespam_cmd(ctx):
        ref = ctx.message.reference
        if not ref: return await ctx.send("⚠️ Reply to a user's message!")
        msg = await ctx.channel.fetch_message(ref.message_id)
        slidespam_targets.add(msg.author.id)
        await ctx.send(f"💥 Slide spam started for: `{msg.author.id}`")

    @client.command(name="stopslidespam")
    @sudo_only()
    async def stopslidespam_cmd(ctx):
        ref = ctx.message.reference
        if not ref: return await ctx.send("⚠️ Reply to a user's message!")
        msg = await ctx.channel.fetch_message(ref.message_id)
        slidespam_targets.discard(msg.author.id)
        await ctx.send(f"🛑 Slide spam stopped for: `{msg.author.id}`")

    # ── DOMAIN EXPANSION ──────────────────────────────────────────────────────
    async def _start_domain(ctx, base: str, mode: str):
        if not ctx.guild: return await ctx.send("❌ Server mein use karo!")
        gid = ctx.guild.id
        if gid in domain_expansion_chats:
            for t in domain_expansion_chats[gid]: t.cancel()
        mode_labels = {"gcnc":"💀 GCNC","ncemo":"🎭 NCEMO","ncbaap":"👑 NCBAAP","infinity":"♾️ INFINITY"}
        caption = (
            "╔══════════════════════════════╗\n"
            "║   😈  D O M A I N           ║\n"
            "║      E X P A N S I O N  ♾️  ║\n"
            "╚══════════════════════════════╝\n\n"
            f"  📛  Base   : {base}\n"
            f"  ⚙️  Mode   : {mode_labels.get(mode, mode)}\n"
            f"  ⚡  Accounts: {len(all_clients)} active\n\n"
            "  ◈ Name cycling — ENGAGED\n"
            "  ◈ Rate limit consumed — ENEMY SLOWED\n"
            "  ◈ Watcher — ONLINE\n\n"
            f"  ➡ {COMMAND_PREFIX}stopdomainexpansion to lift"
        )
        await ctx.send(caption)
        domain_expansion_chats[gid] = [
            asyncio.create_task(domain_expansion_loop(gid, base, mode)),
            asyncio.create_task(domain_expansion_watcher(gid, base)),
        ]

    @client.command(name="domainexpansiongcnc")
    @sudo_only()
    async def de_gcnc(ctx, *, text: str = ""):
        if not text: return await ctx.send("⚠️ Usage: .domainexpansiongcnc <text>")
        await _start_domain(ctx, text, "gcnc")

    @client.command(name="domainexpansionncemo")
    @sudo_only()
    async def de_ncemo(ctx, *, text: str = ""):
        if not text: return await ctx.send("⚠️ Usage: .domainexpansionncemo <text>")
        await _start_domain(ctx, text, "ncemo")

    @client.command(name="domainexpansionncbaap")
    @sudo_only()
    async def de_ncbaap(ctx, *, text: str = ""):
        if not text: return await ctx.send("⚠️ Usage: .domainexpansionncbaap <text>")
        await _start_domain(ctx, text, "ncbaap")

    @client.command(name="domainexpansioninfinity")
    @sudo_only()
    async def de_infinity(ctx, *, text: str = ""):
        if not text: return await ctx.send("⚠️ Usage: .domainexpansioninfinity <text>")
        await _start_domain(ctx, text, "infinity")

    @client.command(name="stopdomainexpansion")
    @sudo_only()
    async def stopde_cmd(ctx):
        gid = ctx.guild.id if ctx.guild else None
        if gid and gid in domain_expansion_chats:
            for t in domain_expansion_chats[gid]: t.cancel()
            del domain_expansion_chats[gid]
            await ctx.send("✅ Domain Expansion LIFTED.\n♾️ The barrier is gone.")
        else: await ctx.send("❌ No active Domain Expansion.")

    # ── STARTALLGC ────────────────────────────────────────────────────────────
    @client.command(name="startallgc")
    @sudo_only()
    async def startallgc_cmd(ctx):
        global current_running_command
        if not current_running_command:
            return await ctx.send("❌ No command running! Start one first.")
        active = set(group_tasks) | set(infinity_tasks) | set(spam_tasks)
        if not active: return await ctx.send("❌ No active groups found!")
        cmd, *rest = current_running_command.split(":")
        args = ":".join(rest) or "INFINITY"
        count = 0
        for gid in active:
            try:
                if cmd in ("gcnc", "ncemo"):
                    _cancel(group_tasks, gid)
                    group_tasks[gid] = [asyncio.create_task(gc_nc_loop(gid, args, cmd))]
                elif cmd == "ncbaap":
                    _cancel(group_tasks, gid)
                    group_tasks[gid] = [asyncio.create_task(gc_ncbaap_loop(gid, args))]
                elif cmd == "infinitygodspeed":
                    _cancel(infinity_tasks, gid)
                    infinity_tasks[gid] = [asyncio.create_task(gc_infinity_godspeed_loop(gid, args))]
                elif cmd in ("infinity", "infinityfast"):
                    _cancel(infinity_tasks, gid)
                    infinity_tasks[gid] = [asyncio.create_task(gc_infinity_loop(gid, args))]
                count += 1
            except: pass
        await ctx.send(f"✅ Started '{cmd}' in {count} server(s)!\n🤖 {len(all_clients)} accounts active")

    # ── ADD ALL ACCOUNTS TO GROUP DM ─────────────────────────────────────────
    @client.command(name="add")
    @sudo_only()
    async def add_cmd(ctx):
        """
        .add — All connected accounts add each other into this Group DM.
        Works ONLY in Group DMs (not in servers).
        """
        ch = ctx.channel

        # Must be a GroupChannel (Group DM)
        if not isinstance(ch, discord.GroupChannel):
            return await ctx.send(
                "❌ Yeh command sirf **Group DM** mein kaam karta hai!\nServer mein nahi chalega."
            )

        if len(all_clients) < 2:
            return await ctx.send("❌ Kam se kam 2 accounts connected hone chahiye!")

        # ── Animation setup ──────────────────────────────────────────────────
        SPIN   = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        FILL   = "█"
        EMPTY  = "░"
        BAR_LEN = 12

        all_uids     = [c.user.id for c in all_clients if c.user]
        total        = len(all_uids)
        existing_ids = {m.id for m in ch.recipients}
        existing_ids.add(ch.owner_id)

        added   = []
        failed  = []
        already = []
        fi      = 0   # frame index

        def bar(done):
            pct    = done / total if total else 0
            filled = int(BAR_LEN * pct)
            return f"[{FILL*filled}{EMPTY*(BAR_LEN-filled)}] {int(pct*100)}%"

        def frame(done, name, status_line):
            spin = SPIN[fi % len(SPIN)]
            return (
                "╔══════════════════════════╗\n"
                "║   🤖  B O T  A D D E R   ║\n"
                "╚══════════════════════════╝\n"
                "\n"
                f"  {spin}  {status_line}\n"
                "\n"
                f"  {bar(done)}\n"
                "\n"
                f"  ✅ Added   : {len(added)}\n"
                f"  ⏭️ Already : {len(already)}\n"
                f"  ❌ Failed  : {len(failed)}\n"
                f"  📦 Total   : {total}\n"
                "\n"
                f"  👤 {name}"
            )

        status = await ctx.send(frame(0, "Starting...", "Initializing..."))

        for idx2, uid in enumerate(all_uids):
            # Get username for animation
            try:
                u = await client.fetch_user(uid)
                uname = str(u)
            except Exception:
                uname = f"ID:{uid}"

            # Show spinner while processing
            fi += 1
            await status.edit(content=frame(idx2, uname, "Adding..."))

            if uid in existing_ids:
                already.append(uid)
                await asyncio.sleep(0.15)
                continue

            # Try each account to add this user via Discord API
            success = False
            for adder in all_clients:
                try:
                    url = f"https://discord.com/api/v9/channels/{ch.id}/recipients/{uid}"
                    headers = {"Authorization": adder.http.token, "Content-Type": "application/json"}
                    async with aiohttp.ClientSession() as session:
                        async with session.put(url, headers=headers) as resp:
                            if resp.status in (200, 201, 204):
                                added.append(uid)
                                success = True
                                break
                except Exception:
                    continue

            if not success:
                failed.append(uid)

            # 3 spinner ticks after each add (smooth animation)
            for _ in range(3):
                fi += 1
                label = "✅ Added!" if success else "❌ Failed"
                await status.edit(content=frame(idx2+1, f"{uname} — {label}", "Adding..."))
                await asyncio.sleep(0.15)

            await asyncio.sleep(0.2)

        # ── Final result ─────────────────────────────────────────────────────
        result = (
            "╔══════════════════════════╗\n"
            "║   ✅  A D D  D O N E !   ║\n"
            "╚══════════════════════════╝\n"
            "\n"
            f"  {bar(total)}\n"
            "\n"
            f"  ✅ Added   : {len(added)} accounts\n"
            f"  ⏭️ Already : {len(already)} already in GC\n"
            f"  ❌ Failed  : {len(failed)} accounts\n"
            f"  📦 Total   : {total}\n"
            "\n"
            f"  🔗 Group: {ch.name or 'Group DM'}\n"
        )
        if failed:
            result += f"\n  ⚠️ Failed IDs: {', '.join(str(x) for x in failed)}\n"
            result += "  (Friend request required first!)"

        await status.edit(content=result)

    # ── STOP ALL ──────────────────────────────────────────────────────────────
    @client.command(name="stopall")
    @sudo_only()
    async def stopall_cmd(ctx):
        for d in (group_tasks, infinity_tasks, spam_tasks, react_tasks, channel_nc_tasks):
            for tlist in d.values():
                for t in tlist: t.cancel()
            d.clear()
        slide_targets.clear()
        slidespam_targets.clear()
        for tlist in domain_expansion_chats.values():
            for t in tlist: t.cancel()
        domain_expansion_chats.clear()
        await ctx.send("⏹ ALL ACTIVITIES STOPPED!")

    # ── STATUS ────────────────────────────────────────────────────────────────
    @client.command(name="status")
    @sudo_only()
    async def status_cmd(ctx):
        await ctx.send(
            f"📊 **Infinity V4 Selfbot Status**\n\n"
            f"🎀 GC NC: {sum(len(v) for v in group_tasks.values())}\n"
            f"♾️ Infinity NC: {sum(len(v) for v in infinity_tasks.values())}\n"
            f"😹 Spam: {sum(len(v) for v in spam_tasks.values())}\n"
            f"📢 Channel NC: {sum(len(v) for v in channel_nc_tasks.values())}\n"
            f"🪼 Slide Targets: {len(slide_targets)}\n"
            f"💥 Slide Spam: {len(slidespam_targets)}\n"
            f"😈 Domain Expansions: {len(domain_expansion_chats)}\n\n"
            f"⚡ Active Accounts: {len(all_clients)}\n"
            f"👑 SUDO Users: {len(SUDO_USERS)}"
        )

    # ── SUDO ──────────────────────────────────────────────────────────────────
    @client.command(name="addsudo")
    @owner_only()
    async def addsudo_cmd(ctx):
        ref = ctx.message.reference
        if not ref: return await ctx.send("⚠️ Reply to a user's message!")
        msg = await ctx.channel.fetch_message(ref.message_id)
        SUDO_USERS.add(msg.author.id); save_sudo()
        await ctx.send(f"✅ SUDO added: `{msg.author.id}`")

    @client.command(name="delsudo")
    @owner_only()
    async def delsudo_cmd(ctx):
        ref = ctx.message.reference
        if not ref: return await ctx.send("⚠️ Reply to a user's message!")
        msg = await ctx.channel.fetch_message(ref.message_id)
        SUDO_USERS.discard(msg.author.id); save_sudo()
        await ctx.send(f"🗑 SUDO removed: `{msg.author.id}`")

    @client.command(name="listsudo")
    @sudo_only()
    async def listsudo_cmd(ctx):
        lines = "\n".join(f"👑 `{uid}`" for uid in SUDO_USERS)
        await ctx.send(f"👑 **SUDO Users:**\n{lines}")

    # ── VOICE ─────────────────────────────────────────────────────────────────
    @client.command(name="voices")
    @sudo_only()
    async def voices_cmd(ctx):
        lines = ["🎭 **Available Voices:**\n"]
        for n, v in VOICE_CHARACTERS.items():
            lines.append(f"`{n}.` **{v['name']}**")
        lines.append(f"\n🎀 Usage: `{COMMAND_PREFIX}animevn 1 Hello world`")
        await ctx.send("\n".join(lines))

    @client.command(name="animevn")
    @sudo_only()
    async def animevn_cmd(ctx, *, args: str = ""):
        if not args: return await ctx.send("⚠️ Usage: .animevn <1-10> <text>")
        tokens = args.split()
        char_nums, text_parts = [], []
        for t in tokens:
            if t.isdigit() and int(t) in VOICE_CHARACTERS: char_nums.append(int(t))
            else: text_parts.append(t)
        if not char_nums: return await ctx.send("❌ Valid numbers: 1–10")
        text = " ".join(text_parts)
        if not text: return await ctx.send("❌ Text bhi dalo!")
        await ctx.send(f"🎭 Generating voices for: {', '.join(VOICE_CHARACTERS[n]['name'] for n in char_nums)}…")
        for cn in char_nums:
            vc = VOICE_CHARACTERS[cn]
            audio = await generate_elevenlabs(text, vc["voice_id"])
            if audio:
                await ctx.send(f"🎀 **{vc['name']}**: {text}", file=discord.File(audio, filename=f"{vc['name']}.mp3"))
            else:
                await ctx.send(f"❌ {vc['name']} voice failed (ElevenLabs error)")
            await asyncio.sleep(0.5)

    # ── ERROR HANDLER ─────────────────────────────────────────────────────────
    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ Missing: `{error.param.name}`")

    return client


# ──────────────────────────────────────────────────────────────────────────────
# MAIN — launch all accounts concurrently, auto-restart on crash
# ──────────────────────────────────────────────────────────────────────────────
async def start_account_safe(token: str, idx: int):
    """Start one account — retry forever on disconnect, skip on bad token."""
    while True:
        c = make_client(idx == 0)
        try:
            print(f"🔄 Account slot {idx+1} connecting…")
            await c.start(token)
        except discord.LoginFailure:
            print(f"❌ Slot {idx+1}: INVALID TOKEN — skipping.")
            return
        except Exception as e:
            print(f"⚠️ Slot {idx+1} offline: {e} — retry in 5s…")
            if c in all_clients: all_clients.remove(c)
            try: await c.close()
            except: pass
            await asyncio.sleep(5)

async def main():
    # Filter out placeholder accounts
    valid_accounts = [
        a for a in ACCOUNTS
        if a.get("email","").strip() and not a.get("email","").startswith("account")
        and a.get("password","").strip() and not a.get("password","").startswith("password")
    ]
    if not valid_accounts:
        print("❌ Koi account nahi mila! ACCOUNTS list mein email aur password daalo.")
        return

    print(f"🔑 {len(valid_accounts)} accounts mili — logging in...")
    print(f"📌 Command prefix: {COMMAND_PREFIX}")
    print(f"⚠️ Selfbots violate Discord ToS — use at own risk!")

    # Login all accounts and get tokens
    tokens = []
    for idx, acc in enumerate(valid_accounts):
        token = await fetch_token(acc["email"], acc["password"], idx)
        if token:
            tokens.append((idx, token))
        await asyncio.sleep(1)  # small gap between logins

    if not tokens:
        print("❌ Koi bhi account login nahi hua! Email/password check karo.")
        return

    print(f"\n🚀 {len(tokens)} accounts login ho gaye! Starting selfbots...")
    await asyncio.gather(
        *(start_account_safe(str(tok), int(idx)) for idx, tok in tokens),
        return_exceptions=True
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Infinity V4 Selfbot — Shutting Down…")
    except Exception as e:
        print(f"❌ Fatal: {e}")
