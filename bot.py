"""
Gelt Telegram Bot — ИИ-ассистент (Groq, python-telegram-bot 21.x)
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
)
from groq import Groq

load_dotenv()
BOT_TOKEN   = os.getenv("BOT_TOKEN")
GROQ_KEY    = os.getenv("GROQ_API_KEY")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/gelt_app")
APP_URL     = os.getenv("APP_URL", "https://gelt.app")

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

groq_client = Groq(api_key=GROQ_KEY)
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
Ты — ИИ-ассистент приложения Gelt. Gelt — мобильное приложение для обучения
программированию школьников, сделанное в стиле Duolingo (XP, сердечки, геймификация).
Сейчас доступен Модуль 1: Pascal.

О приложении:
- Учит программированию без воды и платных замков
- Кириллица, офлайн-режим, соответствует ФГОС
- 5 сердечек на модуль, XP за правильные ответы
- Создано школьниками в 2025 году

Модуль 1 — Pascal (5 уроков):
1. Вывод данных — writeln/write, точка с запятой, строки в одинарных кавычках
2. Переменные и типы — integer, real, string, boolean, char; раздел var до begin
3. Константы — раздел const, нельзя менять после объявления
4. Типы данных — отличия char от string, boolean (true/false)
5. Итоговый тест — квиз на все темы, +100 XP

Правила:
- Объясняй простым языком для школьников
- Не раскрывай ответы на квизы напрямую — объясняй концепцию
- Дружелюбный тон, умеренные эмодзи
- Отвечай на русском (или на языке пользователя)
- Не выдумывай функции которых нет в приложении
"""

user_history: dict[int, list[dict]] = {}
MAX_HISTORY = 20

def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Открыть Gelt", url=APP_URL),
         InlineKeyboardButton("📢 Наш канал", url=CHANNEL_URL)],
        [InlineKeyboardButton("📚 Что такое Gelt?", callback_data="about"),
         InlineKeyboardButton("🎓 Модули", callback_data="modules")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help"),
         InlineKeyboardButton("💬 Задать вопрос ИИ", callback_data="chat")],
    ])

def back_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"),
         InlineKeyboardButton("🎓 Модули", callback_data="modules")]
    ])

LESSONS = {
    "l1": "📘 *Урок 1: Вывод данных*\n\n`writeln('текст')` — с переносом строки\n`write('текст')` — без переноса\n\nЧисла без кавычек: `writeln(42)`\nПосле каждой команды ставь `;`\n\nЗадай вопрос по этой теме 💬",
    "l2": "📘 *Урок 2: Переменные и типы*\n\nРаздел `var` объявляется до `begin`:\n```\nvar\n  x: integer;\n  name: string;\n```\nТипы: `integer`, `real`, `string`, `boolean`, `char`\n\nЗадай вопрос 💬",
    "l3": "📘 *Урок 3: Константы*\n\nРаздел `const` — значение нельзя изменить:\n```\nconst\n  MAX = 100;\n  PI = 3.14;\n```\nОбъявляется до `var` и `begin`.\n\nЗадай вопрос 💬",
    "l4": "📘 *Урок 4: Типы данных*\n\n`char` — один символ: `'A'`\n`string` — текст любой длины\n`boolean` — только `true` или `false`\n`integer` — целые, `real` — дробные\n\nЗадай вопрос 💬",
}

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Привет, {name}! 👋\n\nЯ — ИИ-ассистент приложения *Gelt* 🟢\n"
        "Помогу разобраться с уроками Pascal и отвечу на вопросы об приложении.\n\n"
        "Напиши вопрос или выбери раздел 👇",
        reply_markup=main_kb(), parse_mode="Markdown",
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Что я умею:*\n\n• Объясняю темы Pascal из уроков Gelt\n"
        "• Рассказываю о функционале приложения\n• Веду свободный диалог\n\n"
        "📌 *Команды:*\n/start — главное меню\n/modules — уроки\n"
        "/about — об приложении\n/reset — очистить диалог\n\nПросто напиши вопрос 💬",
        parse_mode="Markdown",
    )

async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_history.pop(update.effective_user.id, None)
    await update.message.reply_text("🔄 История очищена. Задай вопрос 👇", reply_markup=main_kb())

