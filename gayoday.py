import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import random
import os
from telegram import InputFile
import json
import telegram
import datetime

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


    # Проверка на команду /члены
    # Засунул сюда чтобы сидели на одном обработчике
    if update.message.text == "/члены":
        return await members_list(update, context)
    
    if update.message.text == "/гейдня":
        await show_gay_of_the_day(update, context)
    elif update.message.text == "/сброс":
        await reset_gay_of_the_day(update, context)

    if update.message.text == "/лидеры":
        return await show_leaders(update, context)    

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
            try:
                # Получаем информацию о участнике по его ID
                member_info = await context.bot.get_chat_member(chat_id, user_id)
        
                # Формируем полное имя участника
                full_name = member_info.user.first_name
                if member_info.user.last_name:
                    full_name += " " + member_info.user.last_name
        
                # Если у пользователя есть username, формируем ссылку на его профиль
                if member_info.user.username:
                    user_link = f'<a href="tg://user?id={user_id}">{full_name}</a>'
                else:
                    user_link = full_name
        
                # Добавляем ссылку на профиль участника в список
                members_names.append(user_link)

            except telegram.error.BadRequest:
        # Если информация о пользователе не найдена, просто пропускаем этого пользователя
                    logger.warning(f"Couldn't fetch data for user ID {user_id} in chat {chat_id}.")

        
        # Преобразуем список имен в строку и отправляем ее в чат
        members_names.insert(0, "<b>Участники клуба любителей пощекотать очко:</b>")
        await update.message.reply_text("\n".join(members_names), parse_mode='HTML')
    else:
        # Если этого чата нет в нашем словаре, отправляем соответствующее сообщение
        await update.message.reply_text("В этой группе пока еще нет пидрил.")


#Определение гея дня

GAY_OF_THE_DAY_FILE = "gay_of_the_day.json"

# Функция для генерации списка геев дня
def generate_gay_of_the_day():
    # Загружаем список активных участников
    with open("group_members.json", "r") as file:
        group_members = json.load(file)

    gay_of_the_day = {}

    # Для каждой группы генерируем рейтинг участников
    for chat_id, members in group_members.items():
        ratings = {member: random.randint(0, 100) for member in members}
        sorted_ratings = dict(sorted(ratings.items(), key=lambda item: item[1], reverse=True))
        gay_of_the_day[chat_id] = sorted_ratings
        members_scores = gay_of_the_day[chat_id]
        winner_id = max(members_scores, key=members_scores.get)
        winner_score = members_scores[winner_id]
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        save_daily_stats(current_date, chat_id, winner_id, winner_score, members_scores)


    # Сохраняем сгенерированный список в файл
    with open(GAY_OF_THE_DAY_FILE, "w") as file:
        json.dump(gay_of_the_day, file, indent=4)


    return gay_of_the_day

# Обработчик команды /гейдня
async def show_gay_of_the_day(update: Update, context):
    # Загрузка данных из файла
    with open(GAY_OF_THE_DAY_FILE, "r") as file:
        gay_of_the_day_data = json.load(file)
    
    chat_id = str(update.effective_chat.id)
    
    if chat_id in gay_of_the_day_data:
        sorted_gays = sorted(gay_of_the_day_data[chat_id].items(), key=lambda x: x[1], reverse=True)
        
        # Формирование списка имен участников
        members_names = []
        for user_id, score in sorted_gays:
            try:
                # Получаем информацию о участнике по его ID
                member_info = await context.bot.get_chat_member(chat_id, int(user_id))
        
                # Формируем полное имя участника
                full_name = member_info.user.first_name
                if member_info.user.last_name:
                    full_name += " " + member_info.user.last_name
        
                # Если у пользователя есть username, формируем ссылку на его профиль
                if member_info.user.username:
                    user_link = f'<a href="tg://user?id={user_id}">{full_name}</a>'
                else:
                    user_link = full_name
        
                # Добавляем ссылку на профиль участника и его бросок в список
                members_names.append(f"{user_link} пидрила на {score}%")

            except telegram.error.BadRequest:
                logger.warning(f"Couldn't fetch data for user ID {user_id} in chat {chat_id}.")
        
        # Отправляем список участников и их броски в чат
        await update.message.reply_text("\n".join(members_names), parse_mode='HTML')
        
        # Отправляем поздравление участнику с наибольшим броском
        winner_id, winner_score = sorted_gays[0]
        winner_info = await context.bot.get_chat_member(chat_id, int(winner_id))
        winner_name = winner_info.user.first_name
        if winner_info.user.last_name:
            winner_name += " " + winner_info.user.last_name
        await update.message.reply_text(f"Поздравляю, пидор дня - {winner_name}!")
    else:
        await update.message.reply_text("Список геев дня пока еще не сформирован.")


