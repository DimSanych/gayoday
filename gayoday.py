import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import random
import os
from telegram import InputFile
import json



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

#Функция ответа на ключевые фразы

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




#Функционал Гея дня

# Словарь для хранения участников каждой группы
group_members = {}

#Отслеживание активных участников
async def track_active_members(update: Update, context) -> None:
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    
    if chat_id not in group_members:
        group_members[chat_id] = set()
    
    group_members[chat_id].add(user_id)

    # Сохраняем обновленный список участников в JSON
    save_to_json()

#Отслеживание новых участников и исключение покинувших
async def track_members_status(update: Update, context) -> None:
    chat_id = update.effective_chat.id

    for user in update.message.new_chat_members:
        if chat_id not in group_members:
            group_members[chat_id] = set()
        group_members[chat_id].add(user.id)
    
    if update.message.left_chat_member:
        user_id = update.message.left_chat_member.id
        if chat_id in group_members and user_id in group_members[chat_id]:
            group_members[chat_id].remove(user_id)
    
    # Сохраняем обновленный список участников в JSON
    save_to_json()

#Сохранение и загрузка данных из JSON
def save_to_json():
    with open("group_members.json", "w") as file:
        json.dump(group_members, file)

def load_from_json():
    global group_members
    try:
        with open("group_members.json", "r") as file:
            group_members = json.load(file)
    except FileNotFoundError:
        group_members = {}

# #Функция пидора дня
# async def gay_of_the_day(update: Update, context) -> None:
#     # Загружаем актуальный список участников из JSON
#     load_from_json()

#     chat_id = update.effective_chat.id
#     if chat_id in group_members:
#         members_list = list(group_members[chat_id])
        
#         # Словарь для хранения результатов бросков
#         dice_rolls = {}
        
#         for member_id in members_list:
#             member = await context.bot.get_chat_member(chat_id, member_id)
#             dice_rolls[member.user.first_name] = random.randint(0, 100)
        
#         # Сортируем участников по результатам броска в порядке убывания
#         sorted_rolls = sorted(dice_rolls.items(), key=lambda x: x[1], reverse=True)
        
#         # Формируем сообщение с топ-5 участниками
#         message = "Топ-5 участников сегодня:\n"
#         for i in range(min(5, len(sorted_rolls))):
#             message += f"{sorted_rolls[i][0]}: {sorted_rolls[i][1]}%\n"
        
#         # Поздравляем участника с самым большим броском
#         message += f"\nПоздравляем {sorted_rolls[0][0]}! Ты Гей дня с рейтингом {sorted_rolls[0][1]}%!"
        
#         await update.message.reply_text(message)
#     else:
#         await update.message.reply_text("В этой группе пока нет активных участников.")



def main() -> None:
    # Создаем экземпляр бота и передаем ему токен вашего бота
    application = Application.builder().token("6696148424:AAE1JPSQJShBy_5SvPDODvdKRJ7H99xQ24c").build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_members))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))


    # Запускаем бота
    application.run_polling()





if __name__ == "__main__":
    main()
