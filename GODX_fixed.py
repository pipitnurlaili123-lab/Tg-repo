import asyncio, time, json, os
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    ContextTypes, MessageHandler, filters
)
from telegram.error import RetryAfter, TelegramError

# ================= CONFIG =================
OWNER_IDS = {8494250384, 8487244010}

BOT_TOKENS = [
    "8551526198:AAELxyJdcM10aonnY9tvBdqzsKm_LHStvfs",
    "8324923033:AAHAovFD5j9X2rL0CkWIuJQe0AC_WBXXH9Q",
    "8237364355:AAG6C5XlbofiPlK2Tf4iyXB71NoGB4uCy9M",
    "8047490837:AAEdfZ3ShKg5DhKimVu2VWbfJbBzuiKUKI0",
    "8242160554:AAExZowpOntXa_cijVlBl8AGTNqH5p4KgMU",
    "8541010607:AAEvqKj3deMTFMQ1I5yHLK_p_mT-9Gmyo5s",
    "7978564227:AAGc02N4GYXa-852skajtjqjL8C9lU72HGc",
    "8291912901:AAEABBz77uG7-pOacoxIx41fGHZiKZYTARo",
    "8507378731:AAGqWKDKjWonBKKDbJwkZmJ30xsD1pRzNF0",
    "8417620739:AAEZJYqANK0r0k7ARSU8_6-js6JhHOOyYMo",
    "7686787498:AAF6Q2fbJSZ_kTFpRH-AHM9GOLaUWoMuxZc",
    "8378349723:AAG3jjNMzxFjtrJZ4KjR5VmK7gbxZhQp7s8",
]

RAINBOW = ["🔴","🟠","🟡","🟢","🔵","🟣","⚪","⚫"]
MAX_TITLE = 255

NORMAL_RPS = 12
BOOST_RPS = 20
BOOST_TIME = 15

SPAM_SPEEDS = {"s1": 0.12, "s2": 0.08, "s3": 0.04}
STICKER_SPEEDS = {"st1": 0.15, "st2": 0.10, "st3": 0.05}

# ================= ANIMATION FRAMES =================
LOADING_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
FIRE_FRAMES = ["🔥", "🔴", "🟠", "🟡", "⚡", "💥"]
WAVE_FRAMES = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"]

# =========================================
BOTS = [Bot(t) for t in BOT_TOKENS]
BOT_GROUPS = [BOTS[:6], BOTS[6:]]
ACTIVE_GROUP = 0

def switch_group():
    global ACTIVE_GROUP
    ACTIVE_GROUP = (ACTIVE_GROUP + 1) % len(BOT_GROUPS)

TARGET_ID = None
running = False
boosting = False
BASE_TEXT = ""
tasks = []
spam_tasks = []
sticker_tasks = []

wave = 0
INTERVAL = 1 / NORMAL_RPS
lock = asyncio.Lock()
last_action = 0

TRACKED_MESSAGES = []

# ================= STATS =================
stats = {
    "rename_count": 0,
    "spam_count": 0,
    "sticker_count": 0,
    "errors": 0,
    "start_time": None,
    "boost_count": 0
}

# ================= CONSOLE ANIMATION =================
class ConsoleUI:
    @staticmethod
    def clear_line():
        print("\r" + " " * 100 + "\r", end="", flush=True)
    
    @staticmethod
    def animate_startup():
        frames = LOADING_FRAMES
        print("\n" + "═" * 60)
        for i in range(20):
            frame = frames[i % len(frames)]
            print(f"\r{frame} Initializing INFINITY System... {frame}", end="", flush=True)
            time.sleep(0.1)
        print("\n" + "═" * 60 + "\n")
    
    @staticmethod
    def show_banner():
        banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║      ██╗███╗   ██╗███████╗██╗███╗   ██╗██╗████████╗██╗ ║
