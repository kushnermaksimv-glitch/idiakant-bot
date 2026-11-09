import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = "ТВОЙ_ТЕЛЕГРАМ_ТОКЕН"

# --- Клавиатуры (Меню) ---

def get_main_menu():
    """Главное интерактивное меню бота."""
    keyboard = [
        [
            InlineKeyboardButton("📜 Правила", callback_data="rules"),
            InlineKeyboardButton("📊 Статистика", callback_data="stats")
        ],
        [
            InlineKeyboardButton("🎲 Бросить кубик", callback_data="roll_dice"),
            InlineKeyboardButton("💡 Помощь", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Кнопка возврата в меню."""
    keyboard = [[InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)

# --- Обработчики команд ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start — вызов главного меню."""
    user_name = update.effective_user.first_name
    text = (
        f"Привет, {user_name}! 👑\n\n"
        f"Я — главный **Бот Идиаканта**.\n"
        f"Готов помогать в управлении чатом, отвечать на вопросы и развлекать участников.\n\n"
        f"Выбери нужный раздел в меню ниже:"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_menu())
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu())

async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на инлайн-кнопки."""
    query = update.callback_query
    await query.answer()

    if query.data == "main_menu":
        await start(update, context)

    elif query.data == "rules":
        text = (
            "📜 **Правила сообщества:**\n\n"
            "1. Соблюдайте взаимное уважение.\n"
            "2. Без спама и несогласованной рекламы.\n"
            "3. Придерживайтесь тематики чата."
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

    elif query.data == "stats":
        chat = update.effective_chat
        user_id = query.from_user.id
        members = await chat.get_member_count() if chat.type != "private" else 1
        text = (
            f"📊 **Системная информация:**\n\n"
            f"• Ваш ID: `{user_id}`\n"
            f"• Тип чата: {chat.type}\n"
            f"• Участников в чате: {members}"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

    elif query.data == "roll_dice":
        result = random.randint(1, 100)
        text = f"🎲 Тебе выпало число: **{result}** из 100!"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

    elif query.data == "help":
        text = (
            "⚙️ **Список доступных команд:**\n\n"
            "• `/menu` или `/start` — вызвать главное меню\n"
            "• `/id` — узнать свой ID\n"
            "• `/ping` — проверить отклик бота"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрая проверка работы бота."""
    await update.message.reply_text("🏓 Понг! Бот Идиаканта на связи и работает штатно.")

# --- Обработчик упоминаний и текста ---

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Реакция на упоминание имени Идиакант в тексте."""
    text = update.message.text.lower()
    if "идиакант" in text:
        await update.message.reply_text("Я тут! Чем могу помочь? Используй /menu для вызова главных функций.")

# --- Фоновые функции (Приветствие) ---

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тихое фоновое приветствие."""
    for new_member in update.message.new_chat_members:
        if new_member.id != context.bot.id:
            await update.message.reply_text(
                f"Приветствуем, [{new_member.first_name}](tg://user?id={new_member.id})! 👋\n"
                f"Нажми /menu, чтобы открыть возможности бота.",
                parse_mode="Markdown"
            )

def main():
    app = Application.builder().token(TOKEN).build()

    # Регистрация команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CommandHandler("ping", ping))

    # Обработка нажатий кнопок
    app.add_handler(CallbackQueryHandler(menu_callback_handler))

    # Обработка входа новых участников
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

    # Обработка текстовых сообщений (упоминания)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mention))

    print("Главный Бот Идиаканта успешно запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
  
