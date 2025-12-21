import datetime
import os
from time import sleep

import telebot
from dotenv import load_dotenv, find_dotenv
from telebot import types
from telebot.apihelper import ApiTelegramException

from constants import emoji, excluded_markdown, congratulations, censures
from parsers import valid_time, parse_time, tier
from sqltable import (
    get_player_score,
    get_game,
    game_status_change,
    game_status_check,
    change_player_score,
    get_id_chats,
    all_players,
    all_games,
    add_game,
    player_status_change,
    total_players,
    all_games_online,
)
from rick_and_morty_api import RickAndMortyAPI

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv("TELEGRAMM_TOKEN"))
temp_moments = dict()
cur_cheater = None
api_rick = RickAndMortyAPI()


def is_delayed_message(date):
    """Функция для определения, что сообщение является подозрением отложенное (жульничество)"""
    message_time = datetime.datetime.fromtimestamp(date).strftime("%S")
    if int(message_time) < 3:
        return True
    else:
        return False


def final_text(original_text, message, score):
    top_players = all_players(message.chat.id).items()
    sort_top_players = sorted(
        top_players,
        key=lambda x: int(x[1]),
        reverse=True,
    )
    players_scores = []
    for player_name, player_score in sort_top_players:
        players_scores.append(f"{player_name}: {player_score} {emoji[tier(score)]}")
    # отправляем gif анимацию и сообщение
    original_text += (
        f"🤜 <b>РЕЗУЛЬТАТ ИГРЫ 👉{get_game(message.chat.id)[0]}👈</b>\n\n"
        + "\n".join(players_scores)
    )
    return original_text


def check_win_and_end_game(scores, message, score) -> None:
    if scores >= 125:
        mess_win = f"ВООТ ЭТО ДААА, <b>{message.from_user.first_name}</b> 🎉🎉🎉.\n\n" + \
                   f"Вы выиграли игру со счетом <b>{scores}</b> {emoji[tier(scores)]}\n\n"
    with open("images/winner.gif", "rb") as gif_winner:
        bot.send_animation(
            message.chat.id,
            gif_winner,
            caption=final_text(mess_win, message, score),
            parse_mode="HTML",
        )
    mess_loser = (
        f"КОНЕЦ ИГРЫ. <b>{message.from_user.first_name}</b> 🎉🎉🎉.\n\n"
        + f"победил со счетом <b>{scores}</b> {emoji[tier(scores)]}\n\n"
    )

    list_chats = get_id_chats(get_game(message.chat.id)[0])
    list_chats.remove(str(message.chat.id))
    with open("images/loser.gif", "rb") as gif_loser:
        for chat_id in list_chats:
            try:
                sleep(0.3)
                text = final_text(mess_loser, message, score)
                gif_loser.seek(0)
                bot.send_animation(
                    chat_id,
                    gif_loser,
                    caption=text,
                    parse_mode="HTML",
                )
            except ApiTelegramException:
                print(f"Не удалось отправить сообщение в чат {chat_id}")

        game_status_change(message.chat.id)


@bot.message_handler(commands=["time"])
def cur_time(message):
    time_current_message = datetime.datetime.fromtimestamp(message.date).strftime(
        "%H:%M:%S"
    )
    bot.send_message(
        message.chat.id, "Сейчас время: " + time_current_message, parse_mode="HTML"
    )


@bot.message_handler(content_types=["text"])
def who_am_i(message):
    if "кто я" in message.text.lower():
        mess, image = api_rick.get_rundom_character()
        bot.send_photo(
                message.chat.id,
                image,
                caption=mess,
                reply_to_message_id=message.message_id,
            )