║      ██║████╗  ██║██╔════╝██║████╗  ██║██║╚══██╔══╝╚██║ ║
║      ██║██╔██╗ ██║█████╗  ██║██╔██╗ ██║██║   ██║    ╚═╝ ║
║      ██║██║╚██╗██║██╔══╝  ██║██║╚██╗██║██║   ██║    ██╗ ║
║      ██║██║ ╚████║██║     ██║██║ ╚████║██║   ██║    ╚═╝ ║
║      ╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝        ║
║                                                          ║
║              CONTROL SYSTEM v2.0 ENHANCED                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    @staticmethod
    def log_action(action_type, message, emoji="ℹ️"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {emoji} {action_type:12s} │ {message}")
    
    @staticmethod
    def log_stats():
        uptime = time.time() - stats["start_time"] if stats["start_time"] else 0
        uptime_str = f"{int(uptime // 60)}m {int(uptime % 60)}s"
        
        print("\n" + "─" * 60)
        print(f"📊 LIVE STATS │ Uptime: {uptime_str}")
        print("─" * 60)
        print(f"  🔄 Renames:  {stats['rename_count']:,}")
        print(f"  💬 Messages: {stats['spam_count']:,}")
        print(f"  🎨 Stickers: {stats['sticker_count']:,}")
        print(f"  ⚡ Boosts:   {stats['boost_count']}")
        print(f"  ❌ Errors:   {stats['errors']}")
        print("─" * 60 + "\n")

ui = ConsoleUI()

# ================= UTILS =================
def is_admin(uid):
    is_owner = uid in OWNER_IDS
    ui.log_action("AUTH", f"User {uid} - Admin: {is_owner}", "🔐")
    return is_owner

def build_title(text):
    global wave
    emoji = RAINBOW[wave % len(RAINBOW)]
    wave += 1
    return f"{text} {emoji}"[:MAX_TITLE]

async def rate_wait():
    global last_action
    async with lock:
        now = time.monotonic()
        wait = INTERVAL - (now - last_action)
        if wait > 0:
            await asyncio.sleep(wait)
        last_action = time.monotonic()

# ================= WORKERS =================
async def rename_worker(bot: Bot, bot_index: int):
    global running, INTERVAL, boosting
    while running:
        try:
            await rate_wait()
            await bot.set_chat_title(TARGET_ID, build_title(BASE_TEXT))
            stats["rename_count"] += 1
            
            # Animated console output
            frame = FIRE_FRAMES[stats["rename_count"] % len(FIRE_FRAMES)]
            rate = "BOOST" if boosting else "NORMAL"
            ui.clear_line()
            print(f"\r{frame} Bot#{bot_index+1} │ Renames: {stats['rename_count']:,} │ Mode: {rate}", end="", flush=True)
            
        except RetryAfter as e:
            switch_group()
            boosting = False
            INTERVAL = 1 / NORMAL_RPS
            stats["errors"] += 1
            ui.log_action("ERROR", f"Rate limit! Waiting {e.retry_after}s", "⚠️")
            await asyncio.sleep(e.retry_after)
        except TelegramError as e:
            stats["errors"] += 1
            ui.log_action("ERROR", f"Telegram error: {str(e)}", "❌")
            await asyncio.sleep(1)

async def spam_worker(bot: Bot, chat_id, text, delay, bot_index: int):
    while True:
        try:
            msg = await bot.send_message(chat_id, text)
            TRACKED_MESSAGES.append((chat_id, msg.message_id))
            stats["spam_count"] += 1
            
            wave_frame = WAVE_FRAMES[stats["spam_count"] % len(WAVE_FRAMES)]
            ui.clear_line()
            print(f"\r{wave_frame} Spam Bot#{bot_index+1} │ Sent: {stats['spam_count']:,} msgs", end="", flush=True)
            
            await asyncio.sleep(delay)
        except RetryAfter as e:
            stats["errors"] += 1
            ui.log_action("SPAM", f"Rate limit! Waiting {e.retry_after}s", "⚠️")
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            stats["errors"] += 1
            ui.log_action("ERROR", f"Spam error: {str(e)}", "❌")
            await asyncio.sleep(1)

async def sticker_spam_worker(bot: Bot, chat_id, sticker_id, delay, bot_index: int):
    """New: Sticker spam worker"""
    while True:
        try:
            msg = await bot.send_sticker(chat_id, sticker_id)
            TRACKED_MESSAGES.append((chat_id, msg.message_id))
            stats["sticker_count"] += 1
            
            sticker_frame = "🎨" if stats["sticker_count"] % 2 == 0 else "🖼️"
            ui.clear_line()
            print(f"\r{sticker_frame} Sticker Bot#{bot_index+1} │ Sent: {stats['sticker_count']:,} stickers", end="", flush=True)
            
            await asyncio.sleep(delay)
        except RetryAfter as e:
            stats["errors"] += 1
            ui.log_action("STICKER", f"Rate limit! Waiting {e.retry_after}s", "⚠️")
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            stats["errors"] += 1
            ui.log_action("ERROR", f"Sticker error: {str(e)}", "❌")
            await asyncio.sleep(1)

async def boost_timer():
    global boosting, INTERVAL
    ui.log_action("BOOST", f"Activated for {BOOST_TIME}s", "⚡")
    await asyncio.sleep(BOOST_TIME)
    boosting = False
    INTERVAL = 1 / NORMAL_RPS
    ui.log_action("BOOST", "Deactivated - returning to normal speed", "🔽")

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/start from user {user_id}", "🚀")
    
    await update.message.reply_text(
        "✅ Bot is ONLINE!\n\n"
        "Use /menu to see all commands"
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/menu from user {user_id}", "📋")
    
    await update.message.reply_text(
        "╔════════════════════════════════════╗\n"
        "       ⚡ INFINITY CONTROL v2.0 ⚡\n"
        "╚════════════════════════════════════╝\n\n"
        "📌 RENAME SYSTEM\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "➤ /nc <text>\n"
        "   └─ Rename (10 min)\n"
        "➤ /ncloop <text>\n"
        "   └─ Rename (Infinite)\n"
        "➤ /boost\n"
        "   └─ Speed Burst (15s)\n"
        "➤ /ncoff\n"
        "   └─ Stop Rename\n\n"
        "💬 MESSAGE SPAM\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "➤ /s1 <text>  ─ 120ms delay\n"
        "➤ /s2 <text>  ─ 80ms delay\n"
        "➤ /s3 <text>  ─ 40ms delay\n"
        "➤ /spamoff    ─ Stop message spam\n\n"
        "🎨 STICKER SPAM (NEW!)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "➤ Reply to sticker:\n"
        "   /st1  ─ 150ms delay\n"
        "   /st2  ─ 100ms delay\n"
        "   /st3  ─ 50ms delay (EXTREME)\n"
        "➤ /stoff  ─ Stop sticker spam\n\n"
        "🧹 CLEANUP\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "➤ /clean\n"
        "   └─ Delete tracked messages\n\n"
        "📊 STATISTICS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "➤ /stats\n"
        "   └─ Show live statistics\n\n"
        "☠️ TERMINATE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "➤ /offall\n"
        "   └─ Stop ALL operations\n\n"
        "════════════════════════════════════\n"
        "   Powered by INFINITY 🚀\n"
        "   Enhanced UI | Faster Performance"
    )

async def nc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BASE_TEXT, TARGET_ID, running, tasks
    
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/nc from user {user_id}", "🔄")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /nc <text>")
        return
    
    BASE_TEXT = " ".join(context.args)
    TARGET_ID = update.effective_chat.id
    running = True
    
    if stats["start_time"] is None:
        stats["start_time"] = time.time()
    
    ui.log_action("NC", f"Started with text: '{BASE_TEXT}'", "🔥")
    
    tasks = [
        asyncio.create_task(rename_worker(b, i)) 
        for i, b in enumerate(BOT_GROUPS[ACTIVE_GROUP])
    ]
    asyncio.create_task(auto_stop(600))
    
    await update.message.reply_text(
        "╔═══════════════════════╗\n"
        "   🔥 NC ACTIVATED 🔥\n"
        "╠═══════════════════════╣\n"
        f"  Text: {BASE_TEXT[:20]}...\n"
        f"  Duration: 10 minutes\n"
        f"  Bots: {len(BOT_GROUPS[ACTIVE_GROUP])}\n"
        "╚═══════════════════════╝"
    )

async def ncloop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BASE_TEXT, TARGET_ID, running, tasks
    
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/ncloop from user {user_id}", "♾️")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /ncloop <text>")
        return
    
    BASE_TEXT = " ".join(context.args)
    TARGET_ID = update.effective_chat.id
    running = True
    
    if stats["start_time"] is None:
        stats["start_time"] = time.time()
    
    ui.log_action("NC LOOP", f"Started infinite rename: '{BASE_TEXT}'", "♾️")
    
    tasks = [
        asyncio.create_task(rename_worker(b, i)) 
        for i, b in enumerate(BOT_GROUPS[ACTIVE_GROUP])
    ]
    
    await update.message.reply_text(
        "╔═══════════════════════╗\n"
        "  ♾️  NC LOOP ACTIVE ♾️\n"
        "╠═══════════════════════╣\n"
        f"  Text: {BASE_TEXT[:20]}...\n"
        "  Duration: INFINITE\n"
        f"  Bots: {len(BOT_GROUPS[ACTIVE_GROUP])}\n"
        "╚═══════════════════════╝"
    )

