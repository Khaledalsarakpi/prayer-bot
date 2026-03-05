from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes


async def reminder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("5 د", callback_data="r_5"), InlineKeyboardButton("10 د", callback_data="r_10")],
        [InlineKeyboardButton("15 د", callback_data="r_15"), InlineKeyboardButton("30 د", callback_data="r_30")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="r_cancel")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
    ])

    text = "🔔 *اختر وقت التذكير قبل الأذان:*"

    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def handle_reminder_callback(query):
    minutes = query.data.split("_")[1]
    if minutes == "cancel":
        text = "❌ *تم إلغاء التذكير*"
    else:
        text = f"✅ *تم تفعيل التذكير قبل الأذان بـ {minutes} دقيقة*"
    await query.edit_message_text(text, parse_mode="Markdown")