@bot.message_handler(commands=["start"])
def start_message(message):
    """Функция для приветствия"""
    mess = """Игра INtime
Правила
Игроки должны написать в сообщении красивое время в это самое время. За попадание в то самое время начисляются очки.
Примеры сообщений:
10:01 - 1 очко - (зеркало)
10:10 - 2 очка - (двойняшки)
11:11 - 3 очка - (забор)
12:34 - 4 очка - (флеш рояль)

Игра продолжается до 125 очков. Кто первый достигнет финиша, выйгрывает игру, после чего она заканчивается.
Все очки игроков ведутся в рамках одной игры и параллельно ведется общая статистика.
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

    bot.send_message(message.chat.id, mess, parse_mode="HTML")


@bot.message_handler(commands=["connect"])
def connect(message):
    """Подключаем новый чат к игре. После команды должно быть имя"""
    command_args = message.text.split(" ")
    if len(command_args) == 2:
        game_name = command_args[1]
        if game_name in all_games_online():
            add_game(message.chat.id, game_name)
            bot.reply_to(
                message,
                f"Вы подключились к игре: <b>{game_name}</b> 🚀",
                parse_mode="HTML",
            )
        else:
            bot.reply_to(message, "В такую игру никто не играет 🤔")
    else:
        bot.reply_to(
            message,
            "Пожалуйста, напишите название игры после команды <b>/connect</b> 🖥️",
            parse_mode="HTML",
        )


@bot.message_handler(commands=["games"])
def games(message):
    """Функция для вывода списка активных игр"""
    mess = (
        "Все активные игры:\n"
        + "🎮 "
        + ("\n🎮 ".join(all_games_online()) or "нет активных игр")
    )
    bot.reply_to(message, mess, parse_mode="HTML")


@bot.message_handler(commands=["startgame"])
def start_game(message):   # TODO везде сменил на HTML
    """Функция для начала игры. После команды должно быть название игры,
    после чего из названия удаляются все символы мешающие MARKDOWNv2"""
    command_args = message.text.split(" ")
    if len(command_args) == 2:
        game_name = command_args[1]
        for letter in game_name:
            if letter in excluded_markdown:
                game_name = game_name.replace(letter, "")
        if game_name not in all_games():
            cur_game = get_game(message.chat.id)
            if not cur_game:
                add_game(message.chat.id, game_name)
                change_player_score(
                    message.chat.id, message.from_user.username, score=0
                )
                bot.reply_to(
                    message,
                    f"Ваша игра: {game_name}, началась 🚀",
                    parse_mode="HTML",
                )
            else:
                bot.reply_to(
                    message,
                    f"Мы уже тут играем. Ваша игра: {cur_game[0]} 🎮",
                    parse_mode="HTML",
                )
        else:
            bot.reply_to(
                message, "Такое название игры уже существует 🤔", parse_mode="HTML"
            )
    else:
        bot.reply_to(
            message,
            "Пожалуйста, напишите название игры после команды /startgame",
            parse_mode="HTML",
        )


@bot.message_handler(commands=["endgame"])
def end_game(message):
    """Функция для завершения игры. Голосуем за завершение. Если трое проголосовали или половина,
    округленная в нижнюю сторону, то заканчиваем игру"""
    game_name, game_status = get_game(message.chat.id)
    if game_status:
        status_of_players = player_status_change(
            game_name, name=message.from_user.username
        )
        mess = f"Ты проголосовал закончить игру: {game_name} 🛑"
        bot.reply_to(message, mess, parse_mode="HTML")
        if (
            -(-len(status_of_players) // 2)
            == len(tuple(filter(lambda x: x[1] is False, status_of_players)))
            or len(tuple(filter(lambda x: x[1] is False, status_of_players))) > 3
        ):
            mess = f"Голосование участников:<b>{game_name}</b>\n\n" + "\n".join(
                [
                    f'{player[0]}: {(player[1] and "В игре ✅" or "хочет закончить 🛑")}'
                    for player in status_of_players
                ]
            )
            mess_end = f"КОНЕЦ ИГРЫ 👉{game_name}👈\n\n{mess}"
            list_chats = get_id_chats(game_name)
            for chat_id in list_chats:
                bot.send_message(chat_id, mess_end, parse_mode="HTML")
            game_status_change(message.chat.id)
    else:
        mess = "🫠 Тут никто не играет. Можете начать новую игру 🚀 или подключиться к одной из актвных игр 🖥️"
        bot.reply_to(message, mess, parse_mode="HTML")


@bot.message_handler(commands=["top"])
def top_players_message(message):
    cur_game = get_game(message.chat.id)
    if cur_game:
        top_players = all_players(message.chat.id).items()
        sort_top_players = sorted(top_players, key=lambda x: int(x[1]), reverse=True)
        scores = []
        for player, score in sort_top_players:
            scores.append(f"{player}: {score} {emoji[tier(score)]}")
        # отправляем gif анимацию и сообщение
        mess = f"🤜 <b>ТОП ИГРОКОВ В 👉{cur_game[0]}👈</b>\n\n" + "\n".join(scores)
        bot.send_animation(
            message.chat.id,
            open("images/top.gif", "rb"),
            caption=mess,
            parse_mode="HTML",
        )
    else:
        bot.reply_to(message, "Тут никто не играет 😔", parse_mode="HTML")


@bot.message_handler(commands=["total"])
def total_players_message(message):
    total = total_players()
    sorted_total = sorted(total.items(), key=lambda x: int(x[1]), reverse=True)
    scores = []
    for player, score in sorted_total:
        scores.append(f"{player}: {score} {emoji[tier(score/10)]}")
    mess = "🤜 <b>ОБЩИЙ СЧЕТ</b>\n\n" + "\n".join(scores)
    with open("images/total.gif", "rb") as gif:
        bot.send_animation(
            message.chat.id,
            gif,
            caption=mess,
            parse_mode="HTML",
        )


@bot.message_handler(content_types=["text"])
def check_time_message(message):
    """Обработка сообщений от пользователя на предмет игры в 'время'"""
    date_current_message = datetime.datetime.fromtimestamp(message.date).strftime(
            "%d:%H:%M"
        )
    if valid_time(message.text) and game_status_check(message.chat.id):
        time_current_message = datetime.datetime.fromtimestamp(message.date).strftime(
            "%H:%M"
        )
        scores = get_player_score(message.chat.id, message.from_user.username)
        if time_current_message == message.text.strip():
            global cur_cheater
            score = parse_time(message.text)
            if is_delayed_message(date=message.date):
                mess = (
                    message.from_user.first_name
                    + ", пожалуйста помедленнее, я записываю. Нажми, чтобы повторить.⬇️"
                )
                markup = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, one_time_keyboard=True
                )
                item1 = types.KeyboardButton(message.text.strip())
                markup.add(item1)
                with open("images/cheater.gif", "rb") as gif:
                    bot.send_animation(
                        message.chat.id,
                        gif,
                        caption=mess,
                        parse_mode="HTML",
                        reply_markup=markup,
                    )
                cur_cheater = message.from_user.username
            elif temp_moments.get(message.from_user.username) != date_current_message and score:
                temp_moments[message.from_user.username] = date_current_message
                change_player_score(message.chat.id, message.from_user.username, score)
                scores = get_player_score(message.chat.id, message.from_user.username)
                gif = open(f"images/tier{tier(scores)}/{score}.gif", "rb")
                mess = (
                    f"<b>{message.from_user.first_name}</b>, {congratulations[score-1]}\n\n"
                    + f"Держи {emoji[tier(scores)]*score}\n\nТвой счет: <b>{scores}</b> {emoji[tier(scores)]}"
                )
                reply_markup = None
                if cur_cheater == message.from_user.username:
                    reply_markup = types.ReplyKeyboardRemove()
                    cur_cheater = None

                bot.send_animation(
                    message.chat.id,
                    gif,
                    caption=mess,
                    parse_mode="HTML",
                    reply_markup=reply_markup,
                )
                check_win_and_end_game(scores, message, score)
            elif temp_moments.get(message.from_user.username) == date_current_message:
                mess = "Ха-Ха! Повторно получить очки не получится! 😀"
                bot.send_message(message.chat.id, mess, parse_mode="HTML")
        else:
            with open(f"images/tier{tier(scores)}/no.gif", "rb") as gif:
                bot.send_animation(
                    message.chat.id,
                    gif,
                    caption="Не вышло...",
                    reply_markup=types.ReplyKeyboardRemove(),
                )
    elif any([(x in message.text.lower()) for x in censures]):
        mess = f"Попрошу Вас не выражаться, {message.from_user.first_name}..."
        with open("images/consored.gif", "rb") as gif:
            bot.send_animation(
                message.chat.id,
                gif,
                caption=mess,
                reply_to_message_id=message.message_id,
            )


if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True, none_stop=True)