async def auto_stop(sec):
    global running, tasks
    await asyncio.sleep(sec)
    running = False
    for t in tasks: t.cancel()
    tasks.clear()
    ui.log_action("NC", "Auto-stopped after 10 minutes", "🛑")

async def boost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global boosting, INTERVAL
    
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/boost from user {user_id}", "⚡")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    boosting = True
    INTERVAL = 1 / BOOST_RPS
    stats["boost_count"] += 1
    
    asyncio.create_task(boost_timer())
    
    await update.message.reply_text(
        "╔═══════════════════════╗\n"
        "   ⚡ BOOST ENGAGED ⚡\n"
        "╠═══════════════════════╣\n"
        f"  Speed: {BOOST_RPS} req/s\n"
        f"  Duration: {BOOST_TIME}s\n"
        "  Status: TURBO MODE\n"
        "╚═══════════════════════╝"
    )

async def spam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cmd = update.message.text.split()[0][1:]
    ui.log_action("COMMAND", f"/{cmd} from user {user_id}", "💬")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    if not context.args:
        await update.message.reply_text(f"❌ Usage: /{cmd} <text>")
        return
    
    delay = SPAM_SPEEDS.get(cmd)
    text = " ".join(context.args)
    
    ui.log_action("SPAM", f"Started {cmd.upper()} mode: '{text[:30]}...'", "💬")
    
    for i, b in enumerate(BOT_GROUPS[ACTIVE_GROUP]):
        spam_tasks.append(asyncio.create_task(
            spam_worker(b, update.effective_chat.id, text, delay, i)
        ))
    
    await update.message.reply_text(
        f"╔═══════════════════════╗\n"
        f"  💬 SPAM {cmd.upper()} ACTIVE 💬\n"
        f"╠═══════════════════════╣\n"
        f"  Delay: {int(delay*1000)}ms\n"
        f"  Bots: {len(BOT_GROUPS[ACTIVE_GROUP])}\n"
        f"  Text: {text[:20]}...\n"
        f"╚═══════════════════════╝"
    )