async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📱 *Gelt — программирование для школы*\n\n"
        "✅ Без воды и платных замков\n✅ Кириллица и офлайн-режим\n"
        "✅ Соответствует ФГОС\n✅ XP, сердечки, достижения\n\n"
        "🚀 Создано школьниками в 2025 году.\nСейчас доступен *Модуль 1: Pascal*.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Открыть приложение", url=APP_URL)],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
        ]),
    )

async def cmd_modules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Модуль 1 — Pascal:*\n\n🟢 Урок 1 — Вывод данных\n"
        "🟢 Урок 2 — Переменные и типы\n🟢 Урок 3 — Константы\n"
        "🟢 Урок 4 — Типы данных\n🟢 Урок 5 — Итоговый тест (+100 XP)\n\n"
        "🔒 Модуль 2 — Python *(скоро)*\n\nНажми на урок — объясню тему 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📘 Вывод данных", callback_data="l1"),
             InlineKeyboardButton("📘 Переменные", callback_data="l2")],
            [InlineKeyboardButton("📘 Константы", callback_data="l3"),
             InlineKeyboardButton("📘 Типы данных", callback_data="l4")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
        ]),
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    if d == "main_menu":
        await q.edit_message_text("Главное меню — выбери раздел или задай вопрос 👇", reply_markup=main_kb())
    elif d == "about":
        await q.edit_message_text(
            "📱 *Gelt — программирование для школы*\n\n✅ Без воды и платных замков\n"
            "✅ Кириллица и офлайн-режим\n✅ Соответствует ФГОС\n✅ XP, сердечки, достижения\n\n"
            "🚀 Создано школьниками в 2025 году.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📱 Открыть приложение", url=APP_URL)],
                [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
            ]),
        )
    elif d == "modules":
        await q.edit_message_text(
            "📚 *Модуль 1 — Pascal:*\n\n🟢 Урок 1 — Вывод данных\n"
            "🟢 Урок 2 — Переменные и типы\n🟢 Урок 3 — Константы\n"
            "🟢 Урок 4 — Типы данных\n🟢 Урок 5 — Итоговый тест (+100 XP)\n\n"
            "🔒 Модуль 2 — Python *(скоро)*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📘 Вывод данных", callback_data="l1"),
                 InlineKeyboardButton("📘 Переменные", callback_data="l2")],
                [InlineKeyboardButton("📘 Константы", callback_data="l3"),
                 InlineKeyboardButton("📘 Типы данных", callback_data="l4")],
                [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")],
            ]),
        )
    elif d in LESSONS:
        await q.edit_message_text(
            LESSONS[d], parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 К модулям", callback_data="modules")]]),
        )
    elif d == "help":
        await q.edit_message_text(
            "🤖 Просто напиши любой вопрос — отвечу!\n\nПримеры:\n"
            "• _«Что такое writeln?»_\n• _«Как объявить переменную?»_\n"
            "• _«Чем char отличается от string?»_\n\n/reset — очистить историю",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]),
        )
    elif d == "chat":
        await q.edit_message_text("💬 Напиши вопрос — отвечу про Pascal, Gelt или что угодно 👇")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    if not text:
        return

    history = user_history.setdefault(uid, [])
    history.append({"role": "user", "content": text})
    if len(history) > MAX_HISTORY:
        user_history[uid] = history[-MAX_HISTORY:]

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    try:
        resp = groq_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + user_history[uid],
            max_tokens=1024,
            temperature=0.7,
        )
        reply = resp.choices[0].message.content
        user_history[uid].append({"role": "assistant", "content": reply})
    except Exception as e:
        logger.error("Groq error: %s", e)
        reply = "⚠️ Что-то пошло не так. Попробуй чуть позже или напиши нам в канал 📢"

    await update.message.reply_text(reply, reply_markup=back_kb(), parse_mode="Markdown")

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не задан в .env!")
    if not GROQ_KEY:
        raise ValueError("GROQ_API_KEY не задан в .env!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",   cmd_start))
    app.add_handler(CommandHandler("help",    cmd_help))
    app.add_handler(CommandHandler("reset",   cmd_reset))
    app.add_handler(CommandHandler("about",   cmd_about))
    app.add_handler(CommandHandler("modules", cmd_modules))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Gelt Bot запущен на Groq!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
