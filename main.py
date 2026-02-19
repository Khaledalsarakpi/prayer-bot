import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

DB_FILE = "/root/prayer_bot/data/users.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, city TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, prayer_name TEXT, date TEXT)")
    conn.commit()
    conn.close()


def reminder_sent_today(user_id, prayer_name, date):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute("SELECT id FROM reminders WHERE user_id = ? AND prayer_name = ? AND date = ?", 
                         (user_id, prayer_name, date))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def mark_reminder_sent(user_id, prayer_name, date):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO reminders (user_id, prayer_name, date) VALUES (?, ?, ?)", 
                 (user_id, prayer_name, date))
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute("SELECT name, city FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def set_user(user_id, name, city):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT OR REPLACE INTO users (user_id, name, city) VALUES (?, ?, ?)", (user_id, name, city))
    conn.commit()
    conn.close()


def get_remaining(prayer_time):
    now = datetime.now()
    
    time_clean = prayer_time.replace(" ص", "").replace(" م", "").replace("ص", "").replace("م", "").strip()
    
    if not time_clean:
        return ""
    
    try:
        hour, minute = map(int, time_clean.split(":"))
        
        if "م" in prayer_time and hour < 12:
            hour += 12
        elif "ص" in prayer_time and hour == 12:
            hour = 0
        
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if target <= now:
            return ""
        
        delta = target - now
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{hours}س {minutes}د"
    except:
        return ""


def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["مواقيت اليوم"],
        ["العشاء", "المغرب", "العصر", "ظهر", "الفجر"],
        ["⏰ الصلاة القادمة", "📅 التقويم"],
        ["🔄 تغيير المدينة", "📖 المصحف"],
    ], resize_keyboard=True)


def quran_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text="📖 قراءة المصحف",
            web_app=WebAppInfo(url="https://tanzil.net/")
        )]
    ])


def cities_keyboard():
    return ReplyKeyboardMarkup([
        ["دمشق", "حلب", "حمص"],
        ["حماة", "اللاذقية", "طرطوس"],
        ["ادلب", "الغوطة الشرقية", "القنيطرة"],
        ["درعا", "السويداء", "الرقة"],
        ["دير الزور", "الحسكة"],
    ], resize_keyboard=True)


def calendar_keyboard():
    keyboard = []
    row = []
    for i in range(1, 30):
        row.append(str(i))
        if len(row) == 7:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def load_city_times(city):
    import json
    with open("/root/prayer_bot/data/cities.json", "r", encoding="utf-8") as f:
        cities_data = json.load(f)
    if city in cities_data:
        return cities_data[city]
    return cities_data.get("ادلب", [])


def get_ramadan_day(city):
    today = datetime.now().date()
    ramadan_start = datetime(2026, 2, 19).date()
    
    day = (today - ramadan_start).days + 1
    if day < 1:
        day = 1
    return day


def get_fasting_hours(fajr_time, maghrib_time):
    try:
        fajr_clean = fajr_time.replace(" ص", "").replace(" م", "").replace("ص", "").replace("م", "").strip()
        maghrib_clean = maghrib_time.replace(" ص", "").replace(" م", "").replace("ص", "").replace("م", "").strip()
        
        fajr_hour, fajr_min = map(int, fajr_clean.split(":"))
        if "ص" in fajr_time or "ص" not in maghrib_time:
            pass
        elif "م" in fajr_time and fajr_hour < 12:
            fajr_hour += 12
            
        maghrib_hour, maghrib_min = map(int, maghrib_clean.split(":"))
        if "م" in maghrib_time and maghrib_hour < 12:
            maghrib_hour += 12
            
        total_minutes = (maghrib_hour * 60 + maghrib_min) - (fajr_hour * 60 + fajr_min)
        if total_minutes < 0:
            total_minutes += 24 * 60
            
        hours = total_minutes // 60
        mins = total_minutes % 60
        
        return f"{hours}س {mins}د"
    except:
        return ""


