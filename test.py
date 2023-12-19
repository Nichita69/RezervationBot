import logging

from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
BROADCAST = range(4)

user_ids = set()


async def start(update, context):
    user_id = update.effective_chat.id
    user_ids.add(user_id)
    await context.bot.send_message(chat_id=user_id, text="Привет! Теперь вы подписаны на рассылку.")


async def broadcast(update, context):
    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id, text="Привет всем, кто нажал на старт")
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")


def cancel(update, context):
    update.message.reply_text("Anulare. Folosește /start pentru a încerca din nou.")
    return ConversationHandler.END


# Остальные импорты и определения функций...


def main():
    app = ApplicationBuilder().token("6975502522:AAEyevdFTbct4-Ya4J2iP6xQXKhT7Mnek_Q").build()

    # Обработчик для команды /start
    start_handler = CommandHandler("start", start)

    # Обработчик для команды /broadcast
    broadcast_handler = CommandHandler("broadcast", broadcast)

    # Добавление обработчиков в приложение
    app.add_handler(start_handler)
    app.add_handler(broadcast_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
