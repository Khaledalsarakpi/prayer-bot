from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackContext
from utils.json_loader import load_prayer_times
from utils.time_calc import get_today_data, get_ramadan_day


def format_times_message(day_data):
    if not day_data:
        return "⚠️ تعذر جلب المواقيت"

    ramadan_day = get_ramadan_day()

    response = f"""🌙 *مواقيت الصلاة - مدينة إدلب*
═══════════════════════════
📍 *إدلب - سوريا*
📅 *19 فبراير - 19 مارس 2026*
📆 *شهر رمضان 1447*

┌─────────────────────────────┐
│  🕌 مواقيت اليوم - رمضـان {ramadan_day}  │
└─────────────────────────────┘

🌙  الفجر:    {day_data.get('الفجر', '-')}
☀️  الشروق:   {day_data.get('الشروق', '-')}
🕐  الظهر:    {day_data.get('الظهر', '-')}
🌅  العصر:    {day_data.get('العصر', '-')}
🌇  المغرب:   {day_data.get('المغرب', '-')}
🌃  العشاء:   {day_data.get('العشاء', '-')}

═══════════════════════════"""

    return response


async def times_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prayer_times_data = load_prayer_times()
    day_data = get_today_data(prayer_times_data)
    response = format_times_message(day_data)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 تصفح الأيام", callback_data="calendar")],
        [InlineKeyboardButton("🔔 تفعيل التذكير", callback_data="reminder")]
    ])

    if update.callback_query:
        await update.callback_query.edit_message_text(response, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)


def format_day_message(day, day_num):
    response = f"""📅 *رمضان {day_num}*
{day.get('التاريخ_ميلادي', '')}

┌─────────────────────────────┐
│         🕌 المواقيت          │
└─────────────────────────────┘

🌙  الفجر:    {day.get('الفجر', '-')}
☀️  الشروق:   {day.get('الشروق', '-')}
🕐  الظهر:    {day.get('الظهر', '-')}
🌅  العصر:    {day.get('العصر', '-')}
🌇  المغرب:   {day.get('المغرب', '-')}
🌃  العشاء:   {day.get('العشاء', '-')}"""

    return response


async def calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []
    for i in range(1, 30):
        row.append(InlineKeyboardButton(str(i), callback_data=f"day_{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])

    await update.message.reply_text("📅 *اختر يوم Ramadan:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def show_day(update: Update, context: ContextTypes.DEFAULT_TYPE, day_num):
    prayer_times_data = load_prayer_times()
    for day in prayer_times_data:
        if day.get("اليوم_رمضان") == day_num:
            response = format_day_message(day, day_num)

            prev_day = day_num - 1 if day_num > 1 else 29
            next_day = day_num + 1 if day_num < 29 else 1

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("◀", callback_data=f"day_{prev_day}"),
                    InlineKeyboardButton(f"{day_num}/29", callback_data="calendar"),
                    InlineKeyboardButton("▶", callback_data=f"day_{next_day}")
                ],
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ])

            if update.callback_query:
                await update.callback_query.edit_message_text(response, parse_mode="Markdown", reply_markup=keyboard)
            else:
                await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)
            return
