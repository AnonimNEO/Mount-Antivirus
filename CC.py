# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

# Обучение
from tkinter import messagebox
# Логирование Ошибок
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
import datetime
# Работа с ОС и файлами
import getpass
import shutil
import os

from languages import l
from OF import get_user_name, get_current_disc
from RS import RS
from config import LOG_PATH, CLEAR_TEMP_LOG

#global log_path, clear_temp_log
CLEAR_CACHE_VERSION = "0.7.9 Beta"

# @logger.catch
def CC(RUN_IN_RECOVERY):
    """Очистка кэша (%Temp%)"""
    try:
        logger.info(f'CC - {l("start_clean")}...')
        # Получаем имя пользователя
        username = get_user_name()
        if RUN_IN_RECOVERY:
            current_disc = get_current_disc()
        else:
            current_disc = "C:\\"
        temp_path = f"{current_disc}\\Users\\{username}\\AppData\\Local\\Temp\\"

        # Переменные для логирования
        files_not_deleted = []
        files_deleted = []

        # Проходим по содержимому папки Temp
        for item in os.listdir(temp_path):
            item_path = os.path.join(temp_path, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    files_deleted.append(item)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    files_deleted.append(item)
            except:
                files_not_deleted.append(item)
                #logger.exception(f"CC - {l("file_delete_error")} {l("from")} %Temp% - {item}")

        # Получаем текущее время и дату для имени лог-файла
        current_time = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        log_filename = f"{LOG_PATH}\\{CLEAR_TEMP_LOG}_{current_time}.txt"
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        with open(log_filename, "w") as log_file:
            log_file.write(f'{l("delete_files_error")}:\n')
            for file in files_not_deleted:
                log_file.write(f"{file}\n")
            log_file.write(f'\n{l("delete_files_success")}:\n')
            for file in files_deleted:
                log_file.write(f"{file}\n")

        cc_log_text = f'CC - {l("cc_log_dir")} - {LOG_PATH}\\{log_filename}'
        logger.info(cc_log_text)
        messagebox.showinfo(RS(), cc_log_text)

    except:
        logger.exception(l("cc_critical_error"))

if __name__ == "__main__":
    CC(False)
