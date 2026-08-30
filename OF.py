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
from tkinter import ttk, messagebox, filedialog, simpledialog, Menu, scrolledtext
import tkinter as tk
from tkinter.messagebox import askyesno
# Работа с процессами
import subprocess
# Работа с потоками и процессами
import multiprocessing
import threading
# Работа с реестром
import winreg
# Работа с файлами и ОС
import sys
import os
from io import BytesIO
from time import time
from collections import deque
import random
import webbrowser

# from OBPC import OBPC
try:
    from AES import AES
except:
    def AES(a=None, b=None, c=None):
        return a
from RS import RS
from languages import l
from config import ENCRYPT_LOGS, PROGRAM_AUTHENTICATION_CLYTH, LOG_PATH, T_LOG_TXT, THEME

global load_bush
OTHER_FUNCTION_VERSION = "0.14.9 Beta"

# Глобальные имена загруженных кустов
loaded_hive_names = {"SYSTEM": "Offline_SYSTEM", "SOFTWARE": "Offline_SOFTWARE", "USER": "Offline_USER"}

# Глобальные имена для загрузки кустов
HIVE_MAP = {"SYSTEM": "Offline_SYSTEM", "SOFTWARE": "Offline_SOFTWARE", "USER": "Offline_USER"}

# Список для отслеживания загруженных кустов
active_loaded_hives = []

# Логирование Ошибок
from loguru import logger as l_logger

# Логирование с шифрованием
if ENCRYPT_LOGS:
    class Logger:
        def debug(self, message):
            l_logger.debug(AES(message, clyth))

        def info(self, message):
            l_logger.info(AES(message, clyth))

        def warning(self, message):
            l_logger.warning(AES(message, clyth))

        def error(self, message):
            l_logger.error(AES(message, clyth))

        def critical(self, message):
            l_logger.critical(AES(message, clyth))

        def success(self, message):
            l_logger.success(AES(message, clyth))

        def exception(self, message):
            l_logger.exception(AES(message, clyth))

        def catch(self, *args, **kwargs):
            pass

        def add(self, *args, **kwargs):
            l_logger.add(f"{LOG_PATH}\\{T_LOH_TXT}", format="{time} {level} {message}", rotation="10 MB", compression="zip")
else:
    #  Создаём класс-обёртку для l_logger, чтобы он был вызываемым
    class Logger:
        def __init__(self):
            self._logger = l_logger
        
        def debug(self, message):
            self._logger.debug(message)

        def info(self, message):
            self._logger.info(message)

        def warning(self, message):
            self._logger.warning(message)

        def error(self, message):
            self._logger.error(message)

        def critical(self, message):
            self._logger.critical(message)

        def success(self, message):
            self._logger.success(message)

        def exception(self, message):
            self._logger.exception(message)

        def catch(self, *args, **kwargs):
            pass

        def add(self, *args, **kwargs):
            self._logger.add(f'{LOG_PATH}\\{T_LOG_TXT}', format="{time} {level} {message}", rotation="10 MB", compression="zip")

try:
    if encrypt_logs:
        logger = Logger()
    else:
        logger = l_logger
except:
    logger = l_logger

# Заглушка, библиотеки psutil которая всегда возвращает False/None.
class Psutil:
    """
    Заглушка библиотеки psutil которая всегда возвращает False/None
    используйте её когда RUN_IN_RECOVERY = True
    """
    def cpu_percent(self, *args, **kwargs):
        return 0.0

    def virtual_memory(self, *args, **kwargs):
        class MemStub:
            percent = 0.0
            total = 1024 * 1024 # Имитируем 1МБ ОЗУ, чтобы не падал LP.py

        return MemStub()

    def disk_usage(self, *args, **kwargs):
        class DiskStub:
            percent = 0.0

        return DiskStub()

    # Добавлен метод для возврата пустого списка дисков
    def disk_partitions(self, *args, **kwargs):
        return []

    # Заглушка для всех остальных методов, чтобы не вызывать ошибку AttributeError, это поможет устранить только проблему AttributeError.
    def __getattr__(self, name):
        if name in ["sensors_temperatures", "net_io_counters", "process_iter"]:
            return lambda *args, **kwargs: None
        return lambda *args, **kwargs: False



def pac():
    messagebox.showinfo(RS(), l("pac_text"))



def documentation():
    if messagebox.askyesno(RS(), l("browser_problem")):
        webbrowser.open("https://anonimneo.github.io/NEO-Organization/Programs/Crowbar/help.html")



