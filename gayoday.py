import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import random
import os
from telegram import InputFile
import json

class GetUpdatesFilter(logging.Filter):
    def filter(self, record):
        return "getUpdates" not in record.getMessage()
    
filter = GetUpdatesFilter()
httpx_logger = logging.getLogger("httpx")
httpx_logger.addFilter(filter)

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
    chat_id = str(update.effective_chat.id)  # Преобразуем chat_id в строку
    user_id = update.message.from_user.id
    
    if chat_id not in group_members:
        group_members[chat_id] = set()
        
    if user_id not in group_members[chat_id]:
        group_members[chat_id].add(user_id)
        logger.info(f"User {user_id} added to active members in chat {chat_id}.")
        # Сохраняем обновленный список участников в JSON
        save_to_json()
    

#Отслеживание новых участников и исключение покинувших
async def track_members_status(update: Update, context) -> None:
    chat_id = str(update.effective_chat.id)

    # Если ID чата еще нет в group_members, создаем новый ключ
    if chat_id not in group_members:
        group_members[chat_id] = set()

    # Для новых участников
    for user in update.message.new_chat_members:
        group_members[chat_id].add(user.id)
        logger.info(f"New user {user.id} added to chat {chat_id}.")

    # Для участников, покинувших чат
    if update.message.left_chat_member:
        user_id = update.message.left_chat_member.id
        if user_id in group_members[chat_id]:
            group_members[chat_id].remove(user_id)
            logger.info(f"User {user_id} removed from chat {chat_id}.")
            
    # Сохраняем обновленный список участников в JSON
    save_to_json()

#Сохранение и загрузка данных из JSON
def save_to_json():
    with open("group_members.json", "w") as file:
        # Преобразовываем множества в списки перед сохранением
        json_data = {chat_id: list(user_ids) for chat_id, user_ids in group_members.items()}
        json.dump(json_data, file, indent=4)

def load_from_json():
    global group_members
    try:
        with open("group_members.json", "r") as file:
            json_data = json.load(file)
            # Преобразовываем списки обратно в множества после загрузки
            group_members = {chat_id: set(user_ids) for chat_id, user_ids in json_data.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        group_members = {}

# Функция для вывода списка участников группы из файла .json
async def members_list(update: Update, context) -> None:
    # Получаем ID чата
    chat_id = update.effective_chat.id
    
    # Загружаем данные из файла .json
    load_from_json()
    
    # Проверяем, есть ли этот чат в нашем словаре участников
    if str(chat_id) in group_members:
        # Инициализируем пустой список для имен участников
        members_names = []
        
        # Проходимся по каждому ID участника в этом чате
        for user_id in group_members[str(chat_id)]:
            # Получаем информацию о участнике по его ID
            member_info = await context.bot.get_chat_member(chat_id, user_id)
            # Добавляем имя участника в список
            full_name = member_info.user.first_name
            if member_info.user.last_name:
                full_name += " " + member_info.user.last_name
            members_names.append(full_name)
        
        # Преобразуем список имен в строку и отправляем ее в чат
        members_names.insert(0, "<b>Участники клуба любителей пощекотать очко:</b>", parse_mode='HTML')
        await update.message.reply_text("\n".join(members_names))
    else:
        # Если этого чата нет в нашем словаре, отправляем соответствующее сообщение
        await update.message.reply_text("В этой группе пока еще нет пидрил.")



def main() -> None:

    #Загружаем список пользователей   
    load_from_json()

    # Создаем экземпляр бота и передаем ему токен вашего бота
    # # Регистрируем обработчики
    application = Application.builder().token("6696148424:AAE1JPSQJShBy_5SvPDODvdKRJ7H99xQ24c").build()

    # # Регистрируем обработчики
    # application.add_handler(CommandHandler("start", start))
    # application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_members))
    # application.add_handler(MessageHandler(filters.TEXT, handle_message))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_active_members))
    # application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER, track_members_status))
    # #Тестовые обработчики
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_on_condition))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, log_new_user))

# Группа 0: Обработчики участников чата
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_members), group=0)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_active_members), group=0)
    
    # Группа 1: Обработчики текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, handle_message), group=1)
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER, track_members_status), group=1)
    application.add_handler(CommandHandler("members", members_list), group=0)
    
    # Группа 2: Тестовые обработчики
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_on_condition), group=2)
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, log_new_user), group=2)





    # Запускаем бота
    application.run_polling()





if __name__ == "__main__":
    main()