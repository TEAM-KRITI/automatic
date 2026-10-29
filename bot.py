import os
import asyncio
import sqlite3
from datetime import datetime

from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from pyrogram.types import (
    ChatJoinRequest, Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

# ================== CONFIG (env se ya yahin bhar do) ==================
START_IMG = os.getenv("START_IMG", "")                     # start message ki photo ka direct link (optional)
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/telegram")   # support group/channel link
OWNER_URL = os.getenv("OWNER_URL", "https://t.me/telegram")       # tumhara profile link
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
LOGGER_GROUP_ID = int(os.getenv("LOGGER_GROUP_ID", "0"))   # e.g. -1001234567890
OWNER_ID = int(os.getenv("OWNER_ID", "0"))                 # tumhara telegram id
SESSION_STRING = os.getenv("SESSION_STRING", "")           # sirf bulk approve (20000+ pending) ke liye
# =====================================================================

bot = Client("autoapprove_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = (
    Client("autoapprove_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
    if SESSION_STRING else None
)

# ---------------- Database ----------------
db = sqlite3.connect("users.db", check_same_thread=False)
db.execute(
    "CREATE TABLE IF NOT EXISTS users ("
    "user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT, starts INTEGER DEFAULT 0, joined TEXT)"
)
db.commit()


def save_start(u) -> int:
    row = db.execute("SELECT starts FROM users WHERE user_id=?", (u.id,)).fetchone()
    if row:
        db.execute(
            "UPDATE users SET starts=starts+1, first_name=?, username=? WHERE user_id=?",
            (u.first_name, u.username, u.id),
        )
        count = row[0] + 1
    else:
        db.execute(
            "INSERT INTO users VALUES (?,?,?,?,?)",
            (u.id, u.first_name, u.username, 1, datetime.now().isoformat()),
        )
        count = 1
    db.commit()
    return count


# ---------------- Start message text + buttons ----------------
START_TEXT = (
    "✦ **ᴘʀᴇᴍɪᴜᴍ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ʙᴏᴛ** ✦\n\n"
    "❖ ᴘʀᴇᴍɪᴜᴍ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ʙᴏᴛ ꜰᴏʀ ᴛᴇʟᴇɢʀᴀᴍ ♡\n\n"
    "➺ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ꜰᴏʀ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛs ✦"
)

HELP_TEXT = (
    "✦ **ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs** ✦\n\n"
    "1️⃣ ᴍᴀᴊʜᴇ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ ᴍᴇ ᴀᴅᴍɪɴ ʙᴀɴᴀᴏ (ɪɴᴠɪᴛᴇ ᴜsᴇʀs ʀɪɢʜᴛ ᴢᴀʀᴏᴏʀɪ)\n"
    "2️⃣ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ʜᴏ ᴊᴀʏᴇɢɪ\n\n"
    "⚙️ /start - ʙᴏᴛ sᴛᴀʀᴛ ᴋᴀʀᴏ"
)


def start_buttons(client: Client) -> InlineKeyboardMarkup:
    uname = client.me.username
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🔴 ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
            url=f"https://t.me/{uname}?startgroup=true&admin=invite_users",
        )],
        [
            InlineKeyboardButton("🔵 sᴜᴘᴘᴏʀᴛ", url=SUPPORT_URL),
            InlineKeyboardButton("🟣 ᴏᴡɴᴇʀ", url=OWNER_URL),
        ],
        [InlineKeyboardButton("🟡 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", callback_data="help")],
    ])


# ---------------- 1) Auto approve (naye join requests) ----------------
@bot.on_chat_join_request()
async def auto_approve(client: Client, req: ChatJoinRequest):
    try:
        await client.approve_chat_join_request(req.chat.id, req.from_user.id)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await client.approve_chat_join_request(req.chat.id, req.from_user.id)
    except Exception as e:
        print("approve error:", e)


# ---------------- 2) /start: koi reply nahi, sirf logger group me log ----------------
@bot.on_message(filters.command("start") & filters.private)
async def start_logger(client: Client, m: Message):
    u = m.from_user
    count = save_start(u)  # user DB me add + start count badhao
    total = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    text = (
        "🚀 **Bot Started**\n\n"
        f"👤 Name: {u.mention}\n"
        f"🆔 ID: `{u.id}`\n"
        f"🔗 Username: @{u.username if u.username else 'None'}\n"
        f"🔁 Start count: {count}\n"
        f"👥 Total users: {total}\n"
        f"🕒 {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    )
    try:
        await client.send_message(LOGGER_GROUP_ID, text)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await client.send_message(LOGGER_GROUP_ID, text)
    except Exception as e:
        print("logger error:", e)

    # ---- Start message (photo + buttons) ----
    try:
        if START_IMG:
            await m.reply_photo(START_IMG, caption=START_TEXT, reply_markup=start_buttons(client))
        else:
            await m.reply_text(START_TEXT, reply_markup=start_buttons(client), disable_web_page_preview=True)
    except Exception as e:
        print("start msg error:", e)


# ---------------- Help & Commands / Back buttons ----------------
@bot.on_callback_query(filters.regex("^help$"))
async def help_cb(client: Client, q: CallbackQuery):
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="back")]])
    if q.message.photo:
        await q.message.edit_caption(HELP_TEXT, reply_markup=markup)
    else:
        await q.message.edit_text(HELP_TEXT, reply_markup=markup)


@bot.on_callback_query(filters.regex("^back$"))
async def back_cb(client: Client, q: CallbackQuery):
    markup = start_buttons(client)
    if q.message.photo:
        await q.message.edit_caption(START_TEXT, reply_markup=markup)
    else:
        await q.message.edit_text(START_TEXT, reply_markup=markup)


# ---------------- 3) Pending requests ek saath approve (20000+ bhi) ----------------
# Use: /approveall -1001234567890   (sirf OWNER, bot ke private chat me)
@bot.on_message(filters.command("approveall") & filters.private & filters.user(OWNER_ID))
async def approve_all(client: Client, m: Message):
    if not userbot:
        return await m.reply("SESSION_STRING set nahi hai, bulk approve ke liye zaroori hai.")
    if len(m.command) < 2:
        return await m.reply("Use: /approveall <chat_id>")
    chat_id = int(m.command[1])
    note = await m.reply("⏳ Approve ho rahe hain...")
    try:
        # Telegram ka ek hi call saari pending requests approve kar deta hai
        await userbot.approve_all_chat_join_requests(chat_id)
        await note.edit("✅ Saari pending requests approve ho gayi.")
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await userbot.approve_all_chat_join_requests(chat_id)
        await note.edit("✅ Saari pending requests approve ho gayi.")
    except Exception as e:
        # fallback: ek ek karke (max 20000)
        done = 0
        try:
            async for r in userbot.get_chat_join_requests(chat_id, limit=20000):
                try:
                    await userbot.approve_chat_join_request(chat_id, r.user.id)
                    done += 1
                except FloodWait as fw:
                    await asyncio.sleep(fw.value)
                except Exception:
                    pass
            await note.edit(f"✅ {done} requests approve hui.")
        except Exception as e2:
            await note.edit(f"❌ Error: {e} | {e2}")


async def main():
    await bot.start()
    if userbot:
        await userbot.start()
    print("Bot chal raha hai...")
    await idle()
    await bot.stop()
    if userbot:
        await userbot.stop()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
