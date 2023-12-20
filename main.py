import logging
import re
from datetime import datetime

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, \
    CallbackContext

TELEGRAM_TOKEN =("6679083154:AAEUXQWGVHtszmBD8xa6_Y98q6gSF864Lls")
TELEGRAM_CHAT_ID = ('-4062756263')
AUTHORIZED_CHAT_ID = ("409107123")

NAME, PHONE, DATE, NUMBER_OF_PEOPLE = range(4)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
BROADCAST_TEXT = range(5)

user_ids = set()
user_data = {}


def get_base_keyboard():
    keyboard = [["Fa rezervare"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
async def handle_reservation_button(update: Update, context: CallbackContext) -> int:
    # Resetăm conversația și începem din nou
    return await start(update, context)

async def start(update, context):
    reply_markup = get_base_keyboard()
    user = update.effective_user
    user_id = user.id
    user_ids.add(user_id)

    user_data[user_id] = {"first_name": user.first_name, "last_name": user.last_name}
    await context.bot.send_message(
        chat_id=user_id,
        text="Salutare! Vă rugăm să ne scrieți numele dvs",
        reply_markup=reply_markup,
    )
    return NAME


async def name(update, context):
    user_name = update.message.text
    if not re.match("^[A-Za-z ]+$", user_name):
        await update.message.reply_text(
            "Numele introdus este invalid. Vă rugăm să introduceți un nume valid (doar litere și spații)."
        )
        return NAME
    context.user_data["name"] = user_name
    await update.message.reply_text("Scrieți mai jos numărul de telefon")
    return PHONE


async def broadcast(update, context):
    if str(update.effective_chat.id) != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Nu aveți permisiunea de a utiliza această comandă.")
        return ConversationHandler.END
    await update.message.reply_text("Introduceți textul buletinului informativ:")
    return BROADCAST_TEXT


async def broadcast_message(update, context):
    broadcast_content = update.message.text
    if re.match(r"(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png)", broadcast_content):
        for user_id in user_ids:
            try:
                await context.bot.send_photo(chat_id=user_id, photo=broadcast_content)
            except Exception as e:
                logger.error(f"Nu s-a putut trimite fotografia utilizatorului {user_id}: {e}")
    else:
        for user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=user_id, text=broadcast_content)
            except Exception as e:
                logger.error(f"Nu s-a putut trimite mesajul utilizatorului {user_id}: {e}")
    return ConversationHandler.END


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


async def list_users(update, context):
    if str(update.effective_chat.id) != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Nu aveți permisiunea de a utiliza această comandă.")
        return
    if not user_ids:
        await update.message.reply_text("Lista este goală.")
        return
    users_list = "\n".join(
        [f"{uid} - {user_data[uid]['first_name']} {user_data[uid].get('last_name', '')}" for uid in user_ids]
    )
    await update.message.reply_text(f"Lista utilizatorilor care au apăsat /start:\n{users_list}")


async def date(update, context):
    date_text = update.message.text
    try:
        valid_date = datetime.strptime(date_text, "%d.%m.%Y")
        context.user_data["date"] = valid_date.strftime("%d.%m.%Y")
        await update.message.reply_text("Câte persoane veți fi?")
        return NUMBER_OF_PEOPLE
    except ValueError:
        await update.message.reply_text(
            "Data introdusă este invalidă. Vă rugăm să introduceți data în formatul ZZ.LL.AAAA (de exemplu, 31.12.2021)."
        )
        return DATE


async def cancel(update, context):
    await update.message.reply_text("Anulare. Folosește /start pentru a încerca din nou.")
    return ConversationHandler.END


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


from telegram.ext import ConversationHandler, MessageHandler, filters
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    reservation_handler = MessageHandler(filters.Regex("^Fa rezervare$"), handle_reservation_button)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      CommandHandler("broadcast", broadcast),
                      ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.Regex("^Fa rezervare$"), name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.Regex("^Fa rezervare$"), phone)],
            DATE: [MessageHandler(filters.TEXT, date)],
            NUMBER_OF_PEOPLE: [MessageHandler(filters.TEXT, number_of_people)],
            BROADCAST_TEXT: [MessageHandler(filters.TEXT, broadcast_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    list_handler = CommandHandler("list", list_users)


    app.add_handler(reservation_handler)
    app.add_handler(conv_handler)
    app.add_handler(list_handler)

    app.run_polling()

if __name__ == "__main__":
    main()