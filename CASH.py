# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

from tkinter import messagebox
from languages import l
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
import sys
import os

# Импорт Компонентов
try:
    from AP import AP
except:
    def AP(a=None, b=None, c=None, d=None, e=None, f=None, j=None, q=None, w=None, r=None, t=None, y=None, u=None, i=None, o=None, s=None, h=None, k=None, l=None):
        pass
try:
    from ARM import ARM
except:
    def ARM(a=None, b=None):
        pass

try:
    from CC import CC
except:
    def CC(a=None, b=None):
        pass

try:
    from AES import AES
except:
    def AES():
        return 'print("error")'

try:
    from config import *
    import config
except:
    pass

try:
    from E import E
except:
    def E():
        pass

try:
    from EC import EC
except:
    def EC(a=None, b=None):
        pass

try:
    from FE import FE
except:
    def FE(a=None):
        pass

try:
    from FM import FM
except:
    def FM(a=None, b=None):
        pass

try:
    from FR import FR
except:
    def FR(a=None, b=None):
        pass

try:
    from GFA import GFA
except:
    def GFA(a=None, b=None):
        pass

try:
    from RLP import RLP
except:
    def RLP(a=None, b=None):
        pass

try:
    from CM import CM
except:
    def CM(a=None, b=None):
        pass

try:
    from OF import pac, apply_global_theme, get_offline_reg_path, Psutil, run_component, run_component_process, get_user_name, restart_ca, reg_file, run_command, open_with, get_current_disc, load_bush, unload_bush
except:
    def restart_ca():
        pass
    def open_with():
        pass
    def pac():
        messagebox.showerror(RS(), f'{l["pac"]} {l["not_available"]}!')
    def apply_global_theme(a=None, b=None):
        pass
    def get_offline_reg_path(a=None, b=None):
        pass
    def run_component(a=None, b=None):
        pass
    def run_component_process(a=None, b=None):
        pass
    def run_command(a=None, b=None):
        pass
    def load_bush(a=None, b=None):
        pass
    def unload_bush(a=None, b=None):
        pass
    def get_current_disc(a=None, b=None):
        pass
    def get_user_name(a=None, b=None):
        pass

try:
    from PM import PM
except:
    def PM(a=None, b=None):
        pass

try:
    from R import R
except:
    def R():
        pass

try:
    from RS import RS
except:
    def RS(a=None):
        return "error"

try:
    from Run import Run
except:
    def Run(a=None, b=None):
        pass

try:
    from SAU import SAU
except:
    def SAU(a=None, b=None):
        pass

try:
    from SP import SP, scarecrow_protection_version
except:
    def SP(a=None, b=None):
        pass

try:
    from UA import UA, check_and_restore_fonts_if_needed
except:
    def check_and_restore_fonts_if_needed(a=None):
        pass
    def UA(a=None, b=None):
        pass

try:
    from UM import UM
except:
    def UM(a=None, b=None):
        pass

CROWBAR_ANTIVIRUS_SCRIPTS_HANDLER_VERSION = "0.4.10 Beta"

current_theme = THEME[DEFAULT_THEME]

# Получаем настройки скрипта
def get_script_config(code):
    """Получаем конфигурацию скрипта (опции запуска)"""
    config = {
        "delete_script_after_exec": False,
        "launch_when_program_starts": False,
        "enable_while": False,
    }

    # Ищем строки с переменными конфигурации
    for line in code.split("\n"):
        line = line.strip()

        # Пропускаем комментарии и пустые строки
        if not line or line.startswith("# "):
            continue

        if "delete_script_after_exec" in line and "=" in line:
            try:
                value = line.split("=")[1].strip()
                config["delete_script_after_exec"] = value.lower() == "true"
            except:
                pass

        elif "launch_when_program_starts" in line and "=" in line:
            try:
                value = line.split("=")[1].strip()
                config["launch_when_program_starts"] = value.lower() == "true"
            except:
                pass

        elif "enable_while" in line and "=" in line:
            try:
                value = line.split("=")[1].strip()
                config["enable_while"] = value.lower() == "true"
            except:
                pass

        # Выходим, если начался код скрипта
        if line and not line.startswith("# ") and not any(var in line for var in
            ["delete_script_after_exec", "launch_when_program_starts", "enable_while", "valid_version"]):
            break

    return config



