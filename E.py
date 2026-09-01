# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

# Интерфейс
from tkinter import messagebox, simpledialog
import tkinter as tk
# Логирование Ошибок
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
# Капча
import random
import os

from RS import RS
from OF import apply_global_theme, run_component
from config import PROGRAM_AUTHENTICATION_CLYTH
from languages import l

EXIT_VERSION = "1.1.10 Beta"
DYRACHOK_PATH = r"C:\ProgramData\dyrachok.txt"

# @logger.catch
def check_access_file():
    try:
        with open(DYRACHOK_PATH, "r") as f:
            content = f.read()
        if "debil" in content:
            logger.critical(f'E - {l("dyrachok_test_log_text")}.')
            messagebox.showwarning(RS(), l("dyrachok_test_text"))
            return False
        else:
            # logger.success("E - Проверка на дурочка прошла успешно.")
            return True
    except FileNotFoundError:
        return True



# @logger.catch
def tiktok_question():
    if messagebox.askyesno(RS(), l("watch_tiktok?")):
        try:
            with open(DYRACHOK_PATH, "w") as f:
                f.write("debil")
            messagebox.showinfo(RS(), l("dyrachok_test_text"))
        except Exception as e:
            comment = f'E - {l("exit_error")}'
            logger.exception(comment)
            messagebox.showerror(RS(), f"{comment}\n{e}")
            return False
    else:
        logger.info(l("exit_program"))
        os._exit(0)



def bad_capcha():
    messagebox.showerror(RS(), l("bad_capcha"))



def math_window():
    n = random.randint(256, 1024)
    number_input = tk.simpledialog.askinteger(RS(), f'{l("enter_result_example")}: √({n} * {n})')

    if number_input == n:
        # logger.info("E - ввод примера верен.")
        tiktok_question()
    else:
        logger.critical(f'E - {l("bad_result_example")}.')
        bad_capcha()



def captcha_window():
    n = random.randint(256, 1024)
    captcha_input = tk.simpledialog.askinteger(RS(), f'{l("enter_number")}: {n}')

    if captcha_input == n:
        # logger.info("E - ввод числа верен.")
        math_window()
    else:
        logger.critical(f'E - {l("bad_enter_number")}')
        bad_capcha()



def E():
    """Выход из программы через несколько капч"""
    try:
        # Это костыль, чтобы тема применялась к диалоговым окнам
        root = tk.Tk()
        root.title(RS())
        from config import THEME, DEFAULT_THEME
        current_theme = THEME[DEFAULT_THEME]
        from OF import apply_global_theme
        apply_global_theme(root, current_theme)
        root.withdraw()
        if check_access_file():
            if messagebox.askyesno(RS(), f'{l("pac")} - {PROGRAM_AUTHENTICATION_CLYTH}\n\n{l("want_exit?")}'):
                logger.info(f'E - {l("attempting_to_exit")}.')
                captcha_window()
            else:
                logger.info(f'E - {l("cancel_exit")}.')
        root.mainloop()
    except:
        logger.exception(f'E - {l("e_critical_error")}')

if __name__ == "__main__":
    E()
