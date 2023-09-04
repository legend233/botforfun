import telebot
from dotenv import load_dotenv, find_dotenv
import os
from parsers import *
import datetime
from sqltable import *

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TELEGRAMM_TOKEN'))

temp_moments = dict()
emoji = ["💰", "💶", "🏆", "💎","👑"]

def tier(score):
    if score < 50:
        return 0
    elif score < 75:
        return 1
    elif score < 100:
        return 2
    elif score < 125:
        return 3
    else:
        return 4


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
        if score >= 150:
            scores.append(f"{player}: {score} {emoji[tier(score)]} Разогнался!")
        else:
            scores.append(f"{player}: {score} {emoji[tier(score)]}")
    # отправляем gif анимацию и сообщение
    bot.send_animation(message.chat.id, open('images/top.gif', 'rb'), caption="\n".join(scores))


@bot.message_handler(content_types=['text'])
def get_time_message(message):
    """Обработка сообщений от пользователя на предмет игры в 'время'"""
    time_current_mesage = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
    if valid_time(message.text):
        scores = get_player_score(message.from_user.username)
        if time_current_mesage == message.text.strip():
            if temp_moments.get(message.from_user.username) != time_current_mesage:
                score = parse_time(message.text)
                if score:
                    temp_moments[message.from_user.username] = time_current_mesage
                    change_player_score(message.from_user.username, score)
                    scores = get_player_score(message.from_user.username)
                    gif = open(f'images/tier{tier(scores)}/{score}.gif', 'rb')
                    mess = f"Поздравляю, {message.from_user.first_name}! Получи {score} {emoji[tier(scores)]}!\nТеперь у вас {scores} {emoji[tier(scores)]}"
                    bot.send_animation(message.chat.id, gif, caption=mess)
            else:
                bot.send_message(message.chat.id, "Ха-Ха! Повторно получить очки не получится!)")
        else:
            bot.send_animation(message.chat.id, open(f'images/tier{tier(scores)}/no.gif', 'rb'), caption="Не вышло...")

    elif any([x in message.text.lower() for x in ["бля", "сука", "пизд", "пздц", "хуй", "ахуе", "чмо", "пизда", "пидор", "фак", "fuck", "долбоеб", "долбаеб", "залуп"]]):
        mess = f"Попрошу Вас не выражаться, {message.from_user.first_name}..."
        bot.send_animation(message.chat.id, open('images/consored.gif', 'rb'), caption=mess, reply_to_message_id=message.message_id)

bot.polling(none_stop=True)
