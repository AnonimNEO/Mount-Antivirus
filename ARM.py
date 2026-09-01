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
from tkinter import ttk, Menu, messagebox, simpledialog
import tkinter as tk
# Дата и Время
from datetime import datetime
# Логирование Ошибок
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
# Переменные среды
from pathlib import Path
# Работа с реестром
import winreg
# Работа с файлами и ОС
import xml.etree.ElementTree as ET
import win32com.client
import os

from FE import FE
from GFA import GFA
from RS import RS
from languages import l
from PM import action_process_by_name
from OF import pac, get_current_disc, get_offline_reg_path, loaded_hive_names, apply_global_theme, extract_filename_from_path, create_menubar

AUTORUN_MASTER_VERSION = "3.7.23 Beta"

# Класс для взаимодействия с Планировщиком Задач в обычной среде
class TaskSchedulerManager:
    def __init__(self):
        # Инициализация COM-объекта Планировщика Задач
        try:
            self.scheduler = win32com.client.Dispatch("Schedule.Service")
            self.scheduler.Connect()
            self.root_folder = self.scheduler.GetFolder("\\")
        except Exception as e:
            self.scheduler = None
            self.root_folder = None
            logger.exception(f'ARM - {l("scheduler_error")}')
            messagebox.showerror(RS(), f'{l("scheduler_error")}.\n{e}')

    # Функция для получения каталога задач
    def get_folder(self, task_path):
        folder_path = os.path.dirname(task_path)
        if not folder_path:
            return self.root_folder

        try:
            return self.root_folder.GetFolder(folder_path)
        except Exception:
            return None

    # Вспомогательная функция для обхода всех задач в каталоге
    def traverse_folder(self, folder, all_tasks):
        if not folder:
            return

        # Получаем задачи в текущем каталоге
        tasks = folder.GetTasks(0)
        for task in tasks:
            all_tasks.append(task)

        # Рекурсивно обходим подкаталоги
        subfolders = folder.GetFolders(0)
        for subfolder in subfolders:
            self.traverse_folder(subfolder, all_tasks)

    # Получает список всех задач через COM-интерфейс
    def get_all_tasks(self):
        if not self.root_folder:
            return []

        all_com_tasks = []
        self.traverse_folder(self.root_folder, all_com_tasks)
        return all_com_tasks

    # Включает или отключает задачу через COM
    def set_task_state_com(self, task_path_full, enable):
        if not self.scheduler:
            return False
        try:
            folder_path = os.path.dirname(task_path_full) or "\\"
            task_name = os.path.basename(task_path_full)
            folder = self.scheduler.GetFolder(folder_path)
            task = folder.GetTask(task_name)

            task.Enabled = enable
            folder.RegisterTaskDefinition(
                task_name,
                task.Definition,
                6,
                None,
                None,
                task.Definition.Principal.LogonType
            )
            return True
        except:
            logger.exception(f'ARM - {l("edit_task_error")} {task_path_full}')
            return False

    # Удаляет задачу через COM
    def delete_task_com(self, task_path_full):
        if not self.scheduler:
            return False
        try:
            folder_path = os.path.dirname(task_path_full) or "\\"
            task_name = os.path.basename(task_path_full)
            folder = self.scheduler.GetFolder(folder_path)
            folder.DeleteTask(task_name, 0)
            return True
        except:
            logger.exception(f'ARM - {l("delete_task_error")} {task_path_full}')
            return False



