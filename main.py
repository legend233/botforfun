import telebot
from dotenv import load_dotenv, find_dotenv
import os
from parsers import *
import datetime
from sqltable import *

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TELEGRAMM_TOKEN'))


@bot.message_handler(commands=['top'])
def start_message(message):
    """Функция для теста работоспособности бота"""
    top_players = all_players()
    scores = []
    for player in top_players.keys():
        scores.append(f"{player}: {top_players[player]} очков")
    # отправляем gif анимацию и сообщение
    bot.send_animation(message.chat.id, open('images/top.gif', 'rb'), caption="\n".join(scores))


@bot.message_handler(content_types=['text'])
def get_time_message(message):
    """Обработка сообщений от пользователя на предмет игры в 'время'"""
    time_current_mesage = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
    if valid_time(message.text):
        if time_current_mesage == message.text.strip():
            score = parse_time(message.text)
            if score:
                change_player_score(message.from_user.username, score)
                gif = open('images/congratulations{score}.gif', 'rb')
                mess = f"Поздравляю, {message.from_user.first_name}! Получи {score} очков!\nТеперь у вас {get_player_score(message.from_user.username)} очков"
                bot.send_animation(message.chat.id, gif, caption=mess)
                
        else:
            bot.send_animation(message.chat.id, open('images/no.gif', 'rb'), caption="Не вышло...")


bot.polling(none_stop=True)