# @logger.catch()
def run_component(func, *args):
    """
    Данная функция запускает переданную функцию с переданными аргументами в отдельном потоке
    func - функция для запуска
    *args - аргументы для функции
    """
    try:
        if func is None:
            logger.error("OF/run_component - func не может быть None")
            return
        thread = threading.Thread(target=func, args=args, daemon=False)
        thread.start()
        logger.info(f'OF/run_component - {l("start_thread")} {func.__name__}')
    except:
        logger.exception(f'OF/run_component - {l("start_thread_error")} {func.__name__}')



# @logger.catch()
def run_component_process(func, *args):
    """
    Данная функция запускает переданную функцию с переданными аргументами в отдельном процессе
    (Важно: запускайте функцию в отдельном процессе только если запуск в отдельном потоке не помогает. Так как при запуске в отдельном процессе будет создана копия пространства памяти (Потребление ОЗУ будет сильно повышено))
    func - функция для запуска
    *args - аргументы для функции
    """
    try:
        if func is None:
            logger.error("OF/run_component - func не может быть None")
            return
        process = multiprocessing.Process(target=func, args=args)
        process.daemon = False
        process.start()
        logger.info(f'OF/run_component - {l("start_process")} {func.__name__}')
    except:
        logger.exception(f'OF/run_component - {l("start_process_error")} {func.__name__}')



# @logger.catch()
def restart_ca():
    """
    Данная функция перезапускает программу
    """
    logger.info(f'OF/restart_ca - {l("restart_ca")}...')
    python = sys.executable
    os.execl(python, python, *sys.argv)




# def run_obpc(RUN_IN_RECOVERY):
#     fail_start_obpc = 0
#     if not start_obpc:
#         try:
#             thread_obpc = threading.Thread(target=lambda: OBPC(RUN_IN_RECOVERY))
#             thread_obpc.daemon = True
#             thread_obpc.start()
#         except Exception as e:
#             logger.critical(f"OF/run_obpc - Ошибка при работе потока Компонента OnBoardPC:\n{e}")
#             fail_start_obpc += 1
#             if fail_start_obpc > 3:
#                 messagebox.showerror(RS(), "Произошла фатальная ошибка при работе с потоком Компонента OnBoardPC!\nПодробнее в лог-файле")
#                 return
#             logger.info(f"OF/run_obpc - Перезапуск OnBoardPC, попытка №{fail_start_obpc}...")
#             run_lp(RUN_IN_RECOVERY)
#     else:
#         messagebox.showwarning(RS(), "Компонент Голосовое Управление был запущен при запуске программы.")



# @logger.catch()
def apply_global_theme(window, current_theme):
    """
    Функция для применения темы к окну tkinter
    window - окно tkinter
    current_theme - Текущая тема для интерфейса (не сам кортеж, а название кортежа)
    return - функция ничего не возвращает!
    """
    style = ttk.Style()
    style.theme_use("clam")

    # Настройка стандартных tk-виджетов (включая верхнюю панель/меню)
    window.option_add("*Background", current_theme["bg"])
    window.option_add("*Foreground", current_theme["fg"])
    window.option_add("*Menu.activeBackground", current_theme["abg"])
    window.option_add("*Menu.activeForeground", current_theme["afg"])

    # Стилизация текстовых полей (tk.Text)
    window.option_add("*Text.Background", current_theme["bg"])
    window.option_add("*Text.Foreground", current_theme["fg"])
    window.option_add("*Text.InsertBackground", current_theme["fg"])
    window.option_add("*Text.SelectBackground", current_theme["abg"])
    window.option_add("*Text.SelectForeground", current_theme["afg"])

    # Стилизация чекбоксов (tk.Checkbutton)
    window.option_add("*Checkbutton.Background", current_theme["bg"])
    window.option_add("*Checkbutton.Foreground", current_theme["fg"])
    window.option_add("*Checkbutton.activeBackground", current_theme["abg"])
    window.option_add("*Checkbutton.activeForeground", current_theme["afg"])
    window.option_add("*Checkbutton.selectColor", current_theme["abg"])

    # Стилизация обычных кнопок (tk.Button)
    window.option_add("*Button.Background", current_theme["bbg"])
    window.option_add("*Button.Foreground", current_theme["bfg"])
    window.option_add("*Button.activeBackground", current_theme["abg"])
    window.option_add("*Button.activeForeground", current_theme["afg"])

    # Настройка базового стиля для всех ttk виджетов
    style.configure(".",
                    background=current_theme["bg"],
                    foreground=current_theme["fg"],
                    fieldbackground=current_theme["bg"],
                    bordercolor=current_theme["bbg"],
                    lightcolor=current_theme["bg"],
                    darkcolor=current_theme["bg"])

    # Таблицы
    style.configure("Treeview",
                    background=current_theme["bg"],
                    foreground=current_theme["fg"],
                    fieldbackground=current_theme["bg"],
                    rowheight=25)

    style.map("Treeview",
              background=[("selected", current_theme["abg"])],
              foreground=[("selected", current_theme["afg"])])

    style.configure("Treeview.Heading",
                    background=current_theme["bbg"],
                    foreground=current_theme["fg"],
                    relief="flat",
                    font=("default", 10, "bold"))

    style.map("Treeview.Heading",
              background=[("active", current_theme["abg"]), ("pressed", current_theme["abg"])],
              foreground=[("active", current_theme["afg"])])

    # Чекбоксы
    style.configure("TCheckbutton",
                    background=current_theme["bg"],
                    foreground=current_theme["fg"])

    style.map("TCheckbutton",
              background=[("active", current_theme["bg"])],
              foreground=[("active", current_theme["abg"])],
              indicatorcolor=[("selected", current_theme["abg"]), ("active", current_theme["bg"])])

    # Кнопки
    style.configure("TButton",
                    background=current_theme["bbg"],
                    foreground=current_theme["bfg"])
    style.map("TButton",
              background=[("active", current_theme["abg"])],
              foreground=[("active", current_theme["afg"])])

    # Поля ввода
    style.configure("TEntry",
                    fieldbackground=current_theme["bg"],
                    foreground=current_theme["fg"],
                    bordercolor=current_theme["bbg"])

    # Вкладки
    style.configure("TNotebook", background=current_theme["bg"], borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=current_theme["bbg"],
                    foreground=current_theme["bfg"],
                    padding=[10, 2])
    style.map("TNotebook.Tab",
              background=[("selected", current_theme["abg"])],
              foreground=[("selected", current_theme["afg"])])

    # Фон самого главного окна
    window.configure(bg=current_theme["bg"])



