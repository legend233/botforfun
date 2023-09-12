import telebot
from dotenv import load_dotenv, find_dotenv
import os
from parsers import *
import datetime
from sqltable import *

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TELEGRAMM_TOKEN'))
DEV_MODE = os.getenv('DEV_MODE')

temp_moments = dict()
emoji = ["🪙", "💵", "💰", "💎","👑"]
congratulations = ["Успел 😉", "Так держать🤪", "Ай молодец 😎", "Так могут не только лишь все 🥊"]
excluded_markdown = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

def tier(score):
    if score < 25:
        return 0
    elif score < 50:
        return 1
    elif score < 75:
        return 2
    elif score < 100:
        return 3
    else:
        return 4


@bot.message_handler(commands=['time'])
def cur_time(message):
    """Функция для теста текущего времени бота"""
    time_current_mesage = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
    bot.send_message(message.chat.id, "Сейчас время: "+time_current_mesage, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start_message(message):
    mess = """Игра INtime
Правила
Игроки должны написать в сообщении красивое время в это самое время. За попадание в то самое время начисляются очки.
Примеры сообщений:
10:01 - 1 очко - (зеркало)
10:10 - 2 очка - (двойняшки)
11:11 - 3 очка - (забор)
12:34 - 4 очка - (флеш рояль)

Игра продолжается до 125 очков. Кто первый достигнет финиша, выйгрывает игру, после чего она заканчивается. Все очки игроков ведуться в рамках одной игры и параллельно ведеться общая статистика.
Есть градации уровней игры. Уровень сменяется, когда игрок набирает 25, 50, 75, 100, 125 очков.
Список команд:
/startgame "имя игры" - начать игру
/endgame - завершить игру.
(Необходимо более трех игроков или половина игроков в игре, которые хотят выйти)
/games - список активных игр
/connect "имя игры" - подключиться к игре
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
            add_game(message.chat.id, game_name)
            bot.reply_to(message, f"Вы подключились к игре: *{game_name}* 🚀", parse_mode="Markdown")
        else:
            bot.reply_to(message, "В такую игру никто не играет 🤔")
    else:
        bot.reply_to(message, "Пожалуйста, напишите название игры после команды */connect* 🖥️", parse_mode="Markdown")

@bot.message_handler(commands=['games'])
def games(message):
    mess = "Все активные игры:\n" + "🎮 "+('\n🎮 '.join(all_games_online()) or "нет активных игр")
    bot.reply_to(message, mess, parse_mode="Markdown")


@bot.message_handler(commands=['startgame'])
def start_game(message):
    command_args = message.text.split(' ')
    if len(command_args) == 2:
        game_name = command_args[1]
        for letter in game_name:
            if letter in excluded_markdown:
                game_name = game_name.replace(letter, "")
        if game_name not in all_games():
            cur_game = get_game(message.chat.id)
            if not cur_game:
                add_game(message.chat.id, game_name)
                change_player_score(message.chat.id, message.from_user.username, score=0)
                bot.reply_to(message, f"Ваша игра: {game_name}, началась 🚀", parse_mode="Markdown")
            else:
                bot.reply_to(message, f"Мы уже тут играем. Ваша игра: {cur_game[0]} 🎮", parse_mode="Markdown")
        else:
            bot.reply_to(message, "Такое название игры уже существует 🤔", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Пожалуйста, напишите название игры после команды /startgame", parse_mode="Markdown")

@bot.message_handler(commands=['endgame'])
def end_game(message):
    game_name, game_status = get_game(message.chat.id)
    if game_status:
        status_of_players = player_status_change(game_name, name=message.from_user.username)
        mess = f"Ты проголосовал закончить игру: {game_name} 🛑"
        bot.reply_to(message, mess, parse_mode="Markdown")
        if -(-len(status_of_players)// 2) == len(tuple(filter(lambda x: x[1] == False, status_of_players))) or len(tuple(filter(lambda x: x[1] == False, status_of_players))) > 3:
            gif = open(f'images/stopgame.gif', 'rb')
            mess = f"Голосование участников:*{game_name}*\n\n" + "\n".join([f'{player[0]}: {(player[1] and "В игре ✅" or "хочет закончить 🛑")}' for player in status_of_players])
            mess_end = f"КОНЕЦ ИГРЫ 👉{game_name}👈\n\n{mess}"
            list_chats = get_id_chats(game_name)
            for chat_id in list_chats:
                bot.send_message(chat_id, mess_end, parse_mode="Markdown")
            game_status_change(message.chat.id)
    else:
        bot.reply_to(message, "🫠 Тут никто не играет. Можете начать новую игру 🚀 или подключиться к одной из актвных игр 🖥️", parse_mode="Markdown")


@bot.message_handler(commands=['top'])
def top_players_message(message):
    cur_game = get_game(message.chat.id)
    if cur_game:
        top_players = all_players(message.chat.id).items()
        sort_top_players = sorted(top_players, key=lambda x: int(x[1]), reverse=True)
        scores = []
        for player, score in sort_top_players:
            scores.append(f"{player}: {score} {emoji[tier(score)]}")
        # отправляем gif анимацию и сообщение
        mess = f"🤜 *ТОП ИГРОКОВ В 👉{cur_game[0]}👈*\n\n" + "\n".join(scores)
        bot.send_animation(message.chat.id, open('images/top.gif', 'rb'), caption=mess, parse_mode="MarkdownV2")
    else:
        bot.reply_to(message, "Тут никто не играет 😔", parse_mode="Markdown")

@bot.message_handler(commands=['total'])
def total_players_message(message):
    total = total_players()
    sorted_total = sorted(total.items(), key=lambda x: int(x[1]), reverse=True)
    scores = []
    for player, score in sorted_total:
        scores.append(f"{player}: {score} {emoji[tier(score/10)]}")
    mess = f"🤜 *ОБЩИЙ СЧЕТ*\n\n" + "\n".join(scores)
    bot.send_animation(message.chat.id, open('images/total.gif', 'rb'), caption=mess, parse_mode="MarkdownV2")


@bot.message_handler(content_types=['text'])
def get_time_message(message):
    """Обработка сообщений от пользователя на предмет игры в 'время'"""
    if game_status_check(message.chat.id):
        time_current_mesage = datetime.datetime.fromtimestamp(message.date).strftime('%H:%M')
        if valid_time(message.text):
            scores = get_player_score(message.chat.id, message.from_user.username)
            if time_current_mesage == message.text.strip():
                if temp_moments.get(message.from_user.username) != time_current_mesage:
                    score = parse_time(message.text)
                    if score:
                        temp_moments[message.from_user.username] = time_current_mesage
                        change_player_score(message.chat.id, message.from_user.username, score)
                        scores = get_player_score(message.chat.id, message.from_user.username)
                        gif = open(f'images/tier{tier(scores)}/{score}.gif', 'rb')
                        mess = f"*{message.from_user.first_name}*, {congratulations[score-1]}\n\nДержи {emoji[tier(scores)]*score}\n\nТвой счет: *{scores}* {emoji[tier(scores)]}"
                        bot.send_animation(message.chat.id, gif, caption=mess, parse_mode="MarkdownV2")
                        if scores >= 125:
                            gif_winner = open(f'images/winner.gif', 'rb')
                            gif_loser = open(f'images/loser.gif', 'rb')
                            mess_win = f"ВООТ ЭТО ДААА, *{message.from_user.first_name}* 🎉🎉🎉.\n\nВы выиграли игру со счетом *{scores}* {emoji[tier(scores)]}\n\n"
                            game_name = get_game(message.chat.id)[0]
                            def final_text(text):
                                # ToDo: внимание!!! дубляж кода!!!
                                top_players = all_players(message.chat.id).items()
                                sort_top_players = sorted(top_players, key=lambda x: int(x[1]), reverse=True)
                                scores = []
                                for player, score in sort_top_players:
                                    scores.append(f"{player}: {score} {emoji[tier(score)]}")
                                # отправляем gif анимацию и сообщение
                                text += f"🤜 *РЕЗУЛЬТАТ ИГРЫ 👉{get_game(message.chat.id)[0]}👈*\n\n" + "\n".join(scores)
                                return text
                            
                            bot.send_animation(message.chat.id, gif_winner, caption=final_text(mess_win), parse_mode="Markdown")
                            mess_loser = f"КОНЕЦ ИГРЫ. *{message.from_user.first_name}* победил со счетом *{scores}* {emoji[tier(scores)]}\n\n"
                            list_chats = get_id_chats(get_game(message.chat.id)[0])
                            list_chats.remove(str(message.chat.id))
                            for chat_id in list_chats:
                                text = final_text(mess_loser)
                                bot.send_animation(chat_id, gif_loser, caption=text, parse_mode="Markdown")
                            

                            game_status_change(message.chat.id)
                else:
                    bot.send_message(message.chat.id, "Ха-Ха! Повторно получить очки не получится!)", parse_mode="Markdown")
            else:
                bot.send_animation(message.chat.id, open(f'images/tier{tier(scores)}/no.gif', 'rb'), caption="Не вышло...")

        elif any([x in message.text.lower() for x in ["бля", "блия", "биля", "сука", "пизд", "пздц", "хуй", "ахуе", "чмо", "пизда", "пидор", "фак", "fuck", "долбоеб", "долбаеб", "залуп", "ебал"]]):
            mess = f"Попрошу Вас не выражаться, {message.from_user.first_name}..."
            bot.send_animation(message.chat.id, open('images/consored.gif', 'rb'), caption=mess, reply_to_message_id=message.message_id)

bot.polling(none_stop=True)
