from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.json_loader import load_prayer_times
from utils.time_calc import get_next_prayer


def format_next_prayer():
    prayer_times_data = load_prayer_times()
    info = get_next_prayer(prayer_times_data)
    if not info or info[0] is None:
        return "⚠️ تعذر جلب البيانات"

    prayer, time, remaining, date = info
    ramadan_day = None
    for day in prayer_times_data:
        if day.get("التاريخ_ميلادي") == date:
            ramadan_day = day.get("اليوم_رمضان")
            break

    date_text = f"رمضان {ramadan_day}" if ramadan_day else date

    response = f"""⏰ *الصلاة القادمة*
═══════════════════════════

📅 {date_text} | {date}

🕌 *{prayer}*
┌─────────────────────────────┐
│      🕐 {time}            │
└─────────────────────────────┘

⏱️ *الوقت المتبقي:*

┌─────────────────────────────┐
│      ⏰ {remaining}       │
└─────────────────────────────┘

🔄 جارٍ التحديث تلقائياً...

اضغط '⏰ الصلاة القادمة' للتحديث"""

    return response


async def next_prayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = format_next_prayer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 تحديث", callback_data="refresh_next")]
    ])

    await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)