# Защищаем окно от подозрительно частого или резкого перемещения
def protect_window_from_moving(GUI, enable=True, DEBUG_MODE=False, MAX_MOVES_PER_SECOND=15, MAX_PIXEL_JUMP=250, DETECTION_WINDOW=1.5, LOCK_DURATION=0.6):
    """
    Главная функция AutoRunMaster
    RUN_IN_RECOVERY - Код работает в среде восстановления? Тогда True
    current_theme - Текущая тема для интерфейса (не сам кортеж, а название кортежа)
    DEBUG_MODE - включить режим отладки (если True будет больше логов)
    ОПЦИОНАЛЬНО:
        MAX_MOVES_PER_SECOND - Максимум перемещений в секунду
        MAX_PIXEL_JUMP - Максимальный скачок в пикселях
        DETECTION_WINDOW - Временное окно для анализа (секунды)
        LOCK_DURATION - Блокировка на n секунд после обнаружения
    return - функция ничего не возвращает!
    """
    # Состояние
    state = {
        "last_x": GUI.winfo_x(),
        "last_y": GUI.winfo_y(),
        "last_time": time(),
        "move_timestamps": deque(),
        "safe_x": GUI.winfo_x(),
        "safe_y": GUI.winfo_y(),
        "is_locked": False,
        "lock_time": 0,
        "attack_count": 0,
        "is_protected": enable,
    }

    def on_window_move(event):
        # Если защита отключена - ничего не делаем
        if not state["is_protected"]:
            return

        current_time = time()
        current_x = GUI.winfo_x()
        current_y = GUI.winfo_y()

        # Проверяем, не в режиме ли блокировки
        if state["is_locked"]:
            if current_time - state["lock_time"] < LOCK_DURATION:
                # Окно заблокировано - возвращаем в безопасную позицию
                GUI.geometry(f'+{state["safe_x"]}+{state["safe_y"]}')
                return
            else:
                # Блокировка истекла
                state["is_locked"] = False

        # Добавляем временную метку события
        state["move_timestamps"].append(current_time)

        # Удаляем старые события вне временного окна
        while state["move_timestamps"] and current_time - state["move_timestamps"][0] > DETECTION_WINDOW:
            state["move_timestamps"].popleft()

        # Вычисляем расстояние от последней позиции
        dx = abs(current_x - state["last_x"])
        dy = abs(current_y - state["last_y"])
        max_jump = max(dx, dy)

        # проверка на атаку
        is_attack = False
        attack_reason = ""

        # Слишком много перемещений в секунду
        if len(state["move_timestamps"]) > MAX_MOVES_PER_SECOND:
            is_attack = True
            attack_reason = f'{l("excessive_movements")} ({len(state["move_timestamps"])} {l("for2")} {DETECTION_WINDOW} {l("second")})'

        # Резкий скачок позиции
        if max_jump > MAX_PIXEL_JUMP and (current_time - state["last_time"]) < 0.05:
            is_attack = True
            attack_reason = f'{l("sharp_jump")}: {max_jump}px {l("for2")} {(current_time - state["last_time"])*1000:.1f} {l("milliseconds")}'

        if is_attack:
            state["is_locked"] = True
            state["lock_time"] = current_time
            state["attack_count"] += 1

            # Возвращаем окно в безопасную позицию
            GUI.geometry(f'+{state["safe_x"]}+{state["safe_y"]}')
            if DEBUG_MODE:
                logger.debug(f'protect_window_from_moving - {l("attack")} # {state["attack_count"]}: {attack_reason}')
                logger.debug(f'protect_window_from_moving - {l("window_block")} {LOCK_DURATION} {l("second")}')

        # Обновляем безопасную позицию при нормальном движении
        # state["last_x"] = current_x
        # state["last_y"] = current_y
        # state["last_time"] = current_time
        # state["safe_x"] = current_x
        # state["safe_y"] = current_y

    # Привязываем событие к окну
    GUI.bind("<Configure>", on_window_move)

    # Вкл/Выкл защиты
    def toggle_protection(new_state):
        state["is_protected"] = new_state
        if new_state:
            logger.success(f'OF/protect_window_from_moving - {l("protect_window_on")}')
        else:
            logger.info(f'OF/protect_window_from_moving - {l("protect_window_off")}')

    def get_status():
        return {
            "attacks_detected": state["attack_count"],
            "is_locked": state["is_locked"],
            "is_protected": state["is_protected"],
            "safe_position": (state["safe_x"], state["safe_y"])
        }

    if enable:
        logger.success(f'OF/protect_window_from_moving - {l("protect_window_on")}')

    # Возвращаем функции управления
    return toggle_protection, get_status



