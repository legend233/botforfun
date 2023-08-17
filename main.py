import telebot
from dotenv import load_dotenv, find_dotenv
import os
from parsers import *
import datetime

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TELEGRAMM_TOKEN'))


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет')


@bot.message_handler(content_types=['text'])
def get_time_message(message):
    time_current_mesage = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
    print(time_current_mesage)
    print(message.text.strip())
    if time_current_mesage == message.text.strip():
        if valid_time(message.text):
            score = parse_time(message.text)
            bot.send_message(message.chat.id, "Твой результат " + str(score))
    else:
        bot.send_message(message.chat.id, "Не успел?))))")


bot.polling(none_stop=True)
