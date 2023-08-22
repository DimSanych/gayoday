from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я пидрила дня!.')

def main() -> None:
    TOKEN = "6696148424:AAG6-hZc4c2SAEEJwpU5QSp5smdK77ijcGI"
    updater = Updater(TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
