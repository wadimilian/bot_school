# Імпортуємо необхідні бібліотеки
import os
import telebot
import requests
import json

# Отримуємо токен бота з змінної середовища
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot('6290290376:AAEmJ6IWNqMDfGEtSvCDLBQy_bLfAlnK-8E')

# Отримуємо URL бази даних на GitHub (умовний)
DB_URL = "https://github.com/wadimilian/bot_school/blob/main/database.json?raw=true"

# Створюємо словник для збереження ідентифікаторів учнів та викладачів
# Ключ - ідентифікатор Telegram, значення - ідентифікатор у базі даних
ids = {}

# Створюємо функцію для отримання даних з бази даних
def get_data():
    # Використовуємо requests для запиту до URL
    response = requests.get(DB_URL)
    # Перевіряємо статус-код відповіді
    if response.status_code == 200:
        # Повертаємо дані у форматі JSON
        return response.json()
    else:
        # Повертаємо порожній словник у разі помилки
        return {}

# Створюємо функцію для отримання розкладу з бази даних
def get_schedule():
    # Отримуємо дані з бази даних
    data = get_data()
    # Перевіряємо, чи є розклад у даних
    if "schedule" in data:
        # Повертаємо розклад як рядок
        return "\n".join(data["schedule"])
    else:
        # Повертаємо повідомлення про відсутність розкладу
        return "Розклад не знайдено."

# Створюємо функцію для отримання журналу з балами з бази даних
def get_journal(student_id):
    # Отримуємо дані з бази даних
    data = get_data()
    # Перевіряємо, чи є журнал у даних
    if "journal" in data:
        # Перевіряємо, чи є учень у журналі
        if student_id in data["journal"]:
            # Повертаємо журнал учня як рядок
            return "\n".join(data["journal"][student_id])
        else:
            # Повертаємо повідомлення про відсутність учня в журналі
            return "Учень не знайдений в журналі."
    else:
        # Повертаємо повідомлення про відсутність журналу
        return "Журнал не знайдено."

# Створюємо функцію для надсилання домашнього завдання певному класу
def send_homework(teacher_id, class_id, homework):
    # Отримуємо дані з бази даних
    data = get_data()
    # Перевіряємо, чи є викладачі у даних
    if "teachers" in data:
        # Перевіряємо, чи є викладач у списку
        if teacher_id in data["teachers"]:
            # Отримуємо ім'я викладача
            teacher_name = data["teachers"][teacher_id]
            # Перевіряємо, чи є класи у даних
            if "classes" in data:
                # Перевіряємо, чи є клас у списку
                if class_id in data["classes"]:
                    # Отримуємо список учнів класу
                    students = data["classes"][class_id]
                    # Проходимо по кожному учневі
                    for student in students:
                        # Перевіряємо, чи є учень у словнику ідентифікаторів
                        if student in ids:
                            # Отримуємо ідентифікатор Telegram учня
                            chat_id = ids[student]
                            # Надсилаємо повідомлення з домашнім завданням учневі
                            bot.send_message(chat_id, f"Викладач {teacher_name} надав вам таке домашнє завдання:\n{homework}")
                    # Повертаємо повідомлення про успішну розсилку
                    return "Домашнє завдання успішно надіслано."
                else:
                    # Повертаємо повідомлення про відсутність класу
                    return "Клас не знайдений."
            else:
                # Повертаємо повідомлення про відсутність класів
                return "Класи не знайдені."
        else:
            # Повертаємо повідомлення про відсутність викладача
            return "Викладач не знайдений."
    else:
        # Повертаємо повідомлення про відсутність викладачів
        return "Викладачі не знайдені."

# Створюємо обробник для команди /start
@bot.message_handler(commands=['start'])
def start(message):
    # Виводимо привітальне повідомлення та запитуємо ідентифікатор користувача
    bot.send_message(message.chat.id, "Привіт, я бот телеграм для школи. Будь ласка, введіть свій ідентифікатор.")

# Створюємо обробник для текстових повідомлень
@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Отримуємо текст повідомлення та ідентифікатор Telegram користувача
    text = message.text
    chat_id = message.chat.id

    # Перевіряємо, чи є користувач у словнику ідентифікаторів
    if chat_id in ids:
        # Отримуємо ідентифікатор користувача в базі даних
        user_id = ids[chat_id]
        # Перевіряємо, чи є команди у текстовому повідомленні
        if text.startswith("/"):
            # Розбиваємо текст на слова за пробілами
            words = text.split()
            # Отримуємо перше слово як команду
            command = words[0]
            # Обробляємо різні команди
            if command == "/schedule":
                # Виводимо розклад з бази даних
                bot.send_message(chat_id, get_schedule())
            elif command == "/journal":
                # Виводимо журнал з балами
                bot.send_message(chat_id, get_journal(user_id))
            elif command == "/homework":
                # Перевіряємо, чи є достатньо аргументів для команди
                if len(words) >= 3:
                    # Отримуємо ідентифікатор класу та домашнє завдання
                    class_id = words[1]
                    homework = " ".join(words[2:])
                    # Надсилаємо домашнє завдання певному класу
                    bot.send_message(chat_id, send_homework(user_id, class_id, homework))
                else:
                    # Виводимо повідомлення про неправильний формат команди
                    bot.send_message(chat_id, "Неправильний формат команди. Будь ласка, введіть /homework <class_id> <homework>.")
            else:
                # Виводимо повідомлення про невідому команду
                bot.send_message(chat_id, "Невідома команда. Будь ласка, введіть /schedule, /journal або /homework.")
        else:
            # Виводимо повідомлення про те, що бот розуміє тільки команди
            bot.send_message(chat_id, "Бот розуміє тільки команди. Будь ласка, введіть /schedule, /journal або /homework.")
    else:
        # Перевіряємо, чи є текст повідомлення ідентифікатором користувача
        if text.isalnum():
            # Зберігаємо ідентифікатор користувача у словнику
            ids[chat_id] = text
            # Виводимо повідомлення про успішну реєстрацію
            bot.send_message(chat_id, "Ви успішно зареєстровані. Тепер ви можете використовувати команди /schedule, /journal або /homework.")
        else:
            # Виводимо повідомлення про неправильний ідентифікатор користувача
            bot.send_message(chat_id, "Неправильний ідентифікатор. Будь ласка, введіть свій ідентифікатор.")

# Запускаємо бота
bot.polling()
