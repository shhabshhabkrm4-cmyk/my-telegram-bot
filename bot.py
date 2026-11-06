# -*- coding: utf-8 -*-
# سورس 𝑨𝑳𝑲𝑯𝑨𝑴𝑶𝑹𝑮𝒀 - كل الانواع
import telebot
from telebot import types
import sqlite3, random, requests, datetime, re

BOT_TOKEN = "9031871909:AAH24XNA3GyJCJFsoT0vpani-rIV2mFeBP0"
BOT_CREDITS = "𝑨𝑳𝑲𝑯𝑨𝑴𝑶𝑹𝑮𝒀 𝑨𝑳 𝒀𝑶𝑼𝑻𝑼𝑩𝑬𝑹≈{𝑺}"
DEVELOPER_ID = 7138192280

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
DB = 'alkhamorgy.db'

# ========== قاعدة البيانات ==========
def db():
    con = sqlite3.connect(DB)
    c = con.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS groups (group_id INTEGER PRIMARY KEY, welcome TEXT DEFAULT 'نورت يا {name} 🔥')''')
    c.execute('''CREATE TABLE IF NOT EXISTS warns (group_id INTEGER, user_id INTEGER, count INTEGER DEFAULT 0, PRIMARY KEY(group_id, user_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS locks (group_id INTEGER, feature TEXT, PRIMARY KEY(group_id, feature))''')
    c.execute('''CREATE TABLE IF NOT EXISTS replies (group_id INTEGER, keyword TEXT, reply TEXT, PRIMARY KEY(group_id, keyword))''')
    con.commit(); con.close()

db()

def is_admin(chat_id, user_id):
    try:
        m = bot.get_chat_member(chat_id, user_id)
        return m.status in ['administrator','creator'] or user_id == DEVELOPER_ID
    except: return False

def get_target(msg):
    if msg.reply_to_message:
        return msg.reply_to_message.from_user
    return None

# ========== القايمة الرئيسية ==========
def main_menu():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("🛡️ إدارة", callback_data="menu_admin"),
        types.InlineKeyboardButton("🔒 حماية", callback_data="menu_protect"),
        types.InlineKeyboardButton("🎮 ترفيه", callback_data="menu_fun"),
        types.InlineKeyboardButton("🌐 خدمات", callback_data="menu_services"),
        types.InlineKeyboardButton("🆔 ايدي", callback_data="my_id"),
        types.InlineKeyboardButton("❌ قفل", callback_data="close"),
    )
    return m

@bot.message_handler(commands=['start'])
def start(msg):
    txt = f"""<b>أهلا بيك في سـ ـوࢪس 𝑨𝑳𝑲𝑯𝑨𝑴𝑶𝑹𝑮𝒀 🔥</b>

بوت متكامل: إدارة + حماية + ترفيه + خدمات + أذان

دوس على القايمة تحت 👇
{BOT_CREDITS}"""
    if msg.chat.type == 'private':
        bot.send_message(msg.chat.id, txt, reply_markup=main_menu())
    else:
        bot.send_message(msg.chat.id, txt, reply_markup=main_menu())

@bot.message_handler(commands=['id', 'ايدي'])
def my_id(msg):
    u = msg.from_user
    target = get_target(msg) or u
    txt = f"""🆔 <b>بياناتك</b>
• الاسم: {target.first_name}
• الايدي: <code>{target.id}</code>
• اليوزر: @{target.username if target.username else 'مفيش'}
• الجروب: {msg.chat.title if msg.chat.title else 'خاص'}

{BOT_CREDITS}"""
    bot.reply_to(msg, txt)

# ========== إدارة ==========
@bot.message_handler(commands=['ban','حظر'])
def ban(msg):
    if not is_admin(msg.chat.id, msg.from_user.id): return bot.reply_to(msg, "للمشرفين بس ❌")
    t = get_target(msg)
    if not t: return bot.reply_to(msg, "رد على رسالة الشخص")
    try:
        bot.ban_chat_member(msg.chat.id, t.id)
        bot.reply_to(msg, f"✅ تم حظر {t.first_name}\n{BOT_CREDITS}")
    except Exception as e: bot.reply_to(msg, f"❌ فشل: {e}")

@bot.message_handler(commands=['unban','الغاء_حظر'])
def unban(msg):
    if not is_admin(msg.chat.id, msg.from_user.id): return
    t = get_target(msg)
    if t:
        bot.unban_chat_member(msg.chat.id, t.id)
        bot.reply_to(msg, f"✅ تم فك حظر {t.first_name}\n{BOT_CREDITS}")

@bot.message_handler(commands=['kick','طرد'])
def kick(msg):
    if not is_admin(msg.chat.id, msg.from_user.id): return
    t = get_target(msg)
    if t:
        bot.ban_chat_member(msg.chat.id, t.id); bot.unban_chat_member(msg.chat.id, t.id)
        bot.reply_to(msg, f"👢 تم طرد {t.first_name}\n{BOT_CREDITS}")

@bot.message_handler(commands=['mute','كتم'])
def mute(msg):
    if not is_admin(msg.chat.id, msg.from_user.id): return
    t = get_target(msg)
    if t:
        bot.restrict_chat_member(msg.chat.id, t.id, until_date=datetime.datetime.now()+datetime.timedelta(minutes=30))
        bot.reply_to(msg, f"🔇 تم كتم {t.first_name} 30 دقيقة\n{BOT_CREDITS}")

@bot.message_handler(commands=['unmute','الغاء_كتم'])
def unmute(msg):
    if not is_admin(msg.chat.id, msg.from_user.id): return
    t = get_target(msg)
    if t:
        bot.restrict_chat_member(msg.chat.id, t.id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
        bot.reply_to(msg, f"🔊 تم فك كتم {t.first_name}\n{BOT_CREDITS}")

@bot.message_handler(commands=['warn','تحذير'])
def warn(msg):
    if not is_admin(msg.chat.id, msg.from_user.id): return
    t = get_target(msg)
    if not t: return
    con = sqlite3.connect(DB); c = con.cursor()
    c.execute("INSERT OR IGNORE INTO warns VALUES (?,?,0)", (msg.chat.id, t.id))
    c.execute("UPDATE warns SET count=count+1 WHERE group_id=? AND user_id=?", (msg.chat.id, t.id))
    c.execute("SELECT count FROM warns WHERE group_id=? AND user_id=?", (msg.chat.id, t.id))
    cnt = c.fetchone()[0]; con.commit(); con.close()
    if cnt >= 3:
        bot.restrict_chat_member(msg.chat.id, t.id, until_date=datetime.datetime.now()+datetime.timedelta(minutes=30))
        bot.reply_to(msg, f"🚫 {t.first_name} خد 3 تحذيرات واتكتم\n{BOT_CREDITS}")
    else:
        bot.reply_to(msg, f"⚠️ تحذير {cnt}/3 لـ {t.first_name}\n{BOT_CREDITS}")

@bot.message_handler(commands=['pin','تثبيت'])
def pin(msg):
    if msg.reply_to_message and is_admin(msg.chat.id, msg.from_user.id):
        bot.pin_chat_message(msg.chat.id, msg.reply_to_message.message_id)
        bot.reply_to(msg, f"📌 تم التثبيت\n{BOT_CREDITS}")

@bot.message_handler(commands=['del','حذف'])
def dele(msg):
    if msg.reply_to_message and is_admin(msg.chat.id, msg.from_user.id):
        bot.delete_message(msg.chat.id, msg.reply_to_message.message_id)
        bot.delete_message(msg.chat.id, msg.message_id)

# ========== حماية ==========
@bot.message_handler(commands=['lock','قفل'])
def lock(msg):
    if not is_admin(msg.chat.id, msg.from_user.id): return
    parts = msg.text.split()
    if len(parts) < 2: return bot.reply_to(msg, "مثال: /lock روابط - صور - فيديو - ملصقات")
    feat = parts[1]
    con = sqlite3.connect(DB); c = con.cursor()
    c.execute("INSERT OR IGNORE INTO locks VALUES (?,?)", (msg.chat.id, feat)); con.commit(); con.close()
    bot.reply_to(msg, f"🔒 تم قفل {feat}\n{BOT_CREDITS}")

@bot.message_handler(commands=['unlock','فتح'])
def unlock(msg):
    if not is_admin(msg.chat.id, msg.from_user.id): return
    feat = msg.text.split()[1] if len(msg.text.split())>1 else ""
    con = sqlite3.connect(DB); c = con.cursor()
    c.execute("DELETE FROM locks WHERE group_id=? AND feature=?", (msg.chat.id, feat)); con.commit(); con.close()
    bot.reply_to(msg, f"🔓 تم فتح {feat}\n{BOT_CREDITS}")

@bot.message_handler(content_types=['photo','video','sticker','document'])
def protect_media(msg):
    if msg.chat.type == 'private': return
    con = sqlite3.connect(DB); c = con.cursor()
    c.execute("SELECT feature FROM locks WHERE group_id=?", (msg.chat.id,))
    locked = [r[0] for r in c.fetchall()]; con.close()
    mp = {'photo':'صور','video':'فيديو','sticker':'ملصقات','document':'ملفات'}
    if mp.get(msg.content_type) in locked or 'الكل' in locked:
        try: bot.delete_message(msg.chat.id, msg.message_id)
        except: pass

# ========== ترفيه ==========
JOKES = ["مرة واحد غبي راح يجيب لبن، رجع جايب عيش 😂","مرة واحد نام على السرير، السرير اتكسر من الضحك 🤣","بتعرف ليه الكمبيوتر بيضحك؟ عشان عنده كيبورد 😂","مرة واحد دخل امتحان، الامتحان خرج من الخوف 🤣"]
@bot.message_handler(commands=['joke','نكتة'])
def joke(msg): bot.reply_to(msg, f"{random.choice(JOKES)}\n\n{BOT_CREDITS}")

@bot.message_handler(commands=['fortune','حظك'])
def fortune(msg):
    p = random.randint(1,100)
    bot.reply_to(msg, f"🔮 حظك النهارده: {p}%\n{'انت محظوظ جدا 🔥' if p>70 else 'خلي بالك النهارده 👀'}\n\n{BOT_CREDITS}")

@bot.message_handler(commands=['dice','زهر'])
def dice(msg): bot.send_dice(msg.chat.id)

@bot.message_handler(commands=['zodiac','برج'])
def zodiac(msg):
    bot.reply_to(msg, "ابعت برجك كده: /برج الحمل\n\nالحمل - الثور - الجوزاء - السرطان - الاسد - العذراء - الميزان - العقرب - القوس - الجدي - الدلو - الحوت")

# ========== خدمات ==========
@bot.message_handler(commands=['prayer','صلاة','اذان'])
def prayer(msg):
    city = msg.text.split()[1] if len(msg.text.split())>1 else "Cairo"
    try:
        r = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=Egypt&method=5", timeout=10).json()
        t = r['data']['timings']
        bot.reply_to(msg, f"🕌 مواقيت الصلاة في {city}:\nالفجر: {t['Fajr']}\nالشروق: {t['Sunrise']}\nالظهر: {t['Dhuhr']}\nالعصر: {t['Asr']}\nالمغرب: {t['Maghrib']}\nالعشاء: {t['Isha']}\n\n{BOT_CREDITS}")
    except: bot.reply_to(msg, "❌ مش لاقي المدينة دي")

@bot.message_handler(commands=['weather','طقس'])
def weather(msg):
    city = msg.text.split()[1] if len(msg.text.split())>1 else "Cairo"
    try:
        r = requests.get(f"https://wttr.in/{city}?format=3", timeout=10).text
        bot.reply_to(msg, f"🌤 {r}\n\n{BOT_CREDITS}")
    except: bot.reply_to(msg, "❌ حاول تاني")

@bot.message_handler(commands=['time','وقت'])
def time_cmd(msg):
    now = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    bot.reply_to(msg, f"⏰ الوقت: {now}\n\n{BOT_CREDITS}")

@bot.message_handler(commands=['help','مساعدة','اوامر'])
def help_cmd(msg):
    bot.reply_to(msg, f"""📋 <b>اوامر سـ ـوࢪس 𝑨𝑳𝑲𝑯𝑨𝑴𝑶𝑹𝑮𝒀</b>

/start - القايمة
/id - ايديك
/ban - حظر (رد)
/kick - طرد
/mute - كتم
/unmute - فك كتم
/warn - تحذير
/pin - تثبيت
/del - حذف
/lock روابط - قفل
/unlock روابط - فتح
/joke - نكتة
/fortune - حظك
/dice - زهر
/prayer القاهرة - مواقيت الصلاة
/weather القاهرة - طقس
/time - الوقت

{BOT_CREDITS}""")

# ========== ردود تلقائية ==========
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['هلا','السلام عليكم','سلام'])
def auto_reply(msg):
    bot.reply_to(msg, f"هلا بيك يا {msg.from_user.first_name} نورت 🔥\n{BOT_CREDITS}")

# ========== ازرار ==========
@bot.callback_query_handler(func=lambda c: True)
def buttons(call):
    if call.data == "close":
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == "my_id":
        bot.answer_callback_query(call.id, f"ايديك: {call.from_user.id}", show_alert=True)
    elif call.data == "menu_admin":
        bot.edit_message_text("🛡️ <b>الإدارة:</b>\n/ban /kick /mute /warn /pin /del\n\n"+BOT_CREDITS, call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    elif call.data == "menu_protect":
        bot.edit_message_text("🔒 <b>الحماية:</b>\n/lock روابط - /lock صور - /lock فيديو\n/unlock روابط\n\n"+BOT_CREDITS, call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    elif call.data == "menu_fun":
        bot.edit_message_text("🎮 <b>ترفيه:</b>\n/joke /fortune /dice /zodiac\n\n"+BOT_CREDITS, call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    elif call.data == "menu_services":
        bot.edit_message_text("🌐 <b>خدمات:</b>\n/prayer القاهرة - /weather القاهرة - /time - /id\n\n"+BOT_CREDITS, call.message.chat.id, call.message.message_id, reply_markup=main_menu())

print("✅ سورس ALKHAMORGY شغال...")
bot.infinity_polling()