async def sticker_spam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """New: Sticker spam command"""
    user_id = update.effective_user.id
    cmd = update.message.text.split()[0][1:]
    ui.log_action("COMMAND", f"/{cmd} from user {user_id}", "🎨")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    # Check if replying to a sticker
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("❌ Please reply to a sticker to spam it!")
        return
    
    delay = STICKER_SPEEDS.get(cmd)
    sticker_id = update.message.reply_to_message.sticker.file_id
    
    ui.log_action("STICKER", f"Started {cmd.upper()} mode", "🎨")
    
    for i, b in enumerate(BOT_GROUPS[ACTIVE_GROUP]):
        sticker_tasks.append(asyncio.create_task(
            sticker_spam_worker(b, update.effective_chat.id, sticker_id, delay, i)
        ))
    
    await update.message.reply_text(
        f"╔═══════════════════════╗\n"
        f"  🎨 STICKER {cmd.upper()} 🎨\n"
        f"╠═══════════════════════╣\n"
        f"  Delay: {int(delay*1000)}ms\n"
        f"  Bots: {len(BOT_GROUPS[ACTIVE_GROUP])}\n"
        f"  Status: SPAMMING\n"
        f"╚═══════════════════════╝"
    )

async def spam_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/spamoff from user {user_id}", "🛑")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    count = len(spam_tasks)
    for t in spam_tasks: t.cancel()
    spam_tasks.clear()
    
    ui.log_action("SPAM", f"Stopped {count} spam tasks", "🛑")
    await update.message.reply_text(f"🛑 MESSAGE SPAM STOPPED\n📊 Sent: {stats['spam_count']:,} messages")

