"""Основные функции для парсинга сообщений.
10:01 - 1 очко (симетрия)
10:10 - 2 очка (зеркало)
11:11 - 3 очка (забор)
12:34 - 4 очка (флеш рояль)
"""
import re


def valid_time(sample_text: str) -> bool:
    """Функция проверяет корректность формата написанного времени."""
    s = re.fullmatch(r"\d\d:\d\d", sample_text.strip())
    return True if s else False


def parse_time(sample_text: str) -> int:
    """Функция парсит сообщение и возвращает количество очков(результат)"""
    text = sample_text.strip()
    clear_text = text.split(":")
    if len(set(text.replace(":", ""))) == 1:
        result = 3
    elif clear_text[0] == clear_text[1]:
        result = 2
    elif clear_text[0] == clear_text[1][::-1]:
        result = 1
    elif text.replace(":", "") in ("0123", "1234", "2345"):
        result = 4
    else:
        result = 0
    return result
