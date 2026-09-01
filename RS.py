# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

import random
import string

RANDOM_STRING_VERSION = "1.0.6"

def RS(type=None, dir=None):
    """
    Функция для генерации строк
    type (str) - Тип генерируемой строки
        ip - генерирует число от 0 до 255
        ping - генерирует число от 0 до 8
        cmd - генерирует команду
        dir - генерируем название каталога
        file - генерируем название файла
        data - генерируем данные для файла
    dir - Каталог для генерируемых файлов
    return - функция возвращает строку
    """
    if type == None:
        # Случайное количество слов (от 2 до 6)
        num_words = random.randint(2, 3)

        words = []
        for _ in range(num_words):
            # Случайная длина слова (от 3 до 10 букв)
            word_length = random.randint(3, 10)

            # Случайный выбор типа форматирования слова
            formatting = random.choice(["lower", "upper", "title", "mixed"])

            # Генерируем случайное слово
            word = "".join(random.choices(string.ascii_letters, k=word_length))

            # Применяем форматирование
            if formatting == "lower":
                word = word.lower()
            elif formatting == "upper":
                word = word.upper()
            elif formatting == "title":
                word = word.capitalize()
            else: # mixed
                word = "".join(random.choice([c.upper(), c.lower()]) for c in word)

            words.append(word)

        # Добавляем пробел
        title = ""
        for i, word in enumerate(words):
            title += word
            if i < len(words) - 1:
                title += " "

        return title
    elif type == "ip":
        return random.randint(1, 256)
    elif type == "ping":
        return random.randint(1, 9)
    elif type == "cmd":
        commands = ["dir", "echo virus", "ipconfig", "ping www.youtube.com", "systeminfo", r"set path=C:\virus.exe", "netstat", "whoami", "date /t", "time /t"]
        n = random.randint(0, 9)
        return commands[n]
    elif type == "dir":
        n = random.randint(4, 12)
        return "".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUWXYZ0123456789") for i in range(n))
    elif type == "file":
        n = random.randint(4, 10)
        i = random.randint(0, 6)
        file_extension = [".txt", ".exe", ".msi", ".dat", ".tmp", ".jpg", ".mkv"]
        return fr'{dir}\{"".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUWXYZ0123456789") for i in range(n))}{file_extension[i]}'
    elif type == "data":
        n = random.randint(256, 2048)
        return "".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUWXYZ0123456789 !@# $%^&*()") for i in range(n))