# Обработчик команды /сброс
# async def reset_gay_of_the_day(update: Update, context):
#     generate_gay_of_the_day()
#     await update.message.reply_text("Список геев дня был сброшен и сгенерирован заново!")

# Обработчик команды /сброс
async def reset_gay_of_the_day(update: Update, context):
    chat_id = str(update.effective_chat.id)
    
    # Загрузка текущих данных из файла
    with open(GAY_OF_THE_DAY_FILE, "r") as file:
        gay_of_the_day_data = json.load(file)
    
    # Проверяем, есть ли этот чат в данных
    if chat_id in gay_of_the_day_data:
        # Генерируем новые данные только для этого чата
        ratings = {str(member): random.randint(0, 100) for member in group_members[chat_id]}
        sorted_ratings = dict(sorted(ratings.items(), key=lambda item: item[1], reverse=True))
        gay_of_the_day_data[chat_id] = sorted_ratings
        members_scores = gay_of_the_day_data[chat_id]
        winner_id = max(members_scores, key=members_scores.get)
        winner_score = members_scores[winner_id]
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        save_daily_stats(current_date, chat_id, winner_id, winner_score, members_scores)

        # Сохраняем обновленные данные обратно в файл
        with open(GAY_OF_THE_DAY_FILE, "w") as file:
            json.dump(gay_of_the_day_data, file, indent=4)
        
        await update.message.reply_text("Определен новый пидрильный список!")
    else:
        await update.message.reply_text("В этой группе пока еще нет данных о геях дня.")


#Сбор статистики 

DAILY_STATS_FILE = "daily_stats.json"

def save_daily_stats(date, chat_id, winner_id, score, members_scores):
    # Загрузим текущую статистику
    try:
        with open(DAILY_STATS_FILE, "r") as file:
            daily_stats = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        daily_stats = {}

    # Добавим или обновим информацию для данной даты и чата
    if date not in daily_stats:
        daily_stats[date] = {}

    daily_stats[date][chat_id] = {
        "winner_id": winner_id,
        "score": score,
        "members": members_scores
    }

    # Сохраняем обновленную статистику обратно в файл
    with open(DAILY_STATS_FILE, "w") as file:
        json.dump(daily_stats, file, indent=4)

#Функция для загрузки ежедневной статистики
def load_daily_stats():
    try:
        with open(DAILY_STATS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
#Формируем список лидеров
async def get_leaders(chat_id, context):
    # Загрузка данных из файла
    try:
        with open("daily_stats.json", "r") as file:
            stats = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return "Статистика пока не доступна."

    # Подсчет побед для каждого участника
    leaders = {}
    for date, chats in stats.items():
        if str(chat_id) in chats:
            winner_id = chats[str(chat_id)]['winner_id']
            if winner_id in leaders:
                leaders[winner_id] += 1
            else:
                leaders[winner_id] = 1

    # Сортировка участников по количеству побед
    sorted_leaders = sorted(leaders.items(), key=lambda x: x[1], reverse=True)

    # Формирование списка лидеров
    leaders_list = ["<b>Таблица лидеров:</b>"]
    for user_id, wins in sorted_leaders:
        try:
            # Получаем информацию о участнике по его ID
            member_info = await context.bot.get_chat_member(chat_id, int(user_id))
    
            # Формируем полное имя участника
            full_name = member_info.user.first_name
            if member_info.user.last_name:
                full_name += " " + member_info.user.last_name
    
            # Если у пользователя есть username, формируем ссылку на его профиль
            if member_info.user.username:
                user_link = f'<a href="tg://user?id={user_id}">{full_name}</a>'
            else:
                user_link = full_name
    
            # Добавляем ссылку на профиль участника и его количество побед в список
            leaders_list.append(f"{user_link}: {wins} раз(а)")
        except telegram.error.BadRequest:
            logger.warning(f"Couldn't fetch data for user ID {user_id} in chat {chat_id}.")

    return "\n".join(leaders_list)

#Функция отображения списка лидеров:
async def show_leaders(update: Update, context) -> None:
    chat_id = update.effective_chat.id
    leaders_message = await get_leaders(chat_id, context)
    await update.message.reply_text(leaders_message, parse_mode='HTML')    






def main() -> None:

    #Загружаем список пользователей   
    load_from_json()

    # Создаем экземпляр бота и передаем ему токен вашего бота
    # # Регистрируем обработчики
    application = Application.builder().token("6696148424:AAET0jqVNxWOYQbDtRKyWos4VUbaqDSgf-M").build()


    # Группа 0: Обработчики участников чата
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_new_members), group=0)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_active_members), group=0)
    
    # Группа 1: Обработчики текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, handle_message), group=1)
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER, track_members_status), group=1)
    
    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()