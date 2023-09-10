import telebot
from dotenv import load_dotenv, find_dotenv
import os
from parsers import *
import datetime
from sqltable import *

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TELEGRAMM_TOKEN'))

temp_moments = dict()
emoji = ["🪙", "💵", "💰", "💎","👑"]

def tier(score):
    if score < 25:
        return 0
    elif score < 50:
        return 1
    elif score < 75:
        return 2
    elif score < 100:
        return 3
    elif score < 125
        return 4
    else:
        return 5


@bot.message_handler(commands=['time'])
def cur_time(message):
    """Функция для теста текущего времени бота"""
    time_current_mesage = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
    bot.send_message(message.chat.id, "Сейчас время: "+time_current_mesage, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start_message(message):
    mess = """Правила
Игроки должны написать в сообщении красивое время в это самое время. За попадание в то самое время начисляются очки.
Примеры сообщений:
10:01 - 1 очко - (зеркало)
10:10 - 2 очка - (двойняшки)
11:11 - 3 очка - (забор)
12:34 - 4 очка - (флеш рояль)

Игра продолжается до 125 очков. Кто первый достигнет финиша, выйгрывает игру, после чего она заканчивается. Все очки игроков ведуться в рабках одной игры и параллельно ведеться общая статистика.
Есть градации уровней игры. Уровень сменяется, когда игрок набирает 25, 50, 75, 100, 125 очков.
Список команд:
/startgame "имя игры" - начать игру
/endgame "имя игры"  - завершить игру.
(Необходимо более трех игроков или половина игроков в игре, которые хотят выйти)
/top - показать топ игроков текущей игры
/total - показать общую статистику игрокам
/start - помощь"""

    bot.send_message(message.chat.id, mess, parse_mode="Markdown")

@bot.message_handler(commands=['connect'])
def connect(message):
    command_args = message.text.split(' ')
    if len(command_args) == 2:
        game_name = command_args[1]
        if game_name in all_games_online():
            print(game_name)
            add_game(message.chat.id, game_name)
            bot.reply_to(message, f"Вы подключились к игре: *{game_name}*, началась!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "В такую игру никто не играет!")
    else:
        bot.reply_to(message, "Пожалуйста, напишите название игры после команды */connect*", parse_mode="Markdown")

@bot.message_handler(commands=['startgame'])
def start_game(message):
    command_args = message.text.split(' ')
    if len(command_args) == 2:
        game_name = command_args[1]
        if game_name not in all_games():
            cur_game = get_game(message.chat.id)
            if not cur_game:
                add_game(message.chat.id, game_name)
                change_player_score(message.chat.id, message.from_user.username, score=0)
                bot.reply_to(message, f"Ваша игра: {game_name}, началась!", parse_mode="Markdown")
            else:
                bot.reply_to(message, f"Мы уже тут играем! Ваша игра: {cur_game[0]}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "Такое название игры уже существует!", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Пожалуйста, напишите название игры после команды /startgame", parse_mode="Markdown")

@bot.message_handler(commands=['endgame'])
def end_game(message):
    game_name, game_status = get_game(message.chat.id)
    if game_status:
        status_of_players = player_status_change(game_name, name=message.from_user.username)
        mess = f"Голосование участников игры:\n{game_name}\n" + "\n".join([f'{player[0]}: {(player[1] and "В игре ✅" or "хочет закончить 🛑")}' for player in status_of_players])
        bot.reply_to(message, mess, parse_mode="Markdown")
        if -(-len(status_of_players)// 2) == len(tuple(filter(lambda x: x[1] == False, status_of_players))) or len(tuple(filter(lambda x: x[1] == False, status_of_players))) > 3:
            game_status_change(game_name)
            bot.reply_to(message, f"Игра {game_name} окончена!", parse_mode="Markdown")
    else:
        bot.reply_to(message, "В такую игру никто не играет!", parse_mode="Markdown")


@bot.message_handler(commands=['top'])
def top_players_message(message):
    if get_game(message.chat.id):
        top_players = all_players(message.chat.id).items()
        sort_top_players = sorted(top_players, key=lambda x: int(x[1]), reverse=True)
        scores = []
        for player, score in sort_top_players:
            scores.append(f"{player}: {score} {emoji[tier(score)]}")
        # отправляем gif анимацию и сообщение
        mess = f"➡ **{get_game(message.chat.id)[0]}**\n" + "\n".join(scores)
        bot.send_animation(message.chat.id, open('images/top.gif', 'rb'), caption=mess, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Тут никто не играет 😔", parse_mode="Markdown")

@bot.message_handler(commands=['total'])
def total_players_message(message):
    total = total_players()
    sorted_total = sorted(total.items(), key=lambda x: int(x[1]), reverse=True)
    scores = []
    for player, score in sorted_total:
        scores.append(f"{player}: {score} {emoji[tier(score/10)]}")
    
    bot.send_animation(message.chat.id, open('images/total.gif', 'rb'), caption="\n".join(scores), parse_mode="Markdown")


@bot.message_handler(content_types=['text'])
def get_time_message(message):
    """Обработка сообщений от пользователя на предмет игры в 'время'"""
    if game_status_check(message.chat.id):
        time_current_mesage = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
        if valid_time(message.text):
            scores = get_player_score(message.chat.id, message.from_user.username)
            if time_current_mesage == message.text.strip() or DEV_MODE:
                if temp_moments.get(message.from_user.username) != time_current_mesage:
                    score = parse_time(message.text)
                    if score:
                        temp_moments[message.from_user.username] = time_current_mesage
                        change_player_score(message.chat.id, message.from_user.username, score)
                        scores = get_player_score(message.chat.id, message.from_user.username)
                        gif = open(f'images/tier{tier(scores)}/{score}.gif', 'rb')
                        mess = f"Поздравляю, {message.from_user.first_name}! Получи {score} {emoji[tier(scores)]}!\nТеперь у вас {scores} {emoji[tier(scores)]}"
                        bot.send_animation(message.chat.id, gif, caption=mess, parse_mode="Markdown")
                        if scores >= 125:
                            gif = open(f'images/winner.gif', 'rb')
                            bot.send_animation(message.chat.id, gif, caption=mess, parse_mode="Markdown")
                            game_status_change(message.chat.id)
                else:
                    bot.send_message(message.chat.id, "Ха-Ха! Повторно получить очки не получится!)", parse_mode="Markdown")
            else:
                bot.send_animation(message.chat.id, open(f'images/tier{tier(scores)}/no.gif', 'rb'), caption="Не вышло...")

        elif any([x in message.text.lower() for x in ["бля", "блия", "биля", "сука", "пизд", "пздц", "хуй", "ахуе", "чмо", "пизда", "пидор", "фак", "fuck", "долбоеб", "долбаеб", "залуп"]]):
            mess = f"Попрошу Вас не выражаться, {message.from_user.first_name}..."
            bot.send_animation(message.chat.id, open('images/consored.gif', 'rb'), caption=mess, reply_to_message_id=message.message_id)

bot.polling(none_stop=True)
