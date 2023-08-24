import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters


# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обработчик команды /start
async def start(update: Update, context) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}!",
    )

# Обработчик для повторения отправленных сообщений
#async def echo(update: Update, context) -> None:
#    await update.message.reply_text(update.message.text)

def main() -> None:
    # Создаем экземпляр бота и передаем ему токен вашего бота
    application = Application.builder().token("6696148424:AAG6-hZc4c2SAEEJwpU5QSp5smdK77ijcGI").build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_members))



    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()



# Функция приветствия при добавлении бота в группу
async def greet_new_members(update: Update, context) -> None:
    for user in Update.message.NEW_CHAT_MEMBERS:
        if user.username == context.bot.username:
            await Update.message.reply_text("Я искал пидрильный клуб любителей пощекотать очко и похоже я его нашел! Всем привет!")
