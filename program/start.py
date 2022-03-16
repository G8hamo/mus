import asyncio

from datetime import datetime
from sys import version_info
from time import time

from config import (
    ALIVE_IMG,
    ALIVE_NAME,
    BOT_NAME,
    ASSISTANT_NAME,
    BOT_USERNAME,
    GROUP_SUPPORT,
    OWNER_NAME,
    UPDATES_CHANNEL,
)
from program import __version__
from driver.veez import user
from driver.filters import command, other_filters
from driver.database.dbchat import add_served_chat, is_served_chat
from driver.database.dbpunish import is_gbanned_user
from pyrogram import Client, filters, __version__ as pyrover
from pyrogram.errors import FloodWait, MessageNotModified
from pytgcalls import (__version__ as pytover)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest

__major__ = 0
__minor__ = 2
__micro__ = 1

__python_version__ = f"{version_info[0]}.{version_info[1]}.{version_info[2]}"


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60 * 60 * 24),
    ("hour", 60 * 60),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}".format(amount, unit, "" if amount == 1 else "s"))
    return ", ".join(parts)


@Client.on_message(
    command(["start", f"start@{BOT_USERNAME}"]) & filters.private & ~filters.edited
)
async def start_(client: Client, message: Message):
    await message.reply_text(
        f"""✨ **مرحبا عزيزي ⇦ {message.from_user.mention()} !**\n
💭 [{BOT_NAME}](https://t.me/{BOT_USERNAME}) **يتيح لك تشغيل الموسيقى والفيديو في مجموعات من خلال المكالمات الجديدة في Telegram!**
💡 **اضفني مشرف مع صلاحيه اضافه مستخدمين واكتب انضم و اكتشف جميع أوامر البوت وكيفية عملها من خلال النقر على زر »📚الأوامر🎮 او اضغط زر الاوامر المعربه او اكتب الاوامر**
🔖 **لمعرفة كيفية استخدام هذا البوت ، يرجى النقر فوق » زر 🔮طريقة الاستخدام🔮! يوزر الحساب المساعد  @{ASSISTANT_NAME} **
⚡𝐏𝐑𝐎𝐆𝐑𝐀𝐌𝐌𝐄𝐑 **[{ALIVE_NAME}](https://t.me/{OWNER_NAME}) **
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "☑️اضغط لاضافتي لمجموعتك☑️",
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                    )
                ],
                [InlineKeyboardButton("❓طريقه الاستخدام", callback_data="cbhowtouse")],
                [InlineKeyboardButton("🌀الاوامــر الكامله المعربــه🌀", callback_data="cbbasic")],
                [
                    InlineKeyboardButton("📚 الاوامــر", callback_data="cbcmds"),
                    InlineKeyboardButton("❤️ المساعـــد", url=f"https://t.me/{ASSISTANT_NAME}"),
                ],
                [
                    InlineKeyboardButton(
                        "👥جــروب الدعــم", url=f"https://t.me/{GROUP_SUPPORT}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "​​​​• 𝗦َ𝗢ٰ𝗨ِِ𝖱ٰ𝗖ٌ𝗘 𝗧ِٰٰ𝗛𝗢ِٰ𝖱 🕷️🔥", url=f"https://t.me/GB_THOR"
                    )
                ],
            ]
        ),
        disable_web_page_preview=True,
    )


@Client.on_chat_join_request()
async def approve_join_chat(c: Client, m: ChatJoinRequest):
    if not m.from_user:
        return
    try:
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)
    except FloodWait as e:
        await asyncio.sleep(e.x + 2)
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)


@Client.on_message(filters.new_chat_members)
async def new_chat(c: Client, m: Message):
    chat_id = m.chat.id
    if await is_served_chat(chat_id):
        pass
    else:
        await add_served_chat(chat_id)
    ass_uname = (await user.get_me()).username
    bot_id = (await c.get_me()).id
    for member in m.new_chat_members:
        if member.id == bot_id:
            return await m.reply(
"🤖╖   أهلآ بك عزيزي أنا بوت حمايه جروبات !\n\n"
                "⚡️╢• قم بترقيتي الي » مشرف + اكتب تفعيل.\n\n"
                "📣╢• تأكد » من اعطائي الصلاحيات المطلوبه  "
"📣╢• تأكد » كتابه انضم حتي ينضم الحساب المساعد للاغاني !\n\n",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("​​​​• 𝗦َ𝗢ٰ𝗨ِِ𝖱ٰ𝗖ٌ𝗘 𝗧ِٰٰ𝗛𝗢ِٰ𝖱 🕷️🔥", url=f"https://t.me/GB_THOR"),
                        ],
                        [
                            InlineKeyboardButton("🌀الاوامــر الكامله المعربــه🌀", callback_data="cbbasic")],
                        [
                            InlineKeyboardButton("👤المساعــد", url=f"https://t.me/{ass_uname}")
                        ]
                    ]
                )
            )


chat_watcher_group = 5

@Client.on_message(group=chat_watcher_group)
async def chat_watcher_func(_, message: Message):
    try:
        userid = message.from_user.id
    except Exception:
        return
    suspect = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    if await is_gbanned_user(userid):
        try:
            await message.chat.ban_member(userid)
        except Exception:
            return
        await message.reply_text(
            f"👮🏼 (> {عفوا} <)\n\n**الحظر العام** حساب غير مرغوب فيه تم حظر هذا الحساب بواسطه المبرمج!\n\n🚫 **السبب:**يرسل رسايل غير مرغوب فيها للأناث"
        )