def CASH(RUN_IN_RECOVERY, DEBUG_MODE=False):
    """Обработчик скриптов"""
    while True:
        if len(sys.argv) > 1:
            # Был передан файл
            file_path = sys.argv[1]
            if DEBUG_MODE:
                logger.debug(f'CASH - {l("file_transferred")}: {file_path}')
            # Получаем расширение файла
            _, file_extension = os.path.splitext(file_path)
            f_e = file_extension.lower() # Преобразуем в нижний регистр
            if f_e == ".txt" or f_e == ".md" or f_e == ".py":
                FE(file_path)
                break
            elif f_e == ".cas":
                try:
                    with open(file_path, "r", encoding="utf-8-sig") as script:
                        code = script.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, "r", encoding="cp1251") as script:
                            code = script.read()
                    except UnicodeDecodeError:
                        # Попытка с игнорированием ошибок
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as script:
                            code = script.read()

                code = AES(code, clyth, True)

                config = get_script_config(code)

                if DEBUG_MODE:
                    logger.debug(f'CASH - {l("script_config")}: {config}')

                # Создаём контекст выполнения с доступными функциями программы
                exec_globals = {
                    # "__builtins__": __builtins__,
                    "logger": logger,
                    "sys": sys,
                    "os": os,
                    "messagebox": messagebox,
                    "RUN_IN_RECOVERY": RUN_IN_RECOVERY,
                    "run_component": run_component,
                    "run_component_process": run_component_process,
                    "RUN_IN_RECOVERY": RUN_IN_RECOVERY,
                    "current_theme": current_theme,
                    "AP": AP,
                    "ARM": ARM,
                    "CC": CC,
                    "AES": AES,
                    "CM": CM,
                    "config": config,
                    "EC": EC,
                    "FE": FE,
                    "FM": FM,
                    "FR": FR,
                    "GFA": GFA,
                    # OF
                    "Psutil": Psutil,
                    "run_component": run_component,
                    "apply_global_theme": apply_global_theme,
                    "get_offline_reg_path": get_offline_reg_path,
                    "get_current_disc": get_current_disc,
                    "load_bush": load_bush,
                    "unload_bush": unload_bush,
                    "get_user_name": get_user_name,
                    "open_with": open_with,
                    "reg_file": reg_file,
                    "run_command": run_command,
                    "PM": PM,
                    "RLP": RLP,
                    "RS": RS,
                    "Run": Run,
                    "SAU": SAU,
                    "SP": SP,
                    "UA": UA,
                    "UM": UM,
                }

                try:
                    exec(code, exec_globals)
                except Exception as e:
                    logger.exception(f'CASH - {l("exec_script_error")} {file_path}')
                    messagebox.showerror(RS(), f'{l("exec_script_error")}:\n{e}')

                # Используем полученную конфигурацию
                delete_script_after_exec = config["delete_script_after_exec"]
                launch_when_program_starts = config["launch_when_program_starts"]
                enable_while = config["enable_while"]

                if delete_script_after_exec:
                    try:
                        os.remove(file_path)
                        if DEBUG_MODE:
                            logger.debug(f'CASH - {l("script_deleted")}: {file_path}')
                    except:
                        logger.exception(f'CASH - {l("script_deleted_error")}: {file_path}')

                # Выходим из цикла
                if not enable_while:
                    break
                # Если enable_while=True, цикл продолжится и скрипт выполнится снова
                if not enable_while:
                    logger.success(f'CASH - {l("execution_completed")}.')
            else:
                messagebox.showwarning(RS(), l("command_not_found_for_file"))
                break
        else:
            break # Выход, если файл не был передан

if __name__ == "__main__":
    CASH(False, True)