def restart_gui_for_theme(GUI, user_theme):
    current_theme = THEME[user_theme]
    apply_global_theme(GUI, current_theme)



# Создаём пункты в панели
def create_menubar(GUI, RUN_IN_RECOVERY, component=None, component_func=None, component_func2=None, elements=None, DEBUG_MODE=False, component_func3=None, component_func4=None, component_func5=None, component_func6=None):
    """
    Функция для создания стандартной верхней панели
    GUI - окно tkinter
    RUN_IN_RECOVERY - Код работает в среде восстановления? Тогда True
    component (str) - Название Компонента (Абривиатура).
    component_func - 1 Функция компонента которая будет вызываться из панели.
    component_func2 - 2 Функция компонента которая будет вызываться из панели.
    elements - аргументы для 1 и 2 функции.
    DEBUG_MODE - включить режим отладки (если True будет больше логов).
    component_func3 - 3 Функция компонента которая будет вызываться из панели.
    component_func4 - 4 Функция компонента которая будет вызываться из панели.
    component_func5 - 5 Функция компонента которая будет вызываться из панели.
    component_func6 - 6 Функция компонента которая будет вызываться из панели.
    return - функция ничего не возвращает!
    """
    menubar = Menu(GUI)

    if component == "FM":
        custom = 0
        menubar.add_command(label=l("search"), command=component_func)
    elif component == "ARM":
        custom = 0
    elif component == "PM":
        actions_menu = tk.Menu(menubar, tearoff=0)
        actions_menu.add_command(label=l("search"), accelerator="Ctrl+F", command=lambda: component_func(elements, DEBUG_MODE))
        actions_menu.add_command(label=l("cancel_search"), accelerator="Esc", command=lambda: component_func2(elements))
        menubar.add_cascade(label=l("actions"), menu=actions_menu)
        custom = 0
    elif component == "FE":
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=l("file"), menu=file_menu)
        file_menu.add_command(label=l("open"), command=component_func, accelerator="Ctrl+O")
        file_menu.add_command(label=l("save"), command=component_func2, accelerator="Ctrl+S")
        file_menu.add_command(label=l("save_as"), command=component_func3, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label=l("exit"), command=component_func4, accelerator="Alt+F4")

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=l("view"), menu=view_menu)

        font_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label=l("font"), menu=font_menu)

        fonts = ["Courier", "Arial", "Times New Roman", "Helvetica", "Verdana", "Consolas"]
        for font in fonts:
            font_menu.add_command(label=font, command=lambda f=font: component_func5(f))

        size_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label=l("font_size"), menu=size_menu)

        sizes = [8, 10, 11, 12, 14, 16, 18, 20, 24]
        for size in sizes:
            size_menu.add_command(label=str(size), command=lambda s=size: component_func6(s))
        custom = 0
    else:
        custom = 0

    theme_menu = Menu(menubar, tearoff=0)
    themes = [("dark", "dark"), ("white", "white"), ("red", "red"), ("green", "lime"), ("contrast", "black"), ("gray", "gray"), ("orange", "orange")]
    for label, theme_name in themes:
        theme_menu.add_checkbutton(label=l(label), command=lambda tn=theme_name: restart_gui_for_theme(GUI, tn))
    menubar.add_cascade(label=l("themes"), menu=theme_menu)

    # Переменные состояния
    higher = tk.BooleanVar(value=not RUN_IN_RECOVERY)
    protect = tk.BooleanVar(value=not RUN_IN_RECOVERY)

    # Сохраняем индексы с учётом смещения
    topmost_index = (menubar.index("end") + 1 if menubar.index("end") else 1) + custom
    menubar.add_command(label=f'{l("topmost")}: {l("on2")}')

    protect_index = (menubar.index('end') + 1) + custom
    menubar.add_command(label=f'Защита окна: {l("on2")}')

    pac_index = (menubar.index("end") + 1) + custom
    menubar.add_command(label=f'{l("pac")} - {PROGRAM_AUTHENTICATION_CLYTH}')

    # Функции переключения
    def toggle_topmost():
        higher.set(not higher.get())
        GUI.attributes("-topmost", higher.get())
        status = l("on2") if higher.get() else l("off2")
        menubar.entryconfig(topmost_index, label=f'{l("topmost")}: {status}')

    def toggle_protect():
        protect.set(not protect.get())
        protect_window_from_moving(GUI, protect.get(), DEBUG_MODE)
        status = l("on2") if protect.get() else l("off2")
        menubar.entryconfig(protect_index, label=f'Защита окна: {status}')

    # Присваиваем команды
    menubar.entryconfig(topmost_index, command=toggle_topmost)
    menubar.entryconfig(protect_index, command=toggle_protect)
    menubar.entryconfig(pac_index, command=pac)

    GUI.config(menu=menubar)

    # Активируем защиту в обычной среде
    if not RUN_IN_RECOVERY:
        GUI.attributes("-topmost", True)
        GUI.after(100, lambda: protect_window_from_moving(GUI, True, DEBUG_MODE))



