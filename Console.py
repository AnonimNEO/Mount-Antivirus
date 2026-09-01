# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

import tkinter as tk
from tkinter import scrolledtext, messagebox
from io import StringIO
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
import random
import sys

from config import PROGRAM_AUTHENTICATION_CLYTH
from OF import create_menubar
from languages import l
from RS import RS
import config

CROWBAR_CONSOLE_VERSION = "0.1.9 Pre-Alpha"

class CrowbarConsole:
    """Консоль разработчика (python консоль вместе с доступом к функциям программы)"""
    def __init__(self, globals_dict=None, DEBUG_MODE=False):
        self.globals_dict = globals_dict if globals_dict else {}
        self.CC_GUI = None
        self.output_text = None
        self.input_entry = None

    def create_console(self):
        self.CC_GUI = tk.Tk()
        self.CC_GUI.title(RS())
        self.CC_GUI.geometry("650x400")

        # Вывод консоли
        self.output_text = scrolledtext.ScrolledText(
            self.CC_GUI,
            wrap=tk.WORD,
            bg="# 1e1e1e",
            fg="# 00ff00",
            font=("Default", 10),
            height=20
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output_text.insert(tk.END, f'=== {l("crowbar_console")} {crowbar_console_version} ===\n')
        self.output_text.insert(tk.END, f'{l("pac")} - {PROGRAM_AUTHENTICATION_CLYTH}\n')
        self.output_text.insert(tk.END, l("crowbar_console_text"))

        self.output_text.config(state=tk.DISABLED)

        # Поле ввода
        input_frame = tk.Frame(self.CC_GUI)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(input_frame, text=">>>", fg="# 00ff00", bg="black").pack(side=tk.LEFT, padx=5)

        self.input_entry = tk.Entry(
            input_frame,
            font=("Default", 10),
            bg="# 1e1e1e",
            fg="# 00ff00",
            insertbackground="black"
        )
        self.input_entry.pack(fill=tk.X, expand=True, padx=5)
        self.input_entry.bind("<Return>", self.execute_command)
        self.input_entry.focus()

        create_menubar(self.CC_GUI, False, None, DEBUG_MODE=DEBUG_MODE)

        self.CC_GUI.mainloop()

    def execute_command(self, event=None):
        command = self.input_entry.get()
        self.input_entry.delete(0, tk.END)

        if not command.strip():
            return

        logger.info(f'Console - {l("attempt_command")}: {command}')

        if any(x in command for x in ("exit", "quit", "os._exit")):
            self.output_text.config(state=tk.NORMAL)
            comment = f'{l("exit_with_console_text")}\n'
            logger.info(f"Console - {comment}")
            self.output_text.insert(tk.END, comment)
            self.output_text.config(state=tk.DISABLED)
            return

        # Вывод команды
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"> {command}\n")
        self.output_text.config(state=tk.DISABLED)

        try:
            # Перенаправляем stdout для захвата print
            old_stdout = sys.stdout
            sys.stdout = StringIO()

            # Выполняем команду
            exec(command, self.globals_dict)

            # Получаем вывод
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout

            if output:
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END, output)
                self.output_text.config(state=tk.DISABLED)

        except SyntaxError as e:
            self.output_text.config(state=tk.NORMAL)
            comment = f"SyntaxError: {e}\n"
            logger.error(f"Console - {comment[:-5]}\n{e}")
            self.output_text.insert(tk.END, comment)
            self.output_text.config(state=tk.DISABLED)

        except Exception as e:
            logger.exception(f'Console - {l("error")}')
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"Error: {type(e).__name__}: {e}\n")
            self.output_text.config(state=tk.DISABLED)

        finally:
            sys.stdout = old_stdout

        # Прокручиваем в конец
        self.output_text.config(state=tk.NORMAL)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

def open_console(globals_dict=None, DEBUG_MODE=False):
    """Запуск консоли разработчика через капчу"""
    n = random.randint(128, 2048)
    captcha_input = tk.simpledialog.askinteger(RS(), f'{l("enter_number")}: {n}')

    if captcha_input == n:
        pass
    else:
        messagebox.showerror(RS(), l("bad_password_for_console"))
        return
    console = CrowbarConsole(globals_dict, DEBUG_MODE=DEBUG_MODE)
    console.create_console()
