import telebot
from dotenv import load_dotenv, find_dotenv
import os
from parsers import *
import datetime

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TELEGRAMM_TOKEN'))


@bot.message_handler(commands=['start'])
def start_message(message):
    """Функция для теста работоспособности бота"""
    bot.send_message(message.chat.id, 'Привет')


@bot.message_handler(content_types=['text'])
def get_time_message(message):
    """Обработка сообщений от пользователя на предмет игры в 'время'"""
    time_current_mesage = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
    if valid_time(message.text):
        if time_current_mesage == message.text.strip():
            score = parse_time(message.text)
            bot.send_message(message.chat.id, "Твой результат " + str(score))
        else:
            bot.send_message(message.chat.id, "Не успел?))))")


bot.polling(none_stop=True)