# Получаем оффлайн-пути реестра
# @logger.catch()
def get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, RUN_IN_RECOVERY):
    if RUN_IN_RECOVERY:
        psutil = Psutil()
    elif not RUN_IN_RECOVERY:
        import psutil

    if not RUN_IN_RECOVERY:
        # В онлайн-режиме возвращаем исходные константы
        return hkey_const, subkey_path

    offline_map = ARM_CORE_GLOBALS["OFFLINE_HKEY_MAP"]

    if hkey_const == winreg.HKEY_CURRENT_USER:
        # HKCU всегда перенаправляется на загруженный NTUSER.DAT
        new_hkey, temp_name, _ = offline_map[hkey_const]
        # Путь: HKEY_LOCAL_MACHINE\Offline_USER\{subkey_path}
        new_subkey_path = f"{temp_name}\\{subkey_path}"
        return new_hkey, new_subkey_path

    elif hkey_const == winreg.HKEY_LOCAL_MACHINE:
        # HKLM: Проверяем, начинается ли subkey_path с "Software"
        if subkey_path.lower().startswith(r"software"):
            new_hkey, temp_name, _ = offline_map[hkey_const]
            # Удаляем "Software" из начала subkey_path и добавляем имя загруженного куста
            path_after_software = subkey_path[len("Software"):].strip('\\')
            # Путь: HKEY_LOCAL_MACHINE\Offline_SOFTWARE\{путь_после_Software}
            new_subkey_path = f"{temp_name}\\{path_after_software}"
            return new_hkey, new_subkey_path

    return hkey_const, subkey_path



# Получаем диск с установленной шиндовс
# @logger.catch()
def get_current_disc(RUN_IN_RECOVERY=False):
    """
    Функция для получения диска с установленной шиндовс
    RUN_IN_RECOVERY - Код работает в среде восстановления? Тогда True
    return - "[Буква_диска]:\\"
    """
    try:
        if RUN_IN_RECOVERY:
            # В WinPE ищем диск с каталогом Windows, отличный от X:
            drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWYZ"]
            for drive in drives:
                if os.path.exists(os.path.join(drive, 'Windows')):
                    logger.info(f'OF - {l("system_found")} {drive}')
                    return drive, True
            return "X:\\", False

        import psutil
        # Для обычной среды
        partitions = psutil.disk_partitions()
        for p in partitions:
            if "fixed" in p.opts and os.path.exists(os.path.join(p.mountpoint, "Windows")):
                return p.mountpoint, True
        return "C:\\", False
    except:
        logger.exception(f'OF\\get_current_disc - {l("unknown_error")}')
        return "X:\\", False



