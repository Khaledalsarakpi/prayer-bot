from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackContext
from utils.json_loader import load_prayer_times, load_cities, get_city_times
from utils.time_calc import get_today_data, get_ramadan_day


CITY_DISPLAY_NAMES = {
    "ادلب": "إدلب",
    "حلب": "حلب",
    "حمص": "حمص",
    "حماة": "حماة",
    "دمشق": "دمشق",
    "اللاذقية": "اللاذقية"
}

CITY_COUNTRIES = {
    "ادلب": "سوريا",
    "حلب": "سوريا",
    "حمص": "سوريا",
    "حماة": "سوريا",
    "دمشق": "سوريا",
    "اللاذقية": "سوريا"
}


def format_times_message(day_data, city_key):
    if not day_data:
        return "⚠️ تعذر جلب المواقيت"

    ramadan_day = get_ramadan_day()
    city_name = CITY_DISPLAY_NAMES.get(city_key, city_key)
    country = CITY_COUNTRIES.get(city_key, "")

    response = f"""🌙 *مواقيت الصلاة - مدينة {city_name}*
═══════════════════════════
📍 *{city_name} - {country}*
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


async def select_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cities = load_cities()
    city_keys = list(cities.keys())
    
    keyboard = []
    row = []
    for i, city_key in enumerate(city_keys):
        display_name = CITY_DISPLAY_NAMES.get(city_key, city_key)
        row.append(InlineKeyboardButton(display_name, callback_data=f"city_{city_key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])
    
    await update.message.reply_text(
        "🏙️ *اختر المدينة:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def times_today(update: Update, context: ContextTypes.DEFAULT_TYPE, city_key=None):
    if city_key is None:
        await select_city(update, context)
        return
    
    city_times = get_city_times(city_key)
    if not city_times:
        await update.message.reply_text("⚠️ تعذر جلب المواقيت لهذه المدينة")
        return
    
    day_data = get_today_data(city_times)
    response = format_times_message(day_data, city_key)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏙️ تغيير المدينة", callback_data="select_city")],
        [InlineKeyboardButton("📅 تصفح الأيام", callback_data="calendar")],
        [InlineKeyboardButton("🔔 تفعيل التذكير", callback_data="reminder")]
    ])

    if update.callback_query:
        await update.callback_query.edit_message_text(response, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await update.message.reply_text(response, parse_mode="Markdown", reply_markup=keyboard)


async def handle_city_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, city_key):
    city_times = get_city_times(city_key)
    if not city_times:
        await update.callback_query.answer("⚠️ تعذر جلب المواقيت", show_alert=True)
        return
    
    day_data = get_today_data(city_times)
    response = format_times_message(day_data, city_key)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏙️ تغيير المدينة", callback_data="select_city")],
        [InlineKeyboardButton("📅 تصفح الأيام", callback_data="calendar")],
        [InlineKeyboardButton("🔔 تفعيل التذكير", callback_data="reminder")]
    ])

    await update.callback_query.edit_message_text(response, parse_mode="Markdown", reply_markup=keyboard)


async def show_city_selector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cities = load_cities()
    city_keys = list(cities.keys())
    
    keyboard = []
    row = []
    for i, city_key in enumerate(city_keys):
        display_name = CITY_DISPLAY_NAMES.get(city_key, city_key)
        row.append(InlineKeyboardButton(display_name, callback_data=f"city_{city_key}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])
    
    await update.callback_query.edit_message_text(
        "🏙️ *اختر المدينة:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def format_day_message(day, day_num, city_key):
    city_name = CITY_DISPLAY_NAMES.get(city_key, city_key)
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
🌃  العشاء:   {day.get('العشاء', '-')}

📍 {city_name}"""

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


async def show_day(update: Update, context: ContextTypes.DEFAULT_TYPE, day_num, city_key="ادلب"):
    city_times = get_city_times(city_key)
    if not city_times:
        city_times = load_prayer_times()
    
    for day in city_times:
        if day.get("اليوم") == day_num or day.get("اليوم_رمضان") == day_num:
            response = format_day_message(day, day_num, city_key)

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