def format_times(city, day_num=None):
    times = load_city_times(city)
    if not day_num:
        day_num = get_ramadan_day(city)
    
    day_index = day_num - 1
    if day_index >= len(times):
        day_index = len(times) - 1
    day = times[day_index]
    
    fajr = day.get("الفجر", "-")
    zuhr = day.get("الظهر", "-")
    asr = day.get("العصر", "-")
    maghrib = day.get("المغرب", "-")
    isha = day.get("العشاء", "-")
    gregorian_date = day.get("التاريخ_ميلادي", "")
    
    fasting_hours = get_fasting_hours(fajr, maghrib)
    
    return f"""🕌 مواقيت الصلاة - {city}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 التاريخ: {gregorian_date} | 🗓️ رمضان {day_num}
⏱️ عدد ساعات الصيام: {fasting_hours}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌙 الفجر    {fajr}  {get_remaining(fajr)}
🕐 الظهر    {zuhr}  {get_remaining(zuhr)}
🌅 العصر    {asr}  {get_remaining(asr)}
🌇 المغرب   {maghrib}  {get_remaining(maghrib)}
🌃 العشاء   {isha}  {get_remaining(isha)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


def format_prayer(city, prayer_name):
    times = load_city_times(city)
    day_num = get_ramadan_day(city)
    day_index = day_num - 1
    if day_index >= len(times):
        day_index = len(times) - 1
    day = times[day_index]
    
    name_map = {"ظهر": "الظهر"}
    actual_name = name_map.get(prayer_name, prayer_name)
    time = day.get(actual_name, "-")
    remaining = get_remaining(time)
    return f"🕌 صلاة {actual_name}\n\n⏰ الوقت: {time}\nمتبقي: {remaining}"


def format_next_prayer(city):
    times = load_city_times(city)
    day_num = get_ramadan_day(city)
    day_index = day_num - 1
    if day_index >= len(times):
        day_index = len(times) - 1
    day = times[day_index]
    now = datetime.now()
    
    prayers = [("الفجر", day.get("الفجر", "-")), ("الظهر", day.get("الظهر", "-")), 
               ("العصر", day.get("العصر", "-")), ("المغرب", day.get("المغرب", "-")), 
               ("العشاء", day.get("العشاء", "-"))]
    
    for name, time in prayers:
        if time == "-":
            continue
        remaining = get_remaining(time)
        if remaining:
            return f"⏰ الصلاة القادمة\n\n🕌 صلاة {name}\n\n⏰ الوقت: {time}\nمتبقي: {remaining}"
    
    return "🌙 غداً فجراً"


async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute("SELECT user_id, city FROM users")
    users = cursor.fetchall()
    conn.close()
    
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    today_date = now.strftime("%Y-%m-%d")
    
    for user_id, city in users:
        city_times = load_city_times(city)
        city_day_num = get_ramadan_day(city)
        city_day_index = city_day_num - 1
        if city_day_index >= len(city_times):
            city_day_index = len(city_times) - 1
        city_day = city_times[city_day_index]
        
        prayers = {
            "العصر": city_day.get("العصر", ""),
            "المغرب": city_day.get("المغرب", ""),
            "العشاء": city_day.get("العشاء", "")
        }
        
        for prayer_name, prayer_time in prayers.items():
            if not prayer_time:
                continue
            time_clean = prayer_time.replace(" ص", "").replace(" م", "").replace("ص", "").replace("م", "")
            if time_clean == current_time:
                if not reminder_sent_today(user_id, prayer_name, today_date):
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"🔔 حان وقت صلاة {prayer_name}!\n\nاللهم صلِّ على محمد وآل محمد 🤲"
                        )
                        mark_reminder_sent(user_id, prayer_name, today_date)
                    except Exception as e:
                        pass


def schedule_reminders(job_queue: JobQueue):
    job_queue.run_repeating(send_reminders, interval=60, first=10)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    user = get_user(user_id)
    
    if not user or not user[1]:
        text = f"""🎇 رمضان كريم يا {name}! 🌙

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌿 بلغك الله هذا الشهر المبارك 
وأعانك على صيامه وقيامه 
وتقبّل منك صالح الأعمال 🤲

اللهم اجعلنا فيه من عتقاء النار 
واغفر لنا ولوالدينا ولكل من نحب

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏙️ من فضلك، اختر مدينتك:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        await update.message.reply_text(text, reply_markup=cities_keyboard())
    else:
        city = user[1]
        text = format_times(city)
        await update.message.reply_text(text, reply_markup=main_menu_keyboard())


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_FILE)
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    await update.message.reply_text(f"📊 إحصائيات البوت\n\n👥 عدد المشتركين: {count}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    user = get_user(user_id)
    city = user[1] if user else None
    
    if text in ["دمشق", "حلب", "حمص", "حماة", "اللاذقية", "طرطوس", "ادلب", "الغوطة الشرقية", "القنيطرة", "درعا", "السويداء", "الرقة", "دير الزور", "الحسكة"]:
        set_user(user_id, name, text)
        await update.message.reply_text(f"✅ أهلاً {name}!\n\nتم اختيار {text}\n\n{format_times(text)}", reply_markup=main_menu_keyboard())
    
    elif text == "مواقيت اليوم" or text == "/start":
        if city:
            await update.message.reply_text(format_times(city), reply_markup=main_menu_keyboard())
        else:
            await start(update, context)
    
    elif text == "🔄 تغيير المدينة":
        await update.message.reply_text(f"{name}، اختر مدينتك:", reply_markup=cities_keyboard())
    
    elif text == "⏰ الصلاة القادمة":
        if city:
            await update.message.reply_text(format_next_prayer(city), reply_markup=main_menu_keyboard())
        else:
            await start(update, context)
    
    elif text == "📅 التقويم":
        if city:
            await update.message.reply_text(f"📅 اختر يوم - {city}:", reply_markup=calendar_keyboard())
        else:
            await start(update, context)
    
    elif text in ["الفجر", "ظهر", "العصر", "المغرب", "العشاء"]:
        if city:
            await update.message.reply_text(format_prayer(city, text), reply_markup=main_menu_keyboard())
        else:
            await start(update, context)
    
    elif text == "📖 المصحف":
        await update.message.reply_text(
            "📖 اختر قراءة المصحف:",
            reply_markup=quran_keyboard()
        )
    
    elif text.isdigit() and 1 <= int(text) <= 29:
        if city:
            await update.message.reply_text(format_times(city, int(text)), reply_markup=main_menu_keyboard())
        else:
            await start(update, context)
    
    else:
        if city:
            await update.message.reply_text(format_times(city), reply_markup=main_menu_keyboard())
        else:
            await start(update, context)


def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    
    job_queue = app.job_queue
    schedule_reminders(job_queue)
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("Bot Running...")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
