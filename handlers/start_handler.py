from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes


def get_main_menu():
    keyboard = [
        [KeyboardButton("🕐 مواقيت اليوم 🕐"), KeyboardButton("⏰ الصلاة القادمة ⏰")],
        [KeyboardButton("📅 التقويم 📅"), KeyboardButton("🔔 التذكير 🔔")],
        [KeyboardButton("🕌 خدمات إسلامية 🕌")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def get_services_menu():
    keyboard = [
        [KeyboardButton("📖 أذكار الصباح"), KeyboardButton("📖 أذكار المساء")],
        [KeyboardButton("🤲 أدعية"), KeyboardButton("📚 أحاديث")],
        [KeyboardButton("🏠 القائمة الرئيسية")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from utils.localization import welcome_text
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())


async def handle_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.message.reply_text("🕌 *اختر خدمة:*", parse_mode="Markdown", reply_markup=get_services_menu())
    else:
        await update.message.reply_text("🕌 *اختر خدمة:*", parse_mode="Markdown", reply_markup=get_services_menu())


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from utils.localization import welcome_text
    if update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())
    else:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())
