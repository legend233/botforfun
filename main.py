import telebot
from dotenv import load_dotenv, find_dotenv
import os
from parsers import *
import datetime
from sqltable import *

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TELEGRAMM_TOKEN'))

temp_moments = dict()

def token(score):
    emoji = ["💰", "💶", "🏆", "💎","👑"]
    if score < 50:
        return emoji[0]
    elif score < 75:
        return emoji[1]
    elif score < 100:
        return emoji[2]
    elif score < 125:
        return emoji[3]
    else:
        return emoji[4]


@bot.message_handler(commands=['test'])
def start_message(message):
    """Функция для теста работоспособности бота"""
    time_current_mesage = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
    bot.send_message(message.chat.id, "Сейчас время: "+time_current_mesage)


@bot.message_handler(commands=['top'])
def start_message(message):
    top_players = all_players().items()
    sort_top_players = sorted(top_players, key=lambda x: int(x[1]), reverse=True)
    scores = []
    for player, score in sort_top_players:
        scores.append(f"{player}: {score} {token(score)}")
    # отправляем gif анимацию и сообщение
    bot.send_animation(message.chat.id, open('images/top.gif', 'rb'), caption="\n".join(scores))


@bot.message_handler(content_types=['text'])
def get_time_message(message):
    """Обработка сообщений от пользователя на предмет игры в 'время'"""
    time_current_mesage = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
    if valid_time(message.text):
        if time_current_mesage == message.text.strip():
            if temp_moments.get(message.from_user.username) != time_current_mesage:
                score = parse_time(message.text)
                if score:
                    temp_moments[message.from_user.username] = time_current_mesage
                    change_player_score(message.from_user.username, score)
                    gif = open(f'images/congratulations{score}.gif', 'rb')
                    scores = get_player_score(message.from_user.username)
                    mess = f"Поздравляю, {message.from_user.first_name}! Получи {score} {token(scores)}!\nТеперь у вас {scores} {token(scores)}"
                    bot.send_animation(message.chat.id, gif, caption=mess)
            else:
                bot.send_message(message.chat.id, "Ха-Ха! Повторно получить очки не получится!)")
        else:
            bot.send_animation(message.chat.id, open('images/no.gif', 'rb'), caption="Не вышло...")


bot.polling(none_stop=True)