# Загрузка кустов реестра
# @logger.catch()
def load_bush(current_disc, user=False):
    global active_loaded_hives

    if user:
        user_name = user
    else:
        # Формируем пути к файлам
        if not os.path.isdir(f"{current_disc}\\Users\\{default_user_name}\\"):
            user_name = simpledialog.askstring(title=RS(), prompt=f'{l("user_not_found")} {default_user_name}\n{l("enter_user_name")}:')
        else:
            user_name = default_user_name

    hive_paths = {
        HIVE_MAP["SYSTEM"]: os.path.join(current_disc, "Windows", "System32", "config", "SYSTEM"),
        HIVE_MAP["SOFTWARE"]: os.path.join(current_disc, "Windows", "System32", "config", "SOFTWARE"),
        HIVE_MAP["USER"]: os.path.join(current_disc, "Users", user_name, "NTUSER.DAT")
    }

    success_count = 0

    for name, path in hive_paths.items():
        if not os.path.exists(path):
            logger.critical(f'OF/load_bush - {l("bush_not_found")}: {path}')
            continue

        # Если куст уже в списке активных, пропустим
        if name in active_loaded_hives:
            continue

        try:
            # Загрузка куста реестра
            winreg.LoadKey(winreg.HKEY_LOCAL_MACHINE, name, path)

            active_loaded_hives.append(name)
            logger.info(f'OF/load_bush - {l("bush")} {name} {l("success_load")} {path}')
            success_count += 1
        except:
            logger.exception(f'OF/load_bush - {l("load_bush_error")} {path}\\{name}')

    # Возвращаем True, если загрузили хотя бы один куст
    return success_count > 0



# Выгружаем кусты реестра
# @logger.catch()
def unload_bush():
    global active_loaded_hives

    for name in reversed(active_loaded_hives[:]):
        try:
            winreg.unloadkey(winreg.HKEY_LOCAL_MACHINE, name)
            active_loaded_hives.remove(name)
            logger.success(f'OF/unload_bush - {l("bush")} {name} {l("success_unload")}.')
        except:
            logger.exception(f'OF/unload_bush - {l("unload_bush_error")} {name}')



# Получаем Имя текущего пользователя
# @logger.catch()
def get_user_name():
    try:
        user_name = os.getlogin()
        return user_name
    except:
        logger.exception(f'OF/get_user_name - {l("get_user_name_error")}!')
        return default_user_name



# Извлекаем имя файла из пути и/или удаляя аргументы командной строки
def extract_filename_from_path(path_with_args, get_path=False):
    if not path_with_args:
        return ""

    # Удаляем лишние пробелы в начале и конце
    path_with_args = path_with_args.strip()

    # Если путь в кавычках, извлекаем содержимое
    if path_with_args.startswith('"'):
        closing_quote = path_with_args.find('"', 1)
        if closing_quote != -1:
            path_with_args = path_with_args[1:closing_quote]
    else:
        # Ищем последнее расширение исполняемого файла
        import re
        # Ищем путь до первого расширения (.exe, .dll, .com, .bat, .cmd и т.д.)
        match = re.search(r"([^\s]*\.(exe|dll|com|bat|cmd|scr|vbs|js|ps1|msi|sys|drv))\s*", path_with_args, re.IGNORECASE)
        if match:
            path_with_args = match.group(1)
        # Если расширение не найдено, берём всё до первого пробела
        else:
            space_index = path_with_args.find(" ")
            if space_index != -1:
                path_with_args = path_with_args[:space_index]

    if get_path:
        return path_with_args

    # Извлекаем имя файла (последняя часть после последнего обратного слэша)
    file_name = path_with_args.split("\\")[-1]
    return file_name.strip()