async def sticker_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """New: Stop sticker spam"""
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/stoff from user {user_id}", "🛑")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    count = len(sticker_tasks)
    for t in sticker_tasks: t.cancel()
    sticker_tasks.clear()
    
    ui.log_action("STICKER", f"Stopped {count} sticker tasks", "🛑")
    await update.message.reply_text(f"🛑 STICKER SPAM STOPPED\n📊 Sent: {stats['sticker_count']:,} stickers")

async def nc_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global running, tasks
    
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/ncoff from user {user_id}", "🛑")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    running = False
    count = len(tasks)
    for t in tasks: t.cancel()
    tasks.clear()
    
    ui.log_action("NC", "Stopped rename system", "🛑")
    await update.message.reply_text(f"🛑 NC STOPPED\n📊 Total renames: {stats['rename_count']:,}")

async def off_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global running, boosting, INTERVAL
    
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/offall from user {user_id}", "☠️")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    running = False
    boosting = False
    INTERVAL = 1 / NORMAL_RPS
    
    all_tasks = tasks + spam_tasks + sticker_tasks
    for t in all_tasks: t.cancel()
    
    tasks.clear()
    spam_tasks.clear()
    sticker_tasks.clear()
    
    ui.log_action("SYSTEM", "All operations terminated", "☠️")
    ui.log_stats()
    
    await update.message.reply_text(
        "╔═══════════════════════╗\n"
        "  ☠️  ALL STOPPED  ☠️\n"
        "╠═══════════════════════╣\n"
        f"  Renames: {stats['rename_count']:,}\n"
        f"  Messages: {stats['spam_count']:,}\n"
        f"  Stickers: {stats['sticker_count']:,}\n"
        f"  Errors: {stats['errors']}\n"
        "╚═══════════════════════╝"
    )

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """New: Show live statistics"""
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/stats from user {user_id}", "📊")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    uptime = time.time() - stats["start_time"] if stats["start_time"] else 0
    uptime_str = f"{int(uptime // 60)}m {int(uptime % 60)}s"
    
    status = "🔥 ACTIVE" if running else "💤 IDLE"
    boost_status = "⚡ BOOSTED" if boosting else "🔽 NORMAL"
    
    await update.message.reply_text(
        "╔════════════════════════════╗\n"
        "     📊 LIVE STATISTICS 📊\n"
        "╠════════════════════════════╣\n"
        f"  Status: {status}\n"
        f"  Speed: {boost_status}\n"
        f"  Uptime: {uptime_str}\n"
        "╠════════════════════════════╣\n"
        f"  🔄 Renames:  {stats['rename_count']:,}\n"
        f"  💬 Messages: {stats['spam_count']:,}\n"
        f"  🎨 Stickers: {stats['sticker_count']:,}\n"
        f"  ⚡ Boosts:   {stats['boost_count']}\n"
        f"  ❌ Errors:   {stats['errors']}\n"
        "╠════════════════════════════╣\n"
        f"  Active Tasks:\n"
        f"    • Rename: {len(tasks)}\n"
        f"    • Spam: {len(spam_tasks)}\n"
        f"    • Stickers: {len(sticker_tasks)}\n"
        "╚════════════════════════════╝"
    )

