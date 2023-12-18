import logging
import re

import environ
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters

environ.Env.read_env()

env = environ.Env()

TELEGRAM_TOKEN = env("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID")

NAME, PHONE, DATE, NUMBER_OF_PEOPLE = range(4)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update, context):
    await update.message.reply_text("Cum vă numiți?")
    return NAME


async def name(update, context):
    user_name = update.message.text
    if not re.match("^[A-Za-z ]+$", user_name):
        await update.message.reply_text(
            "Numele introdus este invalid. Vă rugăm să introduceți un nume valid (doar litere și spații)."
        )
        return NAME
    context.user_data["name"] = user_name
    await update.message.reply_text("Care este numărul dvs de telefon?")
    return PHONE


async def phone(update, context):
    user_phone = update.message.text
    if not re.match("^\d{7,15}$", user_phone):
        await update.message.reply_text(
            "Numărul de telefon introdus este invalid. Vă rugăm să introduceți un număr valid (doar cifre, între 7 și "
            "15 cifre)."
        )
        return PHONE
    context.user_data["phone"] = user_phone
    await update.message.reply_text("Pentru ce dată doriți să faceți rezervarea?")
    return DATE


async def date(update, context):
    context.user_data["date"] = update.message.text
    await update.message.reply_text("Câte persoane veți fi?")
    return NUMBER_OF_PEOPLE


async def number_of_people(update, context):
    context.user_data["number_of_people"] = update.message.text

    message = (
        f"Solicitare de rezervare:\n"
        f"Nume: {context.user_data['name']}\n"
        f"Telefon: {context.user_data['phone']}\n"
        f"Data: {context.user_data['date']}\n"
        f"Număr de persoane: {context.user_data['number_of_people']}"
    )

    await update.message.reply_text(
        f"Solicitarea dvs pentru {context.user_data['name']} pentru {context.user_data['date']} a fost înregistrată, în"
        f" scurt timp revenim cu confirmarea telefonică!"
    )

    await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

    return ConversationHandler.END


async def cancel(update, context):
    await update.message.reply_text("Anulare. Folosește /start pentru a încerca din nou.")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT, name)],
            PHONE: [MessageHandler(filters.TEXT, phone)],
            DATE: [MessageHandler(filters.TEXT, date)],
            NUMBER_OF_PEOPLE: [MessageHandler(filters.TEXT, number_of_people)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
