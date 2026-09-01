# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

# Логирование ошибок
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
# Интерфейс
import tkinter as tk
from tkinter import ttk, Menu
# Работа с процессами и файлами
import subprocess
import os
import re

from RS import RS
from OF import pac, apply_global_theme, create_menubar
from config import THEME, DEFAULT_THEME, PROGRAM_AUTHENTICATION_CLYTH, CURRENT_LOCALIZATION
from languages import l

RUN_VERSION = "1.1.8 Beta"
RUN_WIDTH_WINDOW = 400
RUN_HEIGHT_WINDOW = 200
RUN_SIZE_WINDOW = f"{RUN_WIDTH_WINDOW}x{RUN_HEIGHT_WINDOW}"

class Run_As_Admin:
    def __init__(self, RUN_GUI):
        self.RUN_GUI = RUN_GUI
        self.RUN_GUI.title(RS())
        self.RUN_GUI.geometry(RUN_SIZE_WINDOW)
        self.RUN_GUI.minsize(RUN_WIDTH_WINDOW, RUN_HEIGHT_WINDOW)

        # Пресеты
        self.presets = [
            {"name": f'---{l("standard")} {l("utilities")}---', "command": ""},
            {"name": l("regedit"), "command": "regedit.exe"},
            {"name": l("taskmgr"), "command": "taskmgr.exe"},
            {"name": l("notepad"), "command": "notepad.exe"},
            {"name": l("explorer"), "command": "explorer.exe"},
            {"name": l("cmd"), "command": "cmd.exe"},
            {"name": l("powershell"), "command": "powershell.exe"},
            {"name": f'---{l("commands")}---', "command": ""},
            {"name": "SFC /SCANNOW", "command": "SFC /SCANNOW"},
            {"name": l("cancel_reboot"), "command": "shutdown /a"},
            {"name": l("reboot_pc"), "command": "shutdown /r"},
            {"name": l("shutdown_pc"), "command": "shutdown /s"},
            {"name": l("end_session"), "command": "shutdown /l"}
        ]

        self.mode = tk.StringVar(value=l("professional"))
        self.current_buttons = []

        self.create_menu()

        self.professional_frame = tk.Frame(RUN_GUI)
        self.professional_frame.pack(fill=tk.BOTH, expand=True)
        self.create_professional_mode()

        self.simplified_frame = tk.Frame(RUN_GUI)
        self.create_simplified_mode()

        # Переключение на профессиональный режим по умолчанию
        self.switch_mode(l("professional"))

        # Привязка события изменения размера окна
        self.RUN_GUI.bind("<Configure>", self.on_window_resize)



    # Создание меню с выбором режима
    def create_menu(self):
        menu_frame = tk.Frame(self.RUN_GUI, height=40)
        menu_frame.pack(side=tk.TOP, fill=tk.X)
        menu_frame.pack_propagate(False)

        label = tk.Label(menu_frame, text=l("mode"))
        label.pack(side=tk.LEFT, padx=10, pady=8)

        mode_combo = ttk.Combobox(
            menu_frame,
            textvariable=self.mode,
            values=[l("professional"), l("simplified")],
            state="readonly",
            width=20
        )
        mode_combo.pack(side=tk.LEFT, padx=5, pady=8)
        mode_combo.bind("<<ComboboxSelected>>", lambda e: self.switch_mode(
            l("professional") if self.mode.get() == l("professional") else l("simplified")
        ))



    def create_professional_mode(self):
        # Поле для ввода команды
        input_frame = tk.Frame(self.professional_frame)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.input_field = tk.Entry(input_frame)
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", lambda e: self.run_command())

        ok_button = tk.Button(
            input_frame,
            text=l("ok"),
            command=self.run_command,
            width=5,
        )
        ok_button.pack(side=tk.LEFT)

        # Меню пресетов
        self.preset_combo = ttk.Combobox(
            self.professional_frame,
            values=[p["name"] for p in self.presets],
            state="readonly",
            height=8
        )
        self.preset_combo.pack(fill=tk.X, padx=5, pady=5)
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_selected)

        # Текстовое поле для отображения ошибок
        log_frame = tk.Frame(self.professional_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(log_frame, text=l("error")).pack(anchor=tk.W)

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(
            log_frame,
            yscrollcommand=scrollbar.set,
            height=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        # Блокируем изменение размера окна в профессиональном режиме
        self.RUN_GUI.resizable(False, False)



    def create_simplified_mode(self):
        self.simplified_frame.pack_propagate(False)

        # Очистка предыдущего интерфейса
        for widget in self.simplified_frame.winfo_children():
            widget.destroy()

        self.current_buttons = []

        # Пропускаем пресеты начинающиеся с "-"
        row = 0
        col = 0
        for preset in self.presets:
            if preset["name"].startswith("-"):
                continue
                
            btn = tk.Button(
                self.simplified_frame,
                text=preset["name"],
                command=lambda cmd=preset["command"]: self.run_command_from_button(cmd),
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            self.current_buttons.append(btn)
            
            col += 1
            if col > 1:
                col = 0
                row += 1

        for i in range(row + 1):
            self.simplified_frame.grid_rowconfigure(i, weight=1)
        self.simplified_frame.grid_columnconfigure(0, weight=1)
        self.simplified_frame.grid_columnconfigure(1, weight=1)



    # Переключаем режим
    def switch_mode(self, mode):
        if mode == l("professional"):
            self.professional_frame.pack(fill=tk.BOTH, expand=True)
            self.simplified_frame.pack_forget()
            self.RUN_GUI.resizable(False, False)
            self.RUN_GUI.geometry(RUN_SIZE_WINDOW)
        else:
            self.RUN_GUI.minsize(600, 275)
            # self.RUN_GUI.geometry(run_)
            self.professional_frame.pack_forget()
            self.simplified_frame.pack(fill=tk.BOTH, expand=True)
            self.RUN_GUI.resizable(True, True)



    def on_preset_selected(self, event=None):
        selected = self.preset_combo.get()
        for preset in self.presets:
            if preset["name"] == selected:
                self.input_field.delete(0, tk.END)
                self.input_field.insert(0, preset["command"])
                break



    # Проверяем является ли текст командой или путём к файлу
    def is_command_or_dir(self, text):
        # Если начинается с буквы и двоеточия, то это путь
        if re.match(r"^[A-Za-z]:", text):
            return False
        return True



    # Выполняем команду или запускаем файл
    def run_command(self):
        command = self.input_field.get().strip()
        if command == "" or command == None:
            return

        try:
            if self.is_command_or_dir(command):
                # Это команда
                subprocess.Popen(command, shell=True)
                logger.info(f'Run - {l("launch")} {l("commands")}: {command}')
            else:
                # Это путь к файлу
                if os.path.exists(command):
                    os.startfile(command)
                    logger.info(f'Run - {l("launch")} {l("file2")}: {command}')
                else:
                    comment = f'Run - {l("not_found")} {l("file")}: {command}'
                    logger.error(comment)
                    self.log(comment)
        except Exception as e:
            comment = f'Run - {l("start_error")} {l("file2")}'
            logger.error(comment)
            self.log(comment, e)



    # Выполняем команду кнопки
    def run_command_from_button(self, command):
        if command == "":
            return
        try:
            subprocess.Popen(command, shell=True)
        except Exception as e:
            logger.exception(l("start_command_error"))
            self.log(l("start_command_error"))



    def on_window_resize(self, event=None):
        if self.mode.get() == l("simplified"):
            # Динамическое изменение размера шрифта в зависимости от размера окна
            width = self.RUN_GUI.winfo_width()
            height = self.RUN_GUI.winfo_height()

            if width > 0 and height > 0:
                font_size = max(14, min(width, height) // 32)
                for btn in self.current_buttons:
                    btn.config(font=("Default", font_size, "bold"))



    # Отображение ошибок в интерфейсе
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)


def Run(current_theme="dark", DEBUG_MODE=False):
    RUN_GUI = tk.Tk()
    apply_global_theme(RUN_GUI, current_theme)
    Run_As_Admin(RUN_GUI)

    create_menubar(RUN_GUI, False, DEBUG_MODE=DEBUG_MODE)

    RUN_GUI.mainloop()

if __name__ == "__main__":
    current_theme = THEME[DEFAULT_THEME]
    Run(current_theme)