# Фейковая Активность
def decoy_mode(cycle=False, debug=True):
    c = 1
    while c > 0:
        fake_ips = []
        fake_pings = []
        fake_cmds = []
        fake_dirs = []
        fake_files = []

        # Генерируем IP, пинги, команды и ключи реестра
        for i in range(5):
            fake_ips.append(f'{RS("ip")}.{RS("ip")}.{RS("ip")}.{RS("ip")}')
            fake_pings.append(f'ping {RS("ping")}.{RS("ping")}.{RS("ping")}.{RS("ping")}')
            fake_cmds.append(RS("cmd"))
            fake_dirs.append(fr'C:\ProgramData\{RS("dir")}')

        try:
            for i in range(0, 3):
                subprocess.Popen(f"ipconfig /flushdns && nslookup {fake_ips[i]}", stdout=subprocess.DEVNULL, shell=True, stderr=subprocess.DEVNULL, creationflags=0x08000000)

            # Создаём директории
            for d in fake_dirs:
                if not os.path.exists(d):
                    if debug:
                        logger.debug(f"create dir - {d}")
                    os.makedirs(d)

            # Создаём файлы в директориях
            for d in fake_dirs:
                for j in range(3):
                    file_path = RS("file", d)
                    fake_files.append(file_path)
                    try:
                        with open(file_path, "w") as file:
                            file.write(RS("data"))
                        if debug:
                            logger.debug(f"create - {f}")
                    except:
                        logger.exception(f'{l("create_file_error")}: {file_path}')

            # Пинги
            for p in fake_pings:
                subprocess.Popen(p, stdout=subprocess.DEVNULL, shell=True, stderr=subprocess.DEVNULL, creationflags=0x08000000)
            for i in range(3, 5):
                subprocess.Popen(f"ipconfig /flushdns && nslookup {fake_ips[i]}", stdout=subprocess.DEVNULL, shell=True, stderr=subprocess.DEVNULL, creationflags=0x08000000)

            # реестр
            try:
                # Генерируем и создаём ключи в реестре
                for i in range(3):
                    key_name = f"Software\\{RS(10)}"
                    registry_keys.append(key_name)

                    try:
                        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_name)
                        if debug:
                            logger.debug(f'{l("create_reg_key")} - {key_name}')

                        # Создаём параметры с информацией о "сборе данных"
                        params = {
                            "UserName": get_random_username(),
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "SystemInfo": f"System_{RS(8)}",
                            "LastAccess": datetime.now().strftime("%H:%M:%S"),
                            "DataHash": RS(16),
                            "SessionID": f"SID_{randint(1000, 9999)}",
                            "ProcessPID": str(randint(100, 9999)),
                            "ComputerName": RS(12),
                            "IPAddress": fake_ips[i],
                            "CollectionData": RS("data")
                        }

                        # Записываем параметры в реестр
                        for param_name, param_value in params.items():
                            winreg.SetValueEx(key, param_name, 0, winreg.REG_SZ, param_value)
                            if debug:
                                logger.debug(f'{l("create-key")} - {key_name}\\{param_name} = {param_value[:20]}')

                        winreg.CloseKey(key)

                    except:
                        logger.exception(f'{l("create_key_error")} {key_name}')

            except:
                logger.exception()

            for cmd in fake_cmds:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, shell=True, stderr=subprocess.DEVNULL, creationflags=0x08000000)

            # удаление ключей
            for key_name in registry_keys:
                try:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_name)
                    if debug:
                        logger.debug(f'{l("reg_key_delete")} - {key_name}')
                except:
                    logger.exception(f'{l("reg_key_delete_error")} - {key_name}')

            for cmd in fake_cmds:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, shell=True, stderr=subprocess.DEVNULL, creationflags=0x08000000)

            # Удаляем файлы и директории
            for f in fake_files:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                        if debug:
                            logger.debug(f'{l("file_delete")} - {f}')
                except:
                    logger.exception(f'{l("file_delete_error")} {f}')

            for d in fake_dirs:
                try:
                    if os.path.exists(d):
                        if debug:
                            logger.debug(f'{l("dir_delete")} dir - {d}')
                        os.rmdir(d)
                except:
                    logger.exception(f'{l("delete_dir_error")} {d}')

            if not cycle:
                c = 0
        except Exception as e:
            logger.exception(f'OF/decoy_mode - {l("decoy_mode_error")}!:')
            if not cycle:
                messagebox.showerror(RS(), f'{l("decoy_mode_error")}!:\n{e}')



