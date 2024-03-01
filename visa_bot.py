import requests
from bs4 import BeautifulSoup
import telebot
from datetime import datetime

# Константы для Telegram бота
TOKEN = '7088638221:AAHV6NwH_q265csV-5fvW6DTSpSzgpQASEk'
CHAT_ID = '5303775757'

# Константы для визового центра Испании
BASE_URL = 'https://blsspain-russia.com/moscow/book_appointment.php'
DATE_FORMAT = '%Y-%m-%d'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Инициализация Telegram бота
bot = telebot.TeleBot(TOKEN)

# Функция для получения доступных дат
def get_available_dates():
    response = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Извлекаем доступные даты из таблицы на странице
    dates_table = soup.find(id='sliderDates')
    available_dates = []
    for cell in dates_table.findAll('td'):
        date_string = cell.find('a').text.strip()
        date = datetime.strptime(date_string, DATE_FORMAT).date()
        available_dates.append(date)

    return available_dates

# Функция для проверки статуса записи
def check_booking_status(chat_id):
    available_dates = get_available_dates()

    # Если есть доступные даты, отправляем сообщение пользователю
    if available_dates:
        message = f"Доступные даты для записи в визовый центр Испании:\n"
        for date in available_dates:
            message += f"{date.strftime(DATE_FORMAT)}\n"
    else:
        message = "Нет доступных дат для записи в визовый центр Испании."

    bot.send_message(chat_id, message)

# Функция для записи на выбранную дату
def book_date(chat_id, selected_date):
    available_dates = get_available_dates()

    # Проверяем, есть ли выбранная дата в списке доступных
    if selected_date in available_dates:
        message = f"Вы записаны на {selected_date.strftime(DATE_FORMAT)}"
    else:
        message = "Выбранная дата недоступна для записи."

    bot.send_message(chat_id, message)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот для записи на визу в Испанию. Чтобы начать, используйте команду /dates для получения доступных дат.")

# Обработчик команды /dates
@bot.message_handler(commands=['dates'])
def handle_dates(message):
    available_dates = get_available_dates()

    if available_dates:
        message_text = "Доступные даты для записи:\n"
        for date in available_dates:
            message_text += f"{date.strftime(DATE_FORMAT)}\n"
    else:
        message_text = "Нет доступных дат для записи."

    bot.send_message(message.chat.id, message_text)

# Обработчик команды /book
@bot.message_handler(commands=['book'])
def handle_book(message):
    try:
        selected_date = datetime.strptime(message.text.split()[1], DATE_FORMAT).date()
        book_date(message.chat.id, selected_date)
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Используйте команду /book в формате /book YYYY-MM-DD")

# Обработчик команды /status
@bot.message_handler(commands=['status'])
def handle_status(message):
    check_booking_status(message.chat.id)

# Запуск Telegram бота
bot.polling()
