import re
import openai
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Сабақ кестесі (мысал)
SCHEDULE_INFO = (
    "📅 Сабақ кестесі:\n"
    "Понедельник:\n"
    "  09:00 - 10:30: Математика\n"
    "  10:45 - 12:15: Физика\n"
    "  13:00 - 14:30: Қазақ тілі\n\n"
    "Вторник:\n"
    "  09:00 - 10:30: Информатика\n"
    "  10:45 - 12:15: Биология\n"
    "  13:00 - 14:30: Химия\n\n"
    "Соңғы жаңартулар үшін хабарласыңыз."
)

# Байланыс деректері
CONTACT_INFO = (
    "📞 Байланыс:\n"
    "Сайт: https://urbancollege.edu.kz\n"
    "Телефон: +7 708 425 5412\n"
    "Мекенжай: Астана қаласы, Дәулеткерей көшесі, 1"
)

# Жаңалықтар (мысал)
NEWS_INFO = (
    "📰 Соңғы жаңалықтар:\n"
    "1. 25 мамырда университетте ашық есік күні өтеді.\n"
    "2. IT факультетінде жаңа курс басталды.\n"
    "3. Студенттерге арналған спорттық жарыстар жақында басталады."
)

# Мамандықтар (мысал)
MAJORS_INFO = (
    "🎓 Мамандықтар тізімі:\n"
    "- 06130100 Программное обеспечение (по видам)\n"
    "- 06120100 Вычислительная техника и информационные сети (по видам)\n"
    "- 06120200 Системы информационной безопасности\n"
    "- 07321100 Монтаж и эксплуатация инженерных систем объектов жилищно-коммунального хозяйства\n"
    "- 07130200 Электроснабжение (по отраслям)\n"
    "- 10130100 Гостиничный бизнес\n"
    "- 07320400 Управление недвижимостью"
)

# 🔘 Негізгі мәзір
async def show_main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("📅 Сабақ кестесі", callback_data='schedule')],
        [InlineKeyboardButton("🧠 Сұрақ қою (AI)", callback_data='ask_ai')],
        [InlineKeyboardButton("📰 Жаңалықтар", callback_data='news')],
        [InlineKeyboardButton("🎓 Мамандықтар", callback_data='majors')],
        [InlineKeyboardButton("📞 Байланыс", callback_data='contact')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Негізгі мәзір:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Негізгі мәзір:", reply_markup=reply_markup)

# 🔘 /start немесе /menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

# Батырма өңдеуші
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "schedule":
        await query.edit_message_text(
            SCHEDULE_INFO,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Артқа", callback_data='main_menu')]
            ])
        )
    elif query.data == "ask_ai":
        context.user_data["mode"] = "ask_ai"
        await query.edit_message_text(
            "🧠 Сұрағыңызды жазыңыз:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Артқа", callback_data='main_menu')]
            ])
        )
    elif query.data == "news":
        await query.edit_message_text(
            NEWS_INFO,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Артқа", callback_data='main_menu')]
            ])
        )
    elif query.data == "majors":
        await query.edit_message_text(
            MAJORS_INFO,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Артқа", callback_data='main_menu')]
            ])
        )
    elif query.data == "contact":
        await query.edit_message_text(
            CONTACT_INFO,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Артқа", callback_data='main_menu')]
            ])
        )
    elif query.data == "main_menu":
        context.user_data["mode"] = None
        await show_main_menu(update, context)

# AI сұрақ өңдеуші
async def handle_ai_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") == "ask_ai":
        question = update.message.text
        await update.message.reply_text("🤖 Жауап дайындап жатырмын...")

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": question}]
            )
            answer = response.choices[0].message.content.strip()

            # 🔘 Артқа батырмасы
            back_button = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Артқа", callback_data='main_menu')]
            ])

            # Жауапты жіберу
            if len(answer) <= 1000:
                await update.message.reply_text(f"📚 Жауап:\n{answer}", reply_markup=back_button)
            else:
                await update.message.reply_text("📚 Жауап төменде берілген 👇", reply_markup=back_button)
                await update.message.reply_text(answer, reply_markup=back_button)

        except Exception as e:
            await update.message.reply_text(f"⚠️ Кешіріңіз, қате кетті.\n{e}")
    else:
        await update.message.reply_text("Алдымен '🧠 Сұрақ қою (AI)' батырмасын басыңыз.")

# YouTube видеосын алу
def get_youtube_video(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=1,
        type="video"
    )
    response = request.execute()
    items = response.get("items")
    if items:
        video_id = items[0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

# Сурет келгенде GPT-4o арқылы өңдеу
async def handle_image_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_url = file.file_path

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Бұл суретте не бейнеленген?"},
                        {"type": "image_url", "image_url": {"url": file_url}}
                    ]
                }
            ],
            max_tokens=500
        )

        answer = response.choices[0].message.content.strip()

        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Артқа", callback_data='main_menu')]
        ])

        await update.message.reply_text(f"📷 Сурет сипаттамасы:\n{answer}", reply_markup=back_button)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Сурет өңдеу кезінде қате орын алды:\n{e}")

# Ботты іске қосу
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_question))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image_message))

    print("✅ Бот іске қосылды...")
    app.run_polling()