def ARM(RUN_IN_RECOVERY=False, current_theme="dark", DEBUG_MODE=False):
    """Главная функция Компонента Мастера Автозагрузки (точка входа)"""
    REG_TYPE_MAP = {
        winreg.REG_SZ: "REG_SZ",
        winreg.REG_EXPAND_SZ: "REG_EXPAND_SZ",
        winreg.REG_MULTI_SZ: "REG_MULTI_SZ",
        winreg.REG_DWORD: "REG_DWORD",
        winreg.REG_QWORD: "REG_QWORD",
        winreg.REG_BINARY: "REG_BINARY",
        winreg.REG_NONE: "REG_NONE"
    }

    # Обратное соответствие
    REG_TYPE_MAP_REV = {v: k for k, v in REG_TYPE_MAP.items()}

    # Список для диалога "Создать"
    CREATABLE_REG_TYPES = ["REG_SZ", "REG_EXPAND_SZ", "REG_MULTI_SZ", "REG_DWORD", "REG_QWORD", "REG_BINARY"]

    ARM_GUI_ELEMENTS = {
        "master": None,
        "notebook": None,
        "tree": None,
        "tabs": {},
        "vsb": None,
        "current_tab": l("custom"),
        "treeview_data": [],
        "focus_after_update": None
    }

    # Путь к каталогу автозагрузки пользователя
    if RUN_IN_RECOVERY:
        current_disc, found_disc = get_current_disc(RUN_IN_RECOVERY)
        if not os.path.isfile(f"{current_disc}\\Users\\{default_user_name}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"):
            user_name = simpledialog.askstring(title=RS(), prompt=f'{l("user_not_found")} {default_user_name}\n{l("enter_user_name")}: ')
        else:
            user_name = default_user_name
        # Путь к каталогу автозагрузки оффлайн-системы
        user_startup_path_str = f"{current_disc}\\Users\\{user_name}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"
        user_startup = Path(user_startup_path_str)
    else:
        appdata_path = os.getenv("APPDATA")

        if appdata_path is not None:
            user_startup = Path(appdata_path) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        else:
            user_startup = fr"C:\Users\{default_user_name}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"

    c_v = "Software\Microsoft\Windows\CurrentVersion"
    wow64 = "SOFTWARE\WOW6432Node\Microsoft"
    ARM_CORE_GLOBALS = {
        "user_startup_path": user_startup,
        "REG_KEYS": {
            l("custom"): None, # Для файлов
            l("registry"): [
                (winreg.HKEY_CURRENT_USER, rf"{c_v}\Run", "Run"),
                (winreg.HKEY_CURRENT_USER, rf"{c_v}\RunOnce", "RunOnce"),
                (winreg.HKEY_LOCAL_MACHINE, rf"{wow64}\Windows\CurrentVersion\Run", "Run")
            ],
            l("system"): [
                (winreg.HKEY_LOCAL_MACHINE, rf"{c_v}\Winlogon", "Shell"),
                (winreg.HKEY_LOCAL_MACHINE, rf"{c_v}\Winlogon", "Userinit"),
                (winreg.HKEY_LOCAL_MACHINE, rf"{c_v}\Winlogon", "Taskman"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager", "Bootshell"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SafeBoot", "AlternateShell"),
                (winreg.HKEY_LOCAL_MACHINE, rf"{c_v}\Polices\System", "legalnoticecaption"),
                (winreg.HKEY_LOCAL_MACHINE, rf"{c_v}\Polices\System", "legalnoticetext")
            ],
            "AppInit_DLLs": [
                (winreg.HKEY_LOCAL_MACHINE, rf"{c_v}\Windows", "AppInit_DLLs", "x64"),
                (winreg.HKEY_LOCAL_MACHINE, rf"{c_v}\Windows", "LoadAppInit_DLLs", "x64"),
                (winreg.HKEY_LOCAL_MACHINE, rf"{wow64}\Windows NT\CurrentVersion\Windows", "AppInit_DLLs", "x32"),
                (winreg.HKEY_LOCAL_MACHINE, rf"{wow64}\Windows NT\CurrentVersion\Windows", "LoadAppInit_DLLs", "x32"),
            ],
            "CmdLine": [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\Setup", "CmdLine"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\Setup", "SetupType"),
                (winreg.HKEY_LOCAL_MACHINE, rf"{c_v}\Policies\System", "EnableCursorSuppression"),
            ]
        },
        # Добавляем карту для преобразования констант HKEY_ в строки
        "HKEY_MAP": {
            winreg.HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT",
            winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
            winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
            winreg.HKEY_USERS: "HKEY_USERS",
            winreg.HKEY_CURRENT_CONFIG: "HKEY_CURRENT_CONFIG",
        },
        "OFFLINE_HKEY_MAP": {
            winreg.HKEY_LOCAL_MACHINE: (winreg.HKEY_LOCAL_MACHINE, loaded_hive_names["SOFTWARE"], "Software"),
            # Для ключей, начинающихся с HKLM\Software
            # Ключи, не начинающиеся с HKLM\Software, не будут работать
            winreg.HKEY_CURRENT_USER: (winreg.HKEY_LOCAL_MACHINE, loaded_hive_names["USER"], None)
        }
    }

    try:
        # Форматируем Unix-таймштамп в читаемую строку
        def format_time(timestamp):
            if timestamp == 0:
                return l("error")
            return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")

        # В зависимости от вкладки и типа элемента возвращает имя файла или путь
        def get_filename_from_item(item_data, current_tab):
            if current_tab == l("custom"):
                return item_data.get(f'{l("name")} {l("file2")}', "")
            elif current_tab in [l("registry"), l("system"), "AppInit_DLLs", "CmdLine"]:
                return item_data.get(f'{l("name")} {l("parameter")}', "")
            elif current_tab == l("scheduler"):
                return item_data.get(l("path"), "")
            else:
                return ""

        # Получаем автозагрузку пользователя
        def get_user_startup(ARM_CORE_GLOBALS):
            user_startup_path = ARM_CORE_GLOBALS["user_startup_path"]
            ARM_data = []
            try:
                for item in user_startup_path.iterdir():
                    if item.is_file() and item.name.lower() != "desktop.ini":
                        try:
                            stats = item.stat()
                            ARM_data.append({
                                f'{l("name")} {l("file2")}': item.name,
                                f'{l("date")} {l("creation")}': format_time(stats.st_ctime),
                                l("danger"): "50%",
                                f'{l("date")} {l("changes")}': format_time(stats.st_mtime),
                                f'{l("date")} {l("discoveries")}': format_time(stats.st_atime),
                                f'{l("path")} {l("parameter")}': str(item)
                            })
                        except:
                            logger.exception(f'ARM - {l("metadata_error")} {item.name}')
                            ARM_data.append({
                                f'{l("name")} {l("file2")}': item.name,
                                f'{l("date")} {l("creation")}': l("error"),
                                f'{l("date")} {l("changes")}': l("error"),
                                f'{l("date")} {l("discoveries")}': l("error"),
                                f'{l("path")} {l("parameter")}': str(item)
                            })
            except Exception as e:
                logger.exception(f'ARM - {l("startup_error")}')
                messagebox.showerror(RS(), f'{l("startup_error")}:\n{e}')
            return ARM_data

        # Получаем данные из заданного ключа реестра
        def read_registry_key(ARM_CORE_GLOBALS, hkey_const, subkey_path, value_name=None):
            # Если value_name = None, читает все значения в ключе
            # Если value_name указано, читает только это значение
            hkey_map = ARM_CORE_GLOBALS["HKEY_MAP"]
            ARM_data = []

            if RUN_IN_RECOVERY:
                final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, RUN_IN_RECOVERY)
            else:
                final_hkey = hkey_const
                final_subkey = subkey_path

            hkey_name = hkey_map.get(hkey_const, str(hkey_const))
            full_path = f"{hkey_name}\\{subkey_path}"

            def check_value(value_name, value):
                if value_name == "Shell" and value != "explorer.exe":
                    return "100%"
                elif value_name == "Shell":
                    return "1%"
                elif value_name == "Userinit" and value != r"C:\Windows\System32\userinit.exe":
                    return "100%"
                elif value_name == "Userinit":
                    return "1%"
                elif value_name == "Taskman" and value != "":
                    return "100%"
                elif value_name == "Taskman":
                    return "0%"
                elif value_name == "Bootshell" and value != r"%SystemRoot%\system32\bootim.exe":
                    return "100%"
                elif value_name == "Bootshell":
                    return "1%"
                elif value_name == "AlternateShell" and value != "cmd.exe":
                    return "100%"
                elif value_name == "AlternateShell":
                    return "1%"
                elif value_name == "AppInit_DLLs" and value != "":
                    return "100%"
                elif value_name == "AppInit_DLLs":
                    return "0%"
                elif value_name == "LoadAppInit_DLLs" and str(value) != "0":
                    return "100%"
                elif value_name == "LoadAppInit_DLLs":
                    return "0%"
                elif value_name == "CmdLine" and value != "":
                    return "100%"
                elif value_name == "CmdLine":
                    return "0%"
                elif value_name == "SetupType" and str(value) != "0":
                    return "100%"
                elif value_name == "SetupType":
                    return "0%"
                elif value_name == "EnableCursorSuppression":
                    return "0%"
                elif value_name == "legalnoticecaption" or value_name == "legalnoticetext":
                    return "0%"
                else:
                    return "50%"

            try:
                with winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_READ) as key:
                    if value_name is not None:
                        try:
                            value, reg_type = winreg.QueryValueEx(key, value_name)
                            ARM_data.append({
                                f'{l("name")} {l("parameter")}': value_name,
                                f'{l("meaning")} {l("parameter")}': str(value),
                                l('danger'): check_value(value_name, value),
                                f'{l("type")} {l("parameter")}': REG_TYPE_MAP.get(reg_type),
                                f'{l("path")} {l("parameter")}': full_path,
                                'hkey': hkey_const,
                                'subkey': subkey_path,
                                'value_type': reg_type
                            })
                        except FileNotFoundError:
                            if key != "Taskman" and key != "legalnoticecaption" and key != "legalnoticetext":
                                logger.warning(f'ARM - {l("key_not_found")}: {full_path}\\{value_name}')
                        except:
                            logger.exception(f'ARM - {l("read_key_error")} {full_path}\\{value_name}')
                            ARM_data.append({
                                f'{l("name")} {l("parameter")}': value_name,
                                f'{l("meaning")} {l("parameter")}': l("error"),
                                l('danger'): check_value(value_name, value),
                                f'{l("type")} {l("parameter")}': l("error"),
                                f'{l("path")} {l("parameter")}': full_path,
                                "hkey": hkey_const,
                                "subkey": subkey_path,
                                "value_type": winreg.REG_NONE
                            })
                    else:
                        i = 0
                        while True:
                            try:
                                value_name, value, reg_type = winreg.EnumValue(key, i)
                                ARM_data.append({
                                    f'{l("name")} {l("parameter")}': value_name,
                                    f'{l("meaning")} {l("parameter")}': str(value),
                                    l('danger'): check_value(value_name, value),
                                    f'{l("type")} {l("parameter")}': REG_TYPE_MAP.get(reg_type),
                                    f'{l("path")} {l("parameter")}': full_path,
                                    "hkey": hkey_const,
                                    "subkey": subkey_path,
                                    "value_type": reg_type
                                })
                                i += 1
                            except OSError:
                                break
                            except FileNotFoundError:
                                pass
                            except:
                                logger.exception(f'ARM - {l("read_key_error")} {full_path}\\{value_name}')
                                ARM_data.append({
                                    f'{l("name")} {l("parameter")}': value_name,
                                    f'{l("meaning")} {l("parameter")}': l("error"),
                                    l("danger"): "50%",
                                    f'{l("type")} {l("parameter")}': l("error"),
                                    f'{l("path")} {l("parameter")}': full_path,
                                    "hkey": hkey_const,
                                    "subkey": subkey_path,
                                    "value_type": winreg.REG_NONE
                                })
            except FileNotFoundError:
                if value_name != "Taskman" and value_name != "legalnoticecaption" and value_name != "legalnoticetext":
                    logger.warning(f'ARM - {l("key_not_found")}: {full_path}')
            except:
                logger.exception(f'ARM - {l("read_key_error")} {full_path}')
            return ARM_data

        # Получаем данные из ключей Run и RunOnce пользователя
        def get_registry_startup(ARM_CORE_GLOBALS):
            reg_keys = ARM_CORE_GLOBALS["REG_KEYS"]
            ARM_data = []
            for hkey_const, subkey_path, _ in reg_keys[l("registry")]:
                ARM_data.extend(read_registry_key(ARM_CORE_GLOBALS, hkey_const, subkey_path))
            return ARM_data

        # Получаем значения из Winlogon
        def get_system_startup(ARM_CORE_GLOBALS):
            reg_keys = ARM_CORE_GLOBALS["REG_KEYS"]
            ARM_data = []
            for hkey_const, subkey_path, value_name in reg_keys[l('system')]:
                ARM_data.extend(read_registry_key(ARM_CORE_GLOBALS, hkey_const, subkey_path, value_name))
            return ARM_data

        # Получаем значения параметров AppInit_DLLs и LoadAppInit_DLLs
        def get_dll_startup(ARM_CORE_GLOBALS):
            reg_keys = ARM_CORE_GLOBALS["REG_KEYS"]
            ARM_data = []
            for hkey_const, subkey_path, value_name, bitness in reg_keys["AppInit_DLLs"]:
                ARM_data.extend(read_registry_key(ARM_CORE_GLOBALS, hkey_const, subkey_path, value_name))
            return ARM_data

        # Получаем значения параметров для вкладки CmdLine
        def get_cmdline_startup(ARM_CORE_GLOBALS):
            reg_keys = ARM_CORE_GLOBALS["REG_KEYS"]
            ARM_data = []
            for hkey_const, subkey_path, value_name in reg_keys["CmdLine"]:
                ARM_data.extend(read_registry_key(ARM_CORE_GLOBALS, hkey_const, subkey_path, value_name))
            return ARM_data

        # Создаём новый параметр реестра
        def create_reg_value(hkey_const, subkey_path, name, reg_type_str, ARM_GUI_ELEMENTS):
            reg_type = REG_TYPE_MAP_REV.get(reg_type_str)
            if reg_type is None:
                if DEBUG_MODE:
                    logger.error(f'ARM - Неизвестный тип реестра: {reg_type_str}')
                return False

            if reg_type in (winreg.REG_SZ, winreg.REG_EXPAND_SZ, winreg.REG_MULTI_SZ):
                initial_value = ""
            elif reg_type in (winreg.REG_DWORD, winreg.REG_QWORD):
                initial_value = 0
            elif reg_type == winreg.REG_BINARY:
                initial_value = b""
            else:
                initial_value = ""

            if RUN_IN_RECOVERY:
                final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, RUN_IN_RECOVERY)
            else:
                final_hkey = hkey_const
                final_subkey = subkey_path

            try:
                with winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ) as key:
                    winreg.SetValueEx(key, name, 0, reg_type, initial_value)
                    logger.success(f'ARM - {l("create_key")}: {name} {l("with_type")} {reg_type_str} {l("in")} {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}\\')
                    ARM_GUI_ELEMENTS["focus_after_update"] = {"type": "name", "value": name}
                    return True
            except PermissionError:
                messagebox.showerror(RS(), l("permission_error"))
                return False
            except Exception as e:
                logger.exception(f'ARM - {l("create_key_error")}: {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}\\{name}')
                messagebox.showerror(RS(), f'{l("create_key_error")} "{name}".\n{e}')
                return False

        # Обновляем существующий параметр реестра
        def update_reg_value(hkey_const, subkey_path, name, new_value, reg_type, item_id, ARM_GUI_ELEMENTS):
            if RUN_IN_RECOVERY:
                final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, RUN_IN_RECOVERY)
            else:
                final_hkey = hkey_const
                final_subkey = subkey_path

            try:
                # Преобразование значения в нужный тип
                if reg_type in (winreg.REG_DWORD, winreg.REG_QWORD):
                    try:
                        value_to_set = int(new_value)
                    except ValueError:
                        # raise ValueError(f'ARM - Некорректное числовое значение для типа {REG_TYPE_MAP.get(reg_type, "неизвестный")}')
                        pass

                elif reg_type == winreg.REG_MULTI_SZ:
                    value_to_set = new_value.split("\n")

                elif reg_type == winreg.REG_BINARY:
                    try:
                        hex_string = new_value.replace(" ", "")
                        if len(hex_string) % 2 != 0:
                            hex_string = "0" + hex_string

                        value_to_set = bytes.fromhex(hex_string)
                    except ValueError as e:
                        # raise ValueError(f'ARM - Некорректная шестнадцатеричная строка для REG_BINARY.\n{e}')
                        pass

                else:
                    value_to_set = new_value

                with winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name, 0, reg_type, value_to_set)
                    logger.success(f'ARM - {l("update_key")}: {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}\\{name}')
                    ARM_GUI_ELEMENTS["focus_after_update"] = {"type": "iid", "value": item_id}
                    return True

            except PermissionError:
                messagebox.showerror(RS(), l("permission_error"))
                return False
            except ValueError as e:
                logger.error(f'ARM - Ошибка преобразования значения для параметра реестра: {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}\\{name}:\n{e}')
                return False
            except Exception as e:
                comment = f'ARM - {l("update_key_error")}: {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}\\{name}'
                messagebox.showerror(RS(), f"{comment}\n{e}")
                logger.exception(comment)
                return False

        # Удаляем параметр реестра
        def delete_reg_value(hkey_const, subkey_path, name, item_id, ARM_GUI_ELEMENTS):
            if RUN_IN_RECOVERY:
                final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, RUN_IN_RECOVERY)
            else:
                final_hkey = hkey_const
                final_subkey = subkey_path
            try:
                ARM_GUI_ELEMENTS["focus_after_update"] = get_next_item_iid(ARM_GUI_ELEMENTS, item_id)

                with winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
                    logger.success(f'ARM - {l("delete_key")}: {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}\\{name}')
                    return True
            except PermissionError:
                logger.error(f'ARM - {l("delete_key_error")}, {l("permission_error")}: {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}\\{name}')
                messagebox.showerror(RS(), l('permission_error'))
                return False
            except Exception as e:
                logger.exception(f'ARM - {l("delete_key_error")}: {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}\\{name}')
                messagebox.showerror(RS(), f'{l("delete_key_error")} "{name}".\n{e}')
                return False

        # Удаляем файл
        def delete_file(file_path, file_name):
            file = Path(file_path)
            try:
                if os.path.isfile(file):
                    os.remove(file)
                    return True
                else:
                    messagebox.showinfo(RS(), l("file_not_found"))
                    return True
            except PermissionError:
                logger.error(f'ARM - {l("permission_error")}: {file_path}')
                messagebox.showerror(RS(), l("permission_error"))
                return False
            except FileNotFoundError:
                messagebox.showinfo(RS(), l("file_not_found"))
                return True
            except Exception as e:
                logger.exception(f'ARM - {l("file_delete_error")}: {file_path}')
                messagebox.showerror(RS(), f'{l("file_delete_error")} "{file.name}".\n{e}')
                return False

        # Вспомогательная функция для получения пути к папке задач
        def get_tasks_directory():
            # Если режим восстановления - используем букву вмонтированного диска
            if RUN_IN_RECOVERY:
                return Path(f"{current_disc}Windows\\System32\\Tasks")
            # Если обычная система - берем системный путь через переменную окружения
            return Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32" / "Tasks"

        # Вспомогательная функция для удаления пространства имен из тегов XML
        def strip_namespace(tag):
            if "}" in tag:
                return tag.split("}", 1)[1]
            return tag

        # Сохраняем кодировки UTF-16
        def save_xml_task(tree, file_path):
            try:
                # Windows Tasks часто требуют UTF-16 LE и BOM
                with open(file_path, "wb") as f:
                    tree.write(f, encoding="utf-16", xml_declaration=True)
                return True
            except:
                logger.exception(f'ARM - {l("save_xml_task_error")} {file_path}')
                return False

        # Получаем Автозагрузку из Планировщика Задач (Универсальный метод через XML ИЛИ COM)
        def get_task_scheduler_startup():
            ARM_data = []

            if not RUN_IN_RECOVERY:
                manager = TaskSchedulerManager()
                com_tasks = manager.get_all_tasks()

                for task in com_tasks:
                    try:
                        # Получаем полный путь задачи
                        full_path = task.Path
                        name = os.path.basename(full_path)
                        is_enabled = task.Enabled

                        # Попытка получить действие (Command)
                        action_path = f'{l("no")} ExecAction'
                        definition = task.Definition

                        for action in definition.Actions:
                            # TASK_ACTION_EXEC = 0 (константа COM)
                            if action.Type == 0:
                                cmd = action.Path
                                args = action.Arguments
                                action_path = f"{cmd} {args}".strip()
                                break

                        # Получаем автора
                        author = definition.RegistrationInfo.Author

                        # Получаем дату создания
                        try:
                            date_created = str(task.Definition.RegistrationInfo.Date)
                        except Exception:
                            date_created = l("error")

                        action_path = l("unknown")
                        if task.Definition.Actions.Count > 0:
                            action = task.Definition.Actions.Item(1)
                            if action.Type == 0:
                                # Извлекаем путь к исполняемому файлу из свойства Path самого действия
                                raw_path = getattr(action, "Path", l('unknown'))
                                if raw_path != l("unknown"):
                                    action_path = os.path.abspath(raw_path)

                        ARM_data.append({
                            l("name"): name,
                            l("state"): l("on") if is_enabled else l('off'),
                            l("path"): action_path,
                            l("author"): author,
                            f'{l("date")} {l("creation")}': date_created,
                            "TaskPath": full_path,
                            "Enabled_raw": is_enabled
                        })
                    except:
                        logger.exception(f'ARM - {l("task_error")} {task.Path}')
                        ARM_data.append({
                            l("name"): task.Path,
                            l("state"): l("error"),
                            l("path"): f'{l("error")} {l("reading_error")}',
                            l("author"): l("error"),
                            f'{l("date")} {l("creation")}': None,
                            "TaskPath": task.Path,
                            "Enabled_raw": False
                        })
                return ARM_data

            else:
                tasks_dir = get_tasks_directory()

                if not tasks_dir.exists():
                    logger.error(f'ARM - {l("task-dir_error")}: {tasks_dir}')
                    return ARM_data

                for root, _, files in os.walk(tasks_dir):
                    for file_name in files:
                        file_path = Path(root) / file_name

                        try:
                            # Парсим XML файл
                            tree = ET.parse(file_path)
                            xml_root = tree.getroot()

                            # Инициализируем переменные по умолчанию
                            name = file_name
                            is_enabled = True  # По умолчанию задачи включены, если тег отсутствует
                            action_path = f'{l("no")} ExecAction'
                            author = f'{l("systems")}/{l("unknown")}'

                            # Проходим по дереву XML
                            # Так как namespace может меняться, ищем локальные имена тегов
                            for elem in xml_root.iter():
                                tag = strip_namespace(elem.tag)

                                if tag == "Author":
                                    author = elem.text if elem.text else author

                                elif tag == "Enabled":
                                    # Если текст "false", то задача выключена
                                    if elem.text and elem.text.lower() == 'false':
                                        is_enabled = False

                                elif tag == "Command":
                                    # Ищем исполняемую команду
                                    action_path = elem.text if elem.text else action_path

                                elif tag == "Arguments":
                                    pass

                            for child in xml_root.iter():
                                if strip_namespace(child.tag) == "Exec":
                                    cmd_text = ""
                                    arg_text = ""
                                    for sub in child:
                                        sub_tag = strip_namespace(sub.tag)
                                        if sub_tag == "Command" and sub.text:
                                            cmd_text = sub.text
                                        if sub_tag == "Arguments" and sub.text:
                                            arg_text = sub.text

                                    if cmd_text:
                                        action_path = f"{cmd_text} {arg_text}".strip()
                                        break # Берем первое действие

                            ARM_data.append({
                                l("name"): name,
                                l("state"): l("on") if is_enabled else l("off"),
                                l("path"): action_path,
                                l("author"): author,
                                "TaskPath": str(file_path), # Полный путь к файлу XML
                                "Enabled_raw": is_enabled
                            })

                        except ET.ParseError:
                            # Это не XML или файл поврежден
                            continue
                        except:
                            logger.exception(f'ARM - {l("xml_task_error")} {file_name}')
                            ARM_data.append({
                                l("name"): file_name,
                                l("state"): l("error"),
                                l("path"): l("error"),
                                l("author"): l("error"),
                                "TaskPath": str(file_path),
                                "Enabled_raw": False
                            })
                return ARM_data

        # Изменяем состояние задачи (Вкл/Выкл)
        def get_task_startup(task_path_str, enable, item_id, ARM_GUI_ELEMENTS):
            if not RUN_IN_RECOVERY:
                manager = TaskSchedulerManager()
                if manager.set_task_state_com(task_path_str, enable):
                    state = l("on") if enable else l("off")
                    logger.success(f'ARM - {l("task")} "{task_path_str}" {l("success")} {state} {l("from_com")}.')
                    ARM_GUI_ELEMENTS["focus_after_update"] = {"type": "iid", "value": item_id}
                    return True
                return False
            else:
                task_path = Path(task_path_str)
                if not task_path.exists():
                    messagebox.showerror(RS(), f'{l("file_not_found")}:\n{task_path}')
                    return False
                try:
                    # Регистрируем все пространства имен для сохранения префиксов
                    ET.register_namespace("", "http://schemas.microsoft.com/windows/2004/02/mit/task")
                    tree = ET.parse(task_path)
                    root = tree.getroot()

                    ns = ""
                    if "}" in root.tag:
                        ns = root.tag.split("}")[0] + "}"

                    settings = root.find(f"{ns}Settings")
                    if settings is None:
                        settings = ET.SubElement(root, f"{ns}Settings")

                    enabled_tag = settings.find(f"{ns}Enabled")
                    if enabled_tag is None:
                        enabled_tag = ET.SubElement(settings, f"{ns}Enabled")

                    enabled_tag.text = "true" if enable else "false"

                    if save_xml_task(tree, task_path):
                        state = l("on") if enable else l("off")
                        logger.success(f'ARM - {l("task")} "{task_path.name}" {l("success")} {state} {l("from_xml")}.')
                        ARM_GUI_ELEMENTS["focus_after_update"] = {"type": "iid", "value": item_id}
                        return True
                    return False
                except Exception as e:
                    logger.exception(f'ARM - {l("xml_error")}')
                    messagebox.showerror(RS(), f'{l("xml_error")}:\n{e}')
                    return False

        # Удаляем задачу из планировщика
        def delete_task_scheduler_task(task_path_str, task_name, item_id, ARM_GUI_ELEMENTS):
            if not RUN_IN_RECOVERY:
                manager = TaskSchedulerManager()
                if manager.delete_task_com(task_path_str):
                    logger.success(f'ARM - {l("task")} "{task_path_str}" {l("delete_task_com")}.')
                    ARM_GUI_ELEMENTS["focus_after_update"] = get_next_item_iid(ARM_GUI_ELEMENTS, item_id)
                    return True
                return False
            else:
                try:
                    task_path = Path(task_path_str)
                    if task_path.exists():
                        ARM_GUI_ELEMENTS["focus_after_update"] = get_next_item_iid(ARM_GUI_ELEMENTS, item_id)
                        task_path.unlink()
                        logger.success(f'ARM - {l("xml_task_delete")}: {task_path}')
                        return True
                    else:
                        messagebox.showerror(RS(), l("file_not_found"))
                        return False
                except Exception as e:
                    logger.exception(f'ARM - {l("xml_task_delete_error")}')
                    messagebox.showerror(RS(), f'{l("file_delete_error")}:\n{e}')
                    return False

        # Обработка смены вкладки
        def on_tab_change(event, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS):
            selected_tab = ARM_GUI_ELEMENTS["notebook"].tab(ARM_GUI_ELEMENTS["notebook"].select(), "text")
            if selected_tab != ARM_GUI_ELEMENTS["current_tab"]:
                ARM_GUI_ELEMENTS["current_tab"] = selected_tab
                set_treeview_columns(ARM_GUI_ELEMENTS)
                load_current_tab_data(ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS)

        # Функция для преобразования типов
        def _to_sortable_type(val):
            try:
                # Попытка преобразовать в число
                return float(val)
            except (ValueError, TypeError):
                # Иначе вернуть как строку в нижнем регистре
                return str(val).lower()

        # Сортируем столбик по клику на заголовок
        def sort_treeview_column(ARM_GUI_ELEMENTS, col):
            tree = ARM_GUI_ELEMENTS.get("tree")
            if not tree:
                return

            items = tree.get_children("")
            if not items:
                return

            ARM_GUI_ELEMENTS.setdefault("sort_direction", {})
            reverse = ARM_GUI_ELEMENTS["sort_direction"].get(col, "asc") == "desc"
            ARM_GUI_ELEMENTS["sort_direction"][col] = "desc" if not reverse else "asc"

            data_to_sort = []
            for item_id in items:
                val = tree.set(item_id, col)
                sortable_val = _to_sortable_type(val)
                data_to_sort.append((sortable_val, item_id))

            data_to_sort.sort(key=lambda t: t[0], reverse=reverse)

            for i, (val, item_id) in enumerate(data_to_sort):
                tree.move(item_id, "", i)

            all_cols = list(tree["columns"])

            for c in all_cols:
                current_text = tree.heading(c, "text")
                current_text = current_text.replace(" \u25B2", "").replace(" \u25BC", "")
                tree.heading(c, text=current_text)

            arrow = " \u25BC" if reverse else " \u25B2"
            current_text = tree.heading(col, 'text'"")
            tree.heading(col, text=current_text + arrow)

        # Обработчик события получения фокуса Treeview
        def handle_treeview_focus_in(ARM_GUI_ELEMENTS):
            tree = ARM_GUI_ELEMENTS.get("tree")
            if not tree:
                return

            items = tree.get_children("")

            if items:
                if not tree.selection():
                    first_item = items[0]
                    tree.selection_set(first_item)
                    tree.focus(first_item)

        # Обработчик ПКМ
        def handle_right_click(event, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS):
            item_id = ARM_GUI_ELEMENTS["tree"].identify_row(event.y)
            ARM_GUI_ELEMENTS["tree"].selection_set(item_id)
            if item_id:
                selected_values = ARM_GUI_ELEMENTS["tree"].item(item_id, "values")
                current_cols = ARM_GUI_ELEMENTS["tree"]["columns"]
                item_data = next((data for data in ARM_GUI_ELEMENTS["treeview_data"] if [str(data.get(k, '')) for k in current_cols] == list(selected_values)), None)
            else:
                item_data = None
            show_context_menu(event, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS, item_data, item_id)

        # Установка столбиков, в зависимости от вкладки
        def set_treeview_columns(ARM_GUI_ELEMENTS):
            if ARM_GUI_ELEMENTS["tree"] and ARM_GUI_ELEMENTS["tree"].winfo_exists():
                ARM_GUI_ELEMENTS["tree"].destroy()

            current_frame = ARM_GUI_ELEMENTS["tabs"][ARM_GUI_ELEMENTS["current_tab"]]

            if ARM_GUI_ELEMENTS["vsb"] and ARM_GUI_ELEMENTS["vsb"].winfo_exists():
                ARM_GUI_ELEMENTS["vsb"].pack_forget()

            ARM_GUI_ELEMENTS["tree"] = ttk.Treeview(current_frame, selectmode="browse")
            ARM_GUI_ELEMENTS["tree"].pack(side="left", fill="both", expand=True)

            ARM_GUI_ELEMENTS["vsb"] = ttk.Scrollbar(current_frame, orient="vertical", command=ARM_GUI_ELEMENTS["tree"].yview)
            ARM_GUI_ELEMENTS["vsb"].pack(side="right", fill="y")
            ARM_GUI_ELEMENTS["tree"].configure(yscrollcommand=ARM_GUI_ELEMENTS["vsb"].set)

            ARM_GUI_ELEMENTS["tree"].bind("<Button-3>", lambda e: handle_right_click(e, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS))
            ARM_GUI_ELEMENTS["tree"].bind("<Key>", lambda e: handle_key_press(e, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS))
            ARM_GUI_ELEMENTS["tree"].bind("<c>", lambda e: handle_menu_key(e, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS))
            ARM_GUI_ELEMENTS["tree"].bind("<FocusIn>", lambda e: handle_treeview_focus_in(ARM_GUI_ELEMENTS))

            columns = []
            headings = {}

            if ARM_GUI_ELEMENTS["current_tab"] == l("custom"):
                columns = (f'{l("name")} {l("file2")}', f'{l("date")} {l("creation")}', l('danger'), f'{l("date")} {l("changes")}', f'{l("date")} {l("discoveries")}')
                headings = dict(zip(columns, columns))
            elif ARM_GUI_ELEMENTS["current_tab"] == l("registry"):
                columns = (f'{l("name")} {l("parameter")}', f'{l("meaning")} {l("parameter")}', l('danger'), f'{l("type")} {l("parameter")}', f'{l("path")} {l("parameter")}')
                headings = dict(zip(columns, columns))
            elif ARM_GUI_ELEMENTS["current_tab"] == l("system"):
                columns = (f'{l("name")} {l("parameter")}', f'{l("meaning")} {l("parameter")}', l('danger'), f'{l("type")} {l("parameter")}', f'{l("path")} {l("parameter")}')
                headings = dict(zip(columns, columns))
            elif ARM_GUI_ELEMENTS["current_tab"] == "AppInit_DLLs":
                columns = [f'{l("name")} {l("parameter")}', l('bit'), f'{l("meaning")} {l("parameter")}', l('danger'), f'{l("path")} {l("parameter")}']
                headings = dict(zip(columns, columns))
            elif ARM_GUI_ELEMENTS["current_tab"] == "CmdLine":
                columns = (f'{l("name")} {l("parameter")}', f'{l("meaning")} {l("parameter")}', l('danger'), f'{l("type")} {l("parameter")}', f'{l("path")} {l("parameter")}')
                headings = dict(zip(columns, columns))
            elif ARM_GUI_ELEMENTS["current_tab"] == l("scheduler"):
                columns = (l("name"), l("state"), l("path"), l("author"))
                headings = dict(zip(columns, columns))

            ARM_GUI_ELEMENTS["tree"]["columns"] = columns
            ARM_GUI_ELEMENTS["tree"]["show"] = "headings"

            for col in columns:
                ARM_GUI_ELEMENTS["tree"].heading(
                    col,
                    text=headings.get(col, col),
                    command=lambda _col=col: sort_treeview_column(ARM_GUI_ELEMENTS, _col)
                )
                ARM_GUI_ELEMENTS["tree"].column(col, width=100, anchor=tk.W)

            if columns:
                ARM_GUI_ELEMENTS["tree"].column(columns[0], width=150, anchor=tk.W)
                if ARM_GUI_ELEMENTS["current_tab"] == "AppInit_DLLs":
                    ARM_GUI_ELEMENTS["tree"].column(columns[0], width=75, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[1], width=15, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[2], width=15, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[3], width=150, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[4], width=75, anchor=tk.W)
                if ARM_GUI_ELEMENTS["current_tab"] in [l("registry"), l("system"), "CmdLine"]:
                    ARM_GUI_ELEMENTS["tree"].column(columns[0], width=100, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[1], width=250, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[2], width=15, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[3], width=50, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[4], width=75, anchor=tk.W)
                if ARM_GUI_ELEMENTS["current_tab"] == l("scheduler"):
                    ARM_GUI_ELEMENTS["tree"].column(columns[0], width=175, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[1], width=65, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[2], width=300, anchor=tk.W)
                    ARM_GUI_ELEMENTS["tree"].column(columns[3], width=50, anchor=tk.W)

        # Восстанавливаем фокус после обновления данных
        def restore_focus_after_update(ARM_GUI_ELEMENTS):
            tree = ARM_GUI_ELEMENTS["tree"]
            focus_info = ARM_GUI_ELEMENTS["focus_after_update"]
            ARM_GUI_ELEMENTS["focus_after_update"] = None

            if focus_info:
                target_iid = None

                if focus_info["type"] == "iid":
                    if tree.exists(focus_info["value"]):
                        target_iid = focus_info["value"]

                elif focus_info["type"] == "name":
                    name_to_find = focus_info["value"]
                    current_cols = tree["columns"]
                    name_col_index = current_cols.index(f'{l("name")} {l("parameter")}') if f'{l("name")} {l("parameter")}' in current_cols else -1

                    if name_col_index != -1:
                        for item_id in tree.get_children(""):
                            values = tree.item(item_id, "values")
                            if values and values[name_col_index] == name_to_find:
                                target_iid = item_id
                                break

                if target_iid:
                    tree.selection_set(target_iid)
                    tree.focus(target_iid)
                    tree.see(target_iid)
                    return

            items = tree.get_children("")
            if items:
                if not tree.selection():
                    tree.selection_set(items[0])
                    tree.focus(items[0])

        # Загружаем данные для активной вкладки и заполняем таблицу
        def load_current_tab_data(ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS):
            tree = ARM_GUI_ELEMENTS["tree"]
            current_tab = ARM_GUI_ELEMENTS["current_tab"]

            # Очищаем Treeview перед загрузкой новых данных
            for item in tree.get_children():
                tree.delete(item)

            if current_tab == l("custom"):
                ARM_GUI_ELEMENTS["treeview_data"] = get_user_startup(ARM_CORE_GLOBALS)
                columns = [f'{l("name")} {l("file2")}', f'{l("date")} {l("creation")}', l('danger'), f'{l("date")} {l("changes")}', f'{l("date")} {l("discoveries")}']
            elif current_tab == l("registry"):
                ARM_GUI_ELEMENTS['treeview_data'] = get_registry_startup(ARM_CORE_GLOBALS)
                columns = [f'{l("name")}, {l("parameter")}', f'{l("meaning")} {l("parameter")}', l('danger'), f'{l("type")} {l("parameter")}', f'{l("path")} {l("parameter")}']
            elif current_tab == l("system"):
                ARM_GUI_ELEMENTS["treeview_data"] = get_system_startup(ARM_CORE_GLOBALS)
                columns = [f'{l("name")} {l("parameter")}', f'{l("meaning")} {l("parameter")}', l('danger'), f'{l("type")} {l("parameter")}', f'{l("path")} {l("parameter")}']
            elif current_tab == "AppInit_DLLs":
                ARM_GUI_ELEMENTS["treeview_data"] = get_dll_startup(ARM_CORE_GLOBALS)
                columns = [f'{l("name")} {l("parameter")}', l('bit'), f'{l("meaning")} {l("parameter")}', l('danger'), f'{l("path")} {l("parameter")}']
            elif current_tab == "CmdLine":
                ARM_GUI_ELEMENTS["treeview_data"] = get_cmdline_startup(ARM_CORE_GLOBALS)
                columns = [f'{l("name")} {l("parameter")}', f'{l("meaning")} {l("parameter")}', l('danger'), f'{l("type")} {l("parameter")}', f'{l("path")} {l("parameter")}']
            elif current_tab == l("scheduler"):
                raw_tasks = get_task_scheduler_startup()

                # if show_only_with_date.get():
                #     ARM_GUI_ELEMENTS['treeview_data'] = [
                #         t for t in raw_tasks
                #         if t.get(f'{l("date")} {l("creation")}') and t.get(f'{l("date")} {l("creation")}') not in ['', l("error"), '01-01-1970 00:00:00']
                #     ]
                # else:
                ARM_GUI_ELEMENTS["treeview_data"] = raw_tasks

                columns = [l("name"), l("state"), l("path"), l("author")]
            else:
                ARM_GUI_ELEMENTS["treeview_data"] = []
                columns = []

            for item_data in ARM_GUI_ELEMENTS["treeview_data"]:
                values = [item_data.get(col, "") for col in columns]
                unique_id = item_data.get("TaskPath") or str(hash(frozenset(item_data.items())))
                tree.insert("", "end", values=values, tags=("ARM_data",), iid=unique_id, open=True)

            restore_focus_after_update(ARM_GUI_ELEMENTS)

        # Вспомогательная функция для получения iid ближайшего элемента
        def get_next_item_iid(ARM_GUI_ELEMENTS, current_item_id):
            tree = ARM_GUI_ELEMENTS["tree"]
            items = list(tree.get_children(""))
            try:
                current_index = items.index(current_item_id)
                if current_index + 1 < len(items):
                    return {"type": "iid", "value": items[current_index + 1]}
                elif current_index - 1 >= 0:
                    return {"type": "iid", "value": items[current_index - 1]}
                else:
                    return None
            except ValueError:
                return None

        # Контекстное Меню
        def show_context_menu(event, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS, item_data, item_id):
            master = ARM_GUI_ELEMENTS["master"]
            current_tab = ARM_GUI_ELEMENTS["current_tab"]
            reg_keys = ARM_CORE_GLOBALS["REG_KEYS"]

            menu = tk.Menu(master, tearoff=0)

            if current_tab != l("system") and current_tab != l("custom") and current_tab != l("scheduler") and current_tab != "CmdLine":
                create_menu = tk.Menu(menu, tearoff=0)

                if current_tab in [l("registry"), "AppInit_DLLs"]:
                    if current_tab == l("registry"):
                        hkey_const, subkey_path, _ = reg_keys[l("registry")][0]
                    elif current_tab == "AppInit_DLLs":
                        hkey_const, subkey_path, _, _ = reg_keys["AppInit_DLLs"][0]

                    for reg_type_str in CREATABLE_REG_TYPES:
                        create_menu.add_command(
                            label=f'{l("parameter")} {reg_type_str}',
                            command=lambda type=reg_type_str: prompt_for_new_reg_value(ARM_GUI_ELEMENTS, hkey_const, subkey_path, type)
                        )
                    menu.add_cascade(label=l("create"), menu=create_menu)
                    menu.add_separator()

            if item_data:
                if current_tab == l("custom"):
                    file_path = item_data[f'{l("path")} {l("parameter")}']
                    file_name = item_data[f'{l("name")} {l("file2")}']

                    menu.add_command(label=l("edit_file"), command=lambda: FE(file_path))
                    menu.add_command(label=f'{l("copy_path")} (Ctrl+C)', command=lambda: copy_to_clipboard(master, file_path))
                    menu.add_command(label=f'{l("copy")} {l("name")} (Ctrl+Shift+C)', command=lambda: copy_to_clipboard(master, file_name))
                    menu.add_separator()
                    menu.add_command(label=f'{l("suspend_process_for_name")} {file_name}', command=lambda: action_process_by_name(file_name, "suspend", DEBUG_MODE))
                    menu.add_command(label=f'{l("kill_process_for_name")} {file_name}', command=lambda: action_process_by_name(file_name, "kill", DEBUG_MODE))
                    menu.add_separator()
                    menu.add_command(label=f'{l("delete")} {l("file")} (Delete)', command=lambda: confirm_and_delete_file(ARM_GUI_ELEMENTS, file_path, file_name, item_id))

                elif current_tab in [l("registry"), l("system"), "AppInit_DLLs", "CmdLine"]:
                    reg_name = item_data[f'{l("name")} {l("parameter")}']
                    reg_path = item_data[f'{l("path")} {l("parameter")}']
                    reg_value = item_data[f'{l("meaning")} {l("parameter")}']

                    file_name = extract_filename_from_path(reg_value)
                    file_path_without_args = extract_filename_from_path(reg_value, True)

                    menu.add_command(label=l("get_full_access"), command=lambda: GFA(reg_path, RUN_IN_RECOVERY))
                    menu.add_command(label=f'{l("copy_path")} (Ctrl+C)', command=lambda: copy_to_clipboard(master, reg_path))
                    menu.add_command(label=f'{l("copy")} {l("name")} {l("parameter")} (Ctrl+Shift+C)', command=lambda: copy_to_clipboard(master, reg_name))
                    menu.add_separator()
                    menu.add_command(label=f'{l("suspend_process_for_name")} {file_name}', command=lambda: action_process_by_name(file_name, 'suspend', DEBUG_MODE))
                    menu.add_command(label=f'{l("kill_process_for_name")} {file_name}', command=lambda: action_process_by_name(file_name, 'kill', DEBUG_MODE))
                    menu.add_separator()
                    menu.add_command(label=f'{l("delete")} {l("file")} {file_name}', command=lambda: confirm_and_delete_file(ARM_GUI_ELEMENTS, file_path_without_args, file_name, item_id))
                    menu.add_separator()
                    if item_data.get("value_type") not in [winreg.REG_NONE, None]:
                        menu.add_command(label=f'{l("change")} (E)', command=lambda: open_edit_dialog(ARM_GUI_ELEMENTS, item_data, item_id))
                    else:
                        menu.add_command(label=f'{l("change")} (E)', state=tk.DISABLED)

                elif current_tab == l("scheduler"):
                    task_name = item_data[l("name")]
                    task_path_full = item_data["TaskPath"]
                    task_action_path = item_data[l("path")]
                    is_enabled = item_data["Enabled_raw"]

                    file_name = extract_filename_from_path(task_action_path)

                    menu.add_command(label=f'{l("copy_path")} (Ctrl+C)', command=lambda: copy_to_clipboard(master, task_action_path))
                    menu.add_separator()

                    if is_enabled:
                        menu.add_command(label=f'{l("turn_off")} (O)', command=lambda: confirm_and_set_task_state(ARM_GUI_ELEMENTS, task_path_full, task_name, False, item_id))
                        menu.add_command(label=f'{l("turn_on")} (O)', state=tk.DISABLED)
                    else:
                        menu.add_command(label=f'{l("turn_off")} (O)', state=tk.DISABLED)
                        menu.add_command(label=f'{l("turn_on")} (O)', command=lambda: confirm_and_set_task_state(ARM_GUI_ELEMENTS, task_path_full, task_name, True, item_id))
                    menu.add_separator()
                    menu.add_command(label=f'{l("suspend_process_for_name")} {file_name}', command=lambda: action_process_by_name(file_name, 'suspend', DEBUG_MODE))
                    menu.add_command(label=f'{l("kill_process_for_name")} {file_name}', command=lambda: action_process_by_name(file_name, 'kill', DEBUG_MODE))
                    menu.add_separator()
                    menu.add_command(label=f'{l("delete")} {l("file")} {file_name}', command=lambda: confirm_and_delete_file(ARM_GUI_ELEMENTS, task_action_path, file_name, item_id))
                    menu.add_separator()
                    menu.add_command(label=f'{l("delete")} (Delete)', command=lambda: confirm_and_delete_task(ARM_GUI_ELEMENTS, task_path_full, task_name, item_id))

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        # Копируем текст в буфер обмена
        def copy_to_clipboard(master, text):
            master.clipboard_clear()
            master.clipboard_append(text)

        # Диалог редактирования
        def open_edit_dialog(ARM_GUI_ELEMENTS, item_data, item_id):
            master = ARM_GUI_ELEMENTS["master"]
            name = item_data[f'{l("name")} {l("parameter")}']
            current_value = str(item_data.get(f'{l("meaning")} {l("parameter")}', ""))
            reg_type = item_data["value_type"]
            hkey_const = item_data["hkey"]
            subkey_path = item_data["subkey"]

            if reg_type == winreg.REG_MULTI_SZ:
                current_value = "\n".join(item_data.get(f'{l("meaning")} {l("parameter")}', []))

            new_value = simpledialog.askstring(RS(),
                f'{l("editing")} {l("parameter")}:\n{name} ({REG_TYPE_MAP.get(reg_type, l("unknown"))})',
                initialvalue=current_value,
                parent=master
            )

            if new_value is not None:
                if update_reg_value(hkey_const, subkey_path, name, new_value, reg_type, item_id, ARM_GUI_ELEMENTS):
                    load_current_tab_data(ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS)

        # Подтверждение и удаление файла
        def confirm_and_delete_file(ARM_GUI_ELEMENTS, file_path, file_name, item_id):
            if delete_file(file_path, file_name):
                load_current_tab_data(ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS)

        # Подтверждение и удаление параметра реестра
        def confirm_and_delete_reg_value(ARM_GUI_ELEMENTS, item_data, item_id):
            name = item_data[f'{l("name")} {l("parameter")}']
            path = item_data[f'{l("path")} {l("parameter")}']
            hkey_const = item_data["hkey"]
            subkey_path = item_data["subkey"]

            if messagebox.askyesno(RS(), f'{l("delete_file?")}:\n{path}\\{name}?'):
                if delete_reg_value(hkey_const, subkey_path, name, item_id, ARM_GUI_ELEMENTS):
                    load_current_tab_data(ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS)

        # Диалог для создания нового параметра реестра
        def prompt_for_new_reg_value(ARM_GUI_ELEMENTS, hkey_const, subkey_path, reg_type_str):
            master = ARM_GUI_ELEMENTS["master"]
            name = simpledialog.askstring(RS(),
                f'{l("enter_new_name_key")} ({reg_type_str}) {l("for")}\n{ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}:',
                parent=master
            )
            if name:
                if create_reg_value(hkey_const, subkey_path, name, reg_type_str, ARM_GUI_ELEMENTS):
                    load_current_tab_data(ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS)

        # Подтверждение и изменение состояния задачи планировщика (Выкл или Вкл)
        def confirm_and_set_task_state(ARM_GUI_ELEMENTS, task_path_full, task_name, enable, item_id):
            if get_task_startup(task_path_full, enable, item_id, ARM_GUI_ELEMENTS):
                load_current_tab_data(ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS)

        # Подтверждение и удаление задачи планировщика
        def confirm_and_delete_task(ARM_GUI_ELEMENTS, task_path_full, task_name, item_id):
            if delete_task_scheduler_task(task_path_full, task_name, item_id, ARM_GUI_ELEMENTS):
                load_current_tab_data(ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS)

        # Вспомогательная функция для получения выбранного элемента
        def get_selected_item_data(ARM_GUI_ELEMENTS):
            tree = ARM_GUI_ELEMENTS["tree"]
            item_id = tree.focus()
            if not item_id:
                return None, None

            selected_values = tree.item(item_id, "values")
            current_cols = tree["columns"]

            item_data = next((data for data in ARM_GUI_ELEMENTS["treeview_data"] if [str(data.get(k, "")) for k in current_cols] == list(selected_values)), None)
            return item_id, item_data

        # Обработчик нажатия клавиш
        def handle_key_press(event, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS):
            item_id, item_data = get_selected_item_data(ARM_GUI_ELEMENTS)

            keysym = event.keysym
            current_tab = ARM_GUI_ELEMENTS["current_tab"]
            tree = ARM_GUI_ELEMENTS["tree"]

            ctrl_mask = 0x0004
            shift_mask = 0x0001
            is_ctrl = (event.state & ctrl_mask) != 0
            is_shift = (event.state & shift_mask) != 0

            sort_key_map = {
                "1": 0,
                "2": 1,
                "3": 2,
                "4": 3
            }

            if keysym in sort_key_map.keys() and not is_ctrl and not is_shift:
                column_index = sort_key_map[keysym]
                current_columns = tree["columns"]

                if column_index < len(current_columns):
                    column_id = current_columns[column_index]
                    sort_treeview_column(ARM_GUI_ELEMENTS, column_id)
                    return "break"

            if not item_data:
                return

            if keysym == "e" and not is_ctrl and current_tab not in [l("custom"), l("scheduler")]:
                if item_data.get("value_type") not in [winreg.REG_NONE, None]:
                    open_edit_dialog(ARM_GUI_ELEMENTS, item_data, item_id)
                return "break"

            elif keysym == "o" and not is_ctrl and current_tab == l("scheduler"):
                task_name = item_data[l("name")]
                task_path_full = item_data["TaskPath"]
                is_enabled = item_data["Enabled_raw"]
                confirm_and_set_task_state(ARM_GUI_ELEMENTS, task_path_full, task_name, not is_enabled, item_id)
                return "break"

            elif keysym == "Delete" and current_tab not in [l("system"), "AppInit_DLLs", "CmdLine"]:
                if current_tab == l("custom"):
                    confirm_and_delete_file(ARM_GUI_ELEMENTS, item_data[f'{l("path")} {l("parameter")}'], item_data[f'{l("name")} {l("file2")}'], item_id)
                elif current_tab == l("registry"):
                    confirm_and_delete_reg_value(ARM_GUI_ELEMENTS, item_data, item_id)
                elif current_tab == l("scheduler"):
                    confirm_and_delete_task(ARM_GUI_ELEMENTS, item_data["TaskPath"], item_data[l("name")], item_id)
                return "break"

            elif keysym == "c" and is_ctrl:
                if is_shift:
                    if current_tab != l("scheduler"):
                        name_key = f'{l("name")} {l("file2")}' if current_tab == l("custom") else f'{l("name")} {l("parameter")}'
                        copy_to_clipboard(ARM_GUI_ELEMENTS["master"], item_data.get(name_key, ""))
                else:
                    path_key = l("path") if current_tab == l("scheduler") else f'{l("path")} {l("parameter")}'
                    copy_to_clipboard(ARM_GUI_ELEMENTS["master"], item_data.get(path_key, ""))
                return "break"

        # Обработчик клавиши Menu
        def handle_menu_key(event, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS):
            item_id, item_data = get_selected_item_data(ARM_GUI_ELEMENTS)

            tree = ARM_GUI_ELEMENTS["tree"]
            x, y = 0, 0

            if item_id:
                bbox = tree.bbox(item_id)
                if bbox:
                    x = tree.winfo_rootx() + bbox[0]
                    y = tree.winfo_rooty() + bbox[1] + bbox[3]
                else:
                    x = tree.winfo_rootx() + 10
                    y = tree.winfo_rooty() + 10
            else:
                x = tree.winfo_rootx() + 10
                y = tree.winfo_rooty() + 10

            class MockEvent:
                def __init__(self, x_root, y_root):
                    self.x_root = x_root
                    self.y_root = y_root

            mock_event = MockEvent(x, y)
            show_context_menu(mock_event, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS, item_data, item_id)
            return "break"

        # Обработчик закрытия окна
        def on_closing():
            ARM_GUI_ELEMENTS["master"].destroy()

        ARM_GUI = tk.Tk()
        ARM_GUI_ELEMENTS["master"] = ARM_GUI
        ARM_GUI.title(RS())
        ARM_GUI.geometry("650x350")

        apply_global_theme(ARM_GUI, current_theme)

        # show_only_with_date = tk.BooleanVar(value=False)

        ARM_GUI.protocol("WM_DELETE_WINDOW", on_closing)

        ARM_GUI_ELEMENTS["current_tab"] = l("custom")
        ARM_GUI_ELEMENTS["treeview_data"] = []
        ARM_GUI_ELEMENTS["focus_after_update"] = None

        # menubar = tk.Menu(ARM_GUI)
        # view_menu = tk.Menu(menubar, tearoff=0)
        # view_menu.add_checkbutton(
        #     label=l('show_date'),
        #     variable=show_only_with_date,
        #     command=lambda: load_current_tab_data(ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS)
        # )

        # Пункт 'Вид' - Нерабочая фигня (сама сортировка по дате)
        # menubar.add_cascade(label=l('view'), menu=view_menu)

        create_menubar(ARM_GUI, RUN_IN_RECOVERY, DEBUG_MODE=DEBUG_MODE)

        ARM_GUI_ELEMENTS["notebook"] = ttk.Notebook(ARM_GUI)
        ARM_GUI_ELEMENTS["notebook"].pack(pady=10, padx=10, fill="both", expand=True)
        ARM_GUI_ELEMENTS["notebook"].bind("<<NotebookTabChanged>>", lambda e: on_tab_change(e, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS))

        tab_names = [l("custom"), l("registry"), l("system"), "AppInit_DLLs", "CmdLine", l("scheduler")]
        for tab_name in tab_names:
            frame = ttk.Frame(ARM_GUI_ELEMENTS["notebook"], padding="5 5 5 5")
            ARM_GUI_ELEMENTS["notebook"].add(frame, text=tab_name)
            ARM_GUI_ELEMENTS["tabs"][tab_name] = frame

        initial_frame = ARM_GUI_ELEMENTS["tabs"][l("custom")]
        ARM_GUI_ELEMENTS["tree"] = ttk.Treeview(initial_frame, selectmode="browse")
        ARM_GUI_ELEMENTS["vsb"] = ttk.Scrollbar(initial_frame, orient="vertical", command=ARM_GUI_ELEMENTS["tree"].yview)
        ARM_GUI_ELEMENTS["tree"].configure(yscrollcommand=ARM_GUI_ELEMENTS["vsb"].set)
        ARM_GUI_ELEMENTS["tree"].pack(side="left", fill="both", expand=True)
        ARM_GUI_ELEMENTS["vsb"].pack(side="right", fill="y")

        ARM_GUI_ELEMENTS["tree"].bind("<Button-3>", lambda e: handle_right_click(e, ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS))

        set_treeview_columns(ARM_GUI_ELEMENTS)
        load_current_tab_data(ARM_GUI_ELEMENTS, ARM_CORE_GLOBALS)

        ARM_GUI.mainloop()
    except Exception as e:
        logger.exception(l("arm_critical_error"))
        messagebox.showerror(RS(), f'{l("arm_critical_error")}\n{e}')

if __name__ == "__main__":
    from config import THEME, DEFAULT_THEME
    current_theme = THEME[DEFAULT_THEME]
    ARM(False, current_theme)