async def clean_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean tracked messages"""
    user_id = update.effective_user.id
    ui.log_action("COMMAND", f"/clean from user {user_id}", "🧹")
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Access Denied - Admin Only")
        return
    
    deleted = 0
    failed = 0
    
    await update.message.reply_text("🧹 Cleaning messages...")
    ui.log_action("CLEAN", f"Starting cleanup of {len(TRACKED_MESSAGES)} messages", "🧹")
    
    for chat_id, msg_id in TRACKED_MESSAGES[:]:
        try:
            await BOTS[0].delete_message(chat_id, msg_id)
            deleted += 1
            TRACKED_MESSAGES.remove((chat_id, msg_id))
        except:
            failed += 1
    
    ui.log_action("CLEAN", f"Deleted {deleted}, Failed {failed}", "✅")
    
    await update.message.reply_text(
        f"╔═══════════════════════╗\n"
        f"   🧹 CLEANUP DONE 🧹\n"
        f"╠═══════════════════════╣\n"
        f"  Deleted: {deleted}\n"
        f"  Failed: {failed}\n"
        f"  Remaining: {len(TRACKED_MESSAGES)}\n"
        f"╚═══════════════════════╝"
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    ui.log_action("ERROR", f"Exception: {context.error}", "❌")
    print(f"Exception while handling an update: {context.error}")

# ================= MAIN =================
def main():
    try:
        # Show startup animation
        ui.show_banner()
        ui.animate_startup()
        
        stats["start_time"] = time.time()
        
        ui.log_action("SYSTEM", "Building application...", "⚙️")
        app = ApplicationBuilder().token(BOT_TOKENS[0]).build()

        # Add error handler
        app.add_error_handler(error_handler)
        
        # Add command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("menu", menu))
        app.add_handler(CommandHandler("nc", nc))
        app.add_handler(CommandHandler("ncloop", ncloop))
        app.add_handler(CommandHandler("boost", boost))
        app.add_handler(CommandHandler(["s1","s2","s3"], spam_cmd))
        app.add_handler(CommandHandler(["st1","st2","st3"], sticker_spam_cmd))
        app.add_handler(CommandHandler("spamoff", spam_off))
        app.add_handler(CommandHandler("stoff", sticker_off))
        app.add_handler(CommandHandler("ncoff", nc_off))
        app.add_handler(CommandHandler("offall", off_all))
        app.add_handler(CommandHandler("stats", show_stats))
        app.add_handler(CommandHandler("clean", clean_messages))

        ui.log_action("SYSTEM", "INFINITY Bot initialized successfully", "✅")
        ui.log_action("SYSTEM", f"Loaded {len(BOT_TOKENS)} bots", "🤖")
        ui.log_action("SYSTEM", "Ready to receive commands", "🚀")
        
        print("\n" + "═" * 60)
        print("🔥 INFINITY BOT RUNNING - Press Ctrl+C to stop")
        print("═" * 60 + "\n")
        
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        ui.log_action("CRITICAL", f"Failed to start: {str(e)}", "💀")
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
