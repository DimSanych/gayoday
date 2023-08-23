import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import random
import os
from telegram import InputFile



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

# Функция приветствия при добавлении бота в группу
async def greet_new_members(update: Update, context) -> None:
    for user in update.message.new_chat_members:
        #
        if user.username == context.bot.username:
            await update.message.reply_text("Я искал пидрильный клуб любителей пощекотать очко и похоже я его нашел! Всем привет!")

        else:
            await update.message.reply_text("Мойдодыр, принимай пополнение!")
            with open("moydodir.jpg", "rb") as photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)        

# # Функция "Гей дня"
# async def gay_of_the_day(update: Update, context) -> None:
#     chat_id = update.effective_chat.id
#     members = await context.bot.get_chat_members_count(chat_id)
#     random_member = random.randint(1, members)
#     user = await context.bot.get_chat_member(chat_id, random_member)
#     score = random.randint(0, 100)
#     await update.message.reply_text(f"Гей дня: {user.user.first_name} с гей-рейтингом {score}%!")

# Функция "Гей дня"
async def gay_of_the_day(update: Update, context) -> None:
    chat_id = update.effective_chat.id
    members_list = await context.bot.get_chat_members(chat_id)
    members_count = len(members_list)
    
    # Словарь для хранения участников и их рейтинга
    members_rating = {}
    
    # Проходимся по каждому участнику и присваиваем ему рейтинг
    for i in range(1, members_count + 1):
        user = members_list[i].user
        score = random.randint(0, 100)
        members_rating[user.first_name] = score
    
    # Сортируем участников по рейтингу
    sorted_members = sorted(members_rating.items(), key=lambda x: x[1], reverse=True)
    
    # Формируем сообщение
    message = "Насколько ты сегодня пидрила:\n"
    for member, rating in sorted_members:
        message += f"{member}: {rating}%\n"
    
    await update.message.reply_text(message)  

def main() -> None:
    # Создаем экземпляр бота и передаем ему токен вашего бота
    application = Application.builder().token("6696148424:AAG6-hZc4c2SAEEJwpU5QSp5smdK77ijcGI").build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("whoispidor", gay_of_the_day))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_members))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))


    # Запускаем бота
    application.run_polling()

# Список фраз, на которые бот будет реагировать
PIDOR_PHRASES = ["пидр", "пидар", "пидор"]

#Функция ответа ботом на оскорбления
async def handle_message(update: Update, context) -> None:
    if update.message and update.message.text:
        user_message = update.message.text.lower()  # Преобразуем сообщение в нижний регистр
        for phrase in PIDOR_PHRASES:
            if phrase in user_message:
                images_dir = "tipidr"

            # Если одна из ключевых фраз найдена в сообщении
                images = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith('.jpg')]
                random_image = random.choice(images)
                with open(random_image, 'rb') as photo:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, reply_to_message_id=update.message.message_id)
                # await update.message.reply_text("А может ты пидр?")

                break  # Выходим из цикла после отправки изображения



if __name__ == "__main__":
    main()