# CMD
##def CMD():
##    try:
##        CMD_GUI = tk.Tk()
##        CMD_GUI.title(RS())
##        CMD_GUI.geometry('700x450')
##        from config import THEME, DEFAULT_THEME
##        current_theme = THEME[DEFAULT_THEME]
##        apply_global_theme(CMD_GUI, current_theme)
##
##        # Создаем виджет для вывода
##        console_text = scrolledtext.ScrolledText(CMD_GUI, wrap=tk.WORD, font=('Default', 10))
##        console_text.pack(fill='both', expand=True, padx=5, pady=5)
##
##        # Создаем рамку для ввода команд и кнопки
##        input_frame = tk.Frame(CMD_GUI)
##        input_frame.pack(fill='x', padx=5, pady=5)
##
##        command_entry = tk.Entry(input_frame, font=('Default', 10))
##        command_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
##
##        def print_to_console(msg):
##            console_text.insert(tk.END, msg + '\n')
##            console_text.see(tk.END)
##
##        def execute_command():
##            CMD_GUI = command_entry.get().strip()
##            if not CMD_GUI:
##                return
##            print_to_console(f'> {CMD_GUI}')
##            command_entry.delete(0, tk.END)
##
##            # Обработка команд
##            try:
##                result = subprocess.run(CMD_GUI, shell=True, capture_output=True, text=True, encoding='cp866')
##                output = result.stdout if result.stdout else result.stderr
##                print_to_console(output.strip())
##            except Exception as e:
##                logger.exception(f'OF/CMD - {l("error")}')
##                print_to_console(f'{l("error")}:\n{e}')
##
##        execute_button = tk.Button(input_frame, text=l('execute'), command=execute_command)
##        execute_button.pack(side='right')
##
##        # Обработка нажатия Enter в поле ввода
##        def on_enter(event):
##            execute_command()
##
##        command_entry.bind('<Return>', on_enter)
##
##        # Возвращаем функцию для вывода сообщений
##        return print_to_console
##    except:
##        logger.exception(f'OF/CMD - {l("error")}')



# Запуск в скрытом режиме
def launch_ghost(exe_path=False):
    if not exe_path:
        exe_path = filedialog.askopenfilename(title=RS(), filetypes=[('Все файлы', '*.*')])
        if not exe_path:
            return
    try:
        n = randint(4, 24)
        temp_dir = tempfile.mkdtemp()
        rand_name = ''.join(random.choices(string.ascii_letters, k=n)) + '.exe'
        temp_path = os.path.join(temp_dir, rand_name)
        shutil.copy2(exe_path, temp_path)

        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE

        subprocess.Popen([temp_path], startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW)
        logger.success(f'{l("start_in_ghost_mode")}: {temp_path}')
    except Exception as e:
        logger.exception(f'OF/launch_ghost - {l("start_in_ghost_mode_error")}')
        messagebox.showerror(RS(), f'{l("start_in_ghost_mode_error")}:\n{e}')



# Открыть С помощью
# @logger.catch()
def open_with():
    target_file_path = filedialog.askopenfilename(title=RS(), filetypes=[('Все файлы', '*.*')])
    if target_file_path and os.path.isfile(target_file_path): # Проверка, что файл выбран и существует
        app_path = filedialog.askopenfilename(title=RS(), filetypes=[('Все файлы', '*.*')])
        if app_path:
            try:
                subprocess.Popen([app_path, target_file_path])
            except Exception as e:
                logger.exception(f'OF/open_with - {l("open_file_error")} "{target_file_path}" {l("with_program")} "{app_path}"', e)
                messagebox.showerror(RSRS(), f'{l("open_file_error")} {l("with_program")}:\n{e}')



def enable_debug_mode():
    """
    Функция для включения тестового режима (режима отладки)
    Если её выполнить то все Компоненты будут запускаться с DEBUG_MODE=True
    Что приведёт к увелечиному числу логов, с большим количеством информации
    Также будут разблокированы тестовый Компоненты (эксперементальные)
    Важно: Для уже запущенных компонентов DEBUG_MODE - не поменяется на True - для этого потребуется перезапуск Компонента
    Тоже самое касается и меню в иконке из-за чего новые пункты появятся только в Главном меню
    Важно2: После перезапуска программы DEBUG_MODE вновь будет раен False
    return - функция ничего не возвращает!
    """
    if askyesno(RS(), l("enable_debug_mode_text")):
        logger.warning(f'OF/enable_debug_mode - {l("debug_mode_on")}.')
        return True
    return False



# @logger.catch()
def reg_file(reg_file, reg_code):
    with open(reg_file, "w") as reg:
        reg.write(reg_code)
    try:
        os.startfile(reg_file)
    except:
        logger.exception(f'OF/reg_file - {l("start_error")} {reg_file}')



# @logger.catch()
def run_command(command):
    try:
        # Запускает команду и ждём её завершения
        process = subprocess.run(command, shell=True)
        return process.returncode
    except:
        logger.exception(f'OF/run_command - {l("start_command_error")} - {command}')
