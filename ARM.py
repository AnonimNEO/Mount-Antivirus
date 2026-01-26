#Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
#Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
#ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
#В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
#ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
#Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
#Или в файле COPYING.txt в архиве с установщиком
#Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
#Coded by @AnonimNEO (Telegram)

#Интерфейс
from tkinter import ttk, messagebox, simpledialog
import tkinter as tk
#Дата и Время
from datetime import datetime
#Логирование Ошибок
from loguru import logger
#Переменные среды
from pathlib import Path
#Работа с реестром
#import winreg as reg
import winreg
#Работа с файлами и ОС
import xml.etree.ElementTree as ET
import win32com.client
import os

from config import *
from RS import random_string
from OF import get_current_disc, get_offline_reg_path, loaded_hive_names

global ARM_data, autorun_master_version, REG_TYPE_MAP, REG_TYPE_MAP_REV, CREATABLE_REG_TYPES, ARM_CORE_GLOBALS, GUI_ELEMENTS, ultimate_load_cpu, ultimate_load_gpu, ultimate_load_ram, ultimate_load_lam
autorun_master_version = "3.2.3 Beta"

REG_TYPE_MAP = {
    winreg.REG_SZ: "REG_SZ",
    winreg.REG_EXPAND_SZ: "REG_EXPAND_SZ",
    winreg.REG_MULTI_SZ: "REG_MULTI_SZ",
    winreg.REG_DWORD: "REG_DWORD",
    winreg.REG_QWORD: "REG_QWORD",
    winreg.REG_BINARY: "REG_BINARY",
    winreg.REG_NONE: "REG_NONE"
}

#Обратное соответствие
REG_TYPE_MAP_REV = {v: k for k, v in REG_TYPE_MAP.items()}

#Список для диалога "Создать"
CREATABLE_REG_TYPES = [
    "REG_SZ", "REG_EXPAND_SZ", "REG_MULTI_SZ",
    "REG_DWORD", "REG_QWORD", "REG_BINARY"
]

GUI_ELEMENTS = {
    "master": None,
    "notebook": None,
    "tree": None,
    "tabs": {},
    "vsb": None,
    "current_tab": "Пользовательская",
    "treeview_data": [],
    "focus_after_update": None
}

#Класс для взаимодействия с Планировщиком Задач в обычной среде
class TaskSchedulerManager:
    def __init__(self):
        #Инициализация COM-объекта Планировщика Задач
        try:
            self.scheduler = win32com.client.Dispatch("Schedule.Service")
            self.scheduler.Connect()
            self.root_folder = self.scheduler.GetFolder("\\")
        except Exception as e:
            self.scheduler = None
            self.root_folder = None
            logger.error(f"ARM - Ошибка при подключении к COM-интерфейсу:\n{e}")
            messagebox.showerror(random_string(), f"Не удалось подключиться к Планировщику Задач.\n{e}")

    #Вспомогательная функция для получения каталога задач
    def get_folder(self, task_path):
        folder_path = os.path.dirname(task_path)
        if not folder_path:
            return self.root_folder

        try:
            return self.root_folder.GetFolder(folder_path)
        except Exception:
            return None

    #Вспомогательная функция для получения имени задачи
    #def get_name(self, task_path):
    #    return os.path.basename(task_path)

    #Вспомогательная функция для обхода всех задач в каталоге
    def traverse_folder(self, folder, all_tasks):
        if not folder:
            return

        #Получаем задачи в текущем каталоге
        tasks = folder.GetTasks(0)
        for task in tasks:
            all_tasks.append(task)

        #Рекурсивно обходим подкаталоги
        subfolders = folder.GetFolders(0)
        for subfolder in subfolders:
            self.traverse_folder(subfolder, all_tasks)

    #Получает список всех задач через COM-интерфейс
    def get_all_tasks(self):
        if not self.root_folder:
            return []

        all_com_tasks = []
        self.traverse_folder(self.root_folder, all_com_tasks)
        return all_com_tasks

    #Включает или отключает задачу через COM
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
        except Exception as e:
            logger.error(f"ARM - Ошибка изменения состояния COM-задачи {task_path_full}:\n{e}")
            return False

    #Удаляет задачу через COM
    def delete_task_com(self, task_path_full):
        if not self.scheduler:
            return False
        try:
            folder_path = os.path.dirname(task_path_full) or "\\"
            task_name = os.path.basename(task_path_full)
            folder = self.scheduler.GetFolder(folder_path)
            folder.DeleteTask(task_name, 0)
            return True
        except Exception as e:
            logger.error(f"ARM - Ошибка удаления COM-задачи {task_path_full}:\n{e}")
            return False



def ARM(run_in_recovery, first_run):
    #Путь к каталогу автозагрузки пользователя
    if run_in_recovery:
        current_disc, found_disc = get_current_disc(run_in_recovery)
        if not os.path.isfile(f"{current_disc}\\Users\\{default_user_name}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"):
            user_name = simpledialog.askstring(title=random_string(), prompt=f"Не найден пользователь {default_user_name}\nВведите нужное имя пользователя: ")
        else:
            user_name = default_user_name
        #Путь к каталогу автозагрузки оффлайн-системы
        user_startup_path_str = f"{current_disc}\\Users\\{user_name}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"
        user_startup = Path(user_startup_path_str)
    else:
        appdata_path = os.getenv("APPDATA")

        if appdata_path is not None:
            user_startup = Path(appdata_path) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        else:
            user_startup = f"C:\\Users\\{default_user_name}\\AppData\\Microsoft\\Windows\\Start Menu\\Program\\Startup\\"
            logger.error("ARM - Переменная среды APPDATA не найдена. Невозможно получить путь автозагрузки пользователя. Используется заглушка Path('.').")



    ARM_CORE_GLOBALS = {
        "user_startup_path": user_startup,
        "REG_KEYS": {
            "Пользовательская": None, #Для файлов
            "Реестр": [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "Run"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "RunOnce")
            ],
            "Системная": [
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon", "Shell"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon", "Userinit")
            ],
            "AppInit_DLLs": [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows", "AppInit_DLLs",
                 "x64"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows", "LoadAppInit_DLLs",
                 "x64"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows NT\CurrentVersion\Windows",
                 "AppInit_DLLs", "x32"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows NT\CurrentVersion\Windows",
                 "LoadAppInit_DLLs", "x32"),
            ],
            "CmdLine": [
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\Setup", "CmdLine"),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\Setup", "SetupType"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "EnableCursorSuppression"),
            ]
        },
        #Добавляем карту для преобразования констант HKEY_ в строки
        "HKEY_MAP": {
            winreg.HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT",
            winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
            winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
            winreg.HKEY_USERS: "HKEY_USERS",
            winreg.HKEY_CURRENT_CONFIG: "HKEY_CURRENT_CONFIG",
        },
        "OFFLINE_HKEY_MAP": {
            winreg.HKEY_LOCAL_MACHINE: (winreg.HKEY_LOCAL_MACHINE, loaded_hive_names["SOFTWARE"], r"Software"),
            #Для ключей, начинающихся с HKLM\Software
            #Ключи, не начинающиеся с HKLM\Software, не будут работать
            winreg.HKEY_CURRENT_USER: (winreg.HKEY_LOCAL_MACHINE, loaded_hive_names["USER"], None)
        }
    }

    try:
        #Форматируем Unix-таймштамп в читаемую строку
        def format_time(timestamp):
            if timestamp == 0:
                return "Ошибка"
            return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")



        #Получаем автозагрузку пользователя
        def get_user_startup(ARM_CORE_GLOBALS):
            user_startup_path = ARM_CORE_GLOBALS["user_startup_path"]
            ARM_data = []
            try:
                for item in user_startup_path.iterdir():
                    if item.is_file() and item.name.lower() != "desktop.ini":
                        try:
                            stats = item.stat()
                            ARM_data.append({
                                "Имя Файла": item.name,
                                "Дата создания": format_time(stats.st_ctime),
                                "Дата Изменения": format_time(stats.st_mtime),
                                "Дата Открытия": format_time(stats.st_atime),
                                "Путь Параметра": str(item)
                            })
                        except Exception as e:
                            logger.error(f"ARM - Ошибка при получении метаданных файла {item.name}:\n{e}")
                            ARM_data.append({
                                "Имя Файла": item.name,
                                "Дата создания": "Ошибка",
                                "Дата Изменения": "Ошибка",
                                "Дата Открытия": "Ошибка",
                                "Путь Параметра": str(item)
                            })
            except Exception as e:
                logger.error(f"ARM - Ошибка при доступе к папке автозагрузки пользователя:\n{e}")
                messagebox.showerror(random_string(), f"Не удалось получить доступ к папке автозагрузки.\n{e}")
            return ARM_data



        #Получаем данные из заданного ключа реестра
        def read_registry_key(ARM_CORE_GLOBALS, hkey_const, subkey_path):
            hkey_map = ARM_CORE_GLOBALS["HKEY_MAP"]

            ARM_data = []

            if run_in_recovery:
                #Получаем реальный путь к кусту в оффлайн-режиме
                final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, run_in_recovery)
            else:
                final_hkey = hkey_const
                final_subkey = subkey_path

            #Используем исходную HKEY для отображения
            hkey_name = hkey_map.get(hkey_const, str(hkey_const))
            full_path = f"{hkey_name}\\{subkey_path}"

            try:
                #Открываем ключ для чтения
                with winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            #Перечисляем значения в ключе
                            value_name, value, reg_type = winreg.EnumValue(key, i)
                            ARM_data.append({
                                "Имя Параметра": value_name,
                                "Значение Параметра": str(value),
                                "Тип Параметра": REG_TYPE_MAP.get(reg_type),
                                "Путь Параметра": full_path, #Сохраняем исходный путь для отображения
                                "hkey": hkey_const, #Сохраняем исходную константу
                                "subkey": subkey_path, #Сохраняем исходный путь
                                "value_type": reg_type
                            })
                            i += 1
                        except OSError: #Ошибка возникает, когда перебраны все значения
                            break
            except FileNotFoundError:
                logger.warning(f"ARM - Ключ реестра не найден: {full_path}")
            except Exception as e:
                logger.error(f"ARM - Ошибка при считывании ключа реестра {full_path}:\n{e}")
            return ARM_data



        #Получаем данные из ключей Run и RunOnce пользователя
        def get_registry_startup(ARM_CORE_GLOBALS):
            reg_keys = ARM_CORE_GLOBALS["REG_KEYS"]
            all_data = []
            #Перебираем все ключи в списке "Реестр"
            for hkey_const, subkey_path, _ in reg_keys["Реестр"]:
                all_data.extend(read_registry_key(ARM_CORE_GLOBALS, hkey_const, subkey_path))
            return all_data



        #Получаем значения Shell и Userinit из Winlogon
        def get_system_startup(ARM_CORE_GLOBALS):
            reg_keys = ARM_CORE_GLOBALS["REG_KEYS"]
            hkey_map = ARM_CORE_GLOBALS["HKEY_MAP"]
            ARM_data = []
            for hkey_const, subkey_path, value_name in reg_keys["Системная"]:
                
                if run_in_recovery:
                    final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, run_in_recovery)
                else:
                    final_hkey = hkey_const
                    final_subkey = subkey_path

                hkey_name = hkey_map.get(hkey_const, str(hkey_const))
                full_path = f"{hkey_name}\\{subkey_path}" 

                try:
                    with winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_READ) as key:
                        value, reg_type = winreg.QueryValueEx(key, value_name)
                        ARM_data.append({
                            "Имя Параметра": value_name,
                            "Значение Параметра": str(value),
                            "Тип Параметра": REG_TYPE_MAP.get(reg_type),
                            "Путь Параметра": full_path,
                            "hkey": hkey_const,
                            "subkey": subkey_path,
                            "value_type": reg_type
                        })
                except Exception as e:
                    logger.error(f"ARM - Ошибка при считывании системного параметра {value_name} из {full_path}:\n{e}")
                    ARM_data.append({
                        "Имя Параметра": value_name,
                        "Значение Параметра": "Ошибка",
                        "Тип Параметра": "Ошибка",
                        "Путь Параметра": full_path,
                        "hkey": hkey_const,
                        "subkey": subkey_path,
                        "value_type": winreg.REG_NONE
                    })
            return ARM_data



        #Получаем значения параметров AppInit_DLLs и LoadAppInit_DLLs
        def get_dll_startup(ARM_CORE_GLOBALS):
            reg_keys = ARM_CORE_GLOBALS["REG_KEYS"]
            hkey_map = ARM_CORE_GLOBALS["HKEY_MAP"]
            ARM_data = []
            for hkey_const, subkey_path, value_name, bitness in reg_keys["AppInit_DLLs"]:
                if run_in_recovery:
                    final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, run_in_recovery)
                else:
                    final_hkey = hkey_const
                    final_subkey = subkey_path

                #преобразование HKEY_const в имя:
                hkey_name = hkey_map.get(hkey_const, str(hkey_const))
                full_path = f"{hkey_name}\\{subkey_path}"
                try: #Используем KEY_READ | winreg.KEY_WOW64_64KEY для 64-битного представления
                    access = winreg.KEY_READ
                    #При работе с загруженным кустом, KEY_WOW64_32KEY не нужен,
                    #так как мы обращаемся напрямую к 32-битному пути (Wow6432Node)
                    #Но сохраним проверку для совместимости
                    if bitness == "x64":
                        pass
                    elif bitness == "x32":
                        access |= winreg.KEY_WOW64_32KEY

                    with winreg.OpenKey(final_hkey, final_subkey, 0, access) as key:
                        value, reg_type = winreg.QueryValueEx(key, value_name)
                        ARM_data.append({
                            "Имя Параметра": value_name,
                            "Битность": bitness,
                            "Значение Параметра": str(value),
                            "Тип Параметра": REG_TYPE_MAP.get(reg_type),
                            "Путь Параметра": full_path,
                            "hkey": hkey_const,
                            "subkey": subkey_path,
                            "value_type": reg_type
                        })
                except FileNotFoundError as e:
                    logger.error(f"ARM - Не найден параметр реестра AppInit_DLLs{value_name} ({bitness}) из {full_path}:\n{e}")
                    ARM_data.append({
                        "Имя Параметра": value_name,
                        "Битность": bitness,
                        "Значение Параметра": "Параметр Отсутствует",
                        "Тип Параметра": "REG_NONE",
                        "Путь Параметра": full_path,
                        "hkey": hkey_const,
                        "subkey": subkey_path,
                        "value_type": winreg.REG_NONE
                    })
                except Exception as e:
                    logger.error(f"ARM - Ошибка при считывании параметра AppInit_DLLs{value_name} ({bitness}) из {full_path}:\n{e}")
                    ARM_data.append({
                        "Имя Параметра": value_name,
                        "Битность": bitness,
                        "Значение Параметра": "Ошибка",
                        "Тип Параметра": "Ошибка",
                        "Путь Параметра": full_path,
                        "hkey": hkey_const,
                        "subkey": subkey_path,
                        "value_type": winreg.REG_NONE
                    })
            return ARM_data


        #Получаем значения параметров для вкладки CmdLine
        def get_cmdline_startup(ARM_CORE_GLOBALS):
            reg_keys = ARM_CORE_GLOBALS["REG_KEYS"]
            hkey_map = ARM_CORE_GLOBALS["HKEY_MAP"]
            ARM_data = []
            for hkey_const, subkey_path, value_name in reg_keys["CmdLine"]:
                if run_in_recovery:
                    final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, run_in_recovery)
                else:
                    final_hkey = hkey_const
                    final_subkey = subkey_path

                hkey_name = hkey_map.get(hkey_const, str(hkey_const))
                full_path = f"{hkey_name}\\{subkey_path}"

                try:
                    with winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_READ) as key:
                        value, reg_type = winreg.QueryValueEx(key, value_name)
                        ARM_data.append({
                            "Имя Параметра": value_name,
                            "Значение Параметра": str(value),
                            "Тип Параметра": REG_TYPE_MAP.get(reg_type),
                            "Путь Параметра": full_path,
                            "hkey": hkey_const,
                            "subkey": subkey_path,
                            "value_type": reg_type
                        })
                except Exception as e:
                    logger.error(f"ARM - Ошибка при считывании параметра {value_name} из {full_path}:\n{e}")
                    ARM_data.append({
                        "Имя Параметра": value_name,
                        "Значение Параметра": "Ошибка или отсутствует",
                        "Тип Параметра": "Ошибка",
                        "Путь Параметра": full_path,
                        "hkey": hkey_const,
                        "subkey": subkey_path,
                        "value_type": winreg.REG_NONE
                    })
            return ARM_data



        #Создаём новый параметр реестра
        def create_reg_value(hkey_const, subkey_path, name, reg_type_str, gui_elements):
            reg_type = REG_TYPE_MAP_REV.get(reg_type_str)
            if reg_type is None:
                logger.error(f"ARM - Неизвестный тип реестра: {reg_type_str}")
                return False

            if reg_type in (winreg.REG_SZ, winreg.REG_EXPAND_SZ, winreg.REG_MULTI_SZ):
                initial_value = ""
            elif reg_type in (winreg.REG_DWORD, winreg.REG_QWORD):
                initial_value = 0
            elif reg_type == winreg.REG_BINARY:
                initial_value = b""
            else:
                initial_value = ""

            if run_in_recovery:
                final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, run_in_recovery)
            else:
                final_hkey = hkey_const
                final_subkey = subkey_path

            try:
                with winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ) as key:
                    winreg.SetValueEx(key, name, 0, reg_type, initial_value)
                    logger.success(f"ARM - Создан параметр реестра: {name} с типом {reg_type_str} в {ARM_CORE_GLOBALS['HKEY_MAP'].get(hkey_const)}\\{subkey_path}")
                    gui_elements["focus_after_update"] = {"type": "name", "value": name}
                    return True
            except PermissionError:
                messagebox.showerror(random_string(), "Недостаточно прав для изменения реестра. Требуются права администратора.")
                return False
            except Exception as e:
                logger.error(f"ARM - Ошибка при создании параметра реестра: {name} в {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}:\n{e}")
                messagebox.showerror(random_string(), f'Не удалось создать параметр реестра "{name}".\n{e}')
                return False



        #Обновляем существующий параметр реестра
        def update_reg_value(hkey_const, subkey_path, name, new_value, reg_type, item_id, gui_elements):
            if run_in_recovery:
                final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, run_in_recovery)
            else:
                final_hkey = hkey_const
                final_subkey = subkey_path

            try:
                #Преобразование значения в нужный тип
                if reg_type in (winreg.REG_DWORD, winreg.REG_QWORD):
                    try:
                        value_to_set = int(new_value)
                    except ValueError:
                        raise ValueError(f"ARM - Некорректное числовое значение для типа {REG_TYPE_MAP.get(reg_type, 'неизвестный')}")

                elif reg_type == winreg.REG_MULTI_SZ:
                    value_to_set = new_value.split("\n")

                elif reg_type == winreg.REG_BINARY:
                    try:
                        hex_string = new_value.replace(" ", "")
                        if len(hex_string) % 2 != 0:
                            hex_string = "0" + hex_string

                        value_to_set = bytes.fromhex(hex_string)
                    except ValueError as e:
                        raise ValueError(f"ARM - Некорректная шестнадцатеричная строка для REG_BINARY.\n{e}")

                else:
                    value_to_set = new_value

                with winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name, 0, reg_type, value_to_set)
                    logger.success(f"ARM - Обновлен параметр реестра: {name} в {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}")
                    gui_elements["focus_after_update"] = {"type": "iid", "value": item_id}
                    return True

            except PermissionError:
                messagebox.showerror(random_string(), "Недостаточно прав для изменения реестра. Требуются права администратора.")
                return False
            except ValueError as e:
                logger.error(f"ARM - Ошибка преобразования значения для параметра реестра: {name} в {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}:\n{e}")
                return False
            except Exception as e:
                messagebox.showerror(random_string(), f"Не удалось обновить параметр реестра '{name}'.\n{e}")
                logger.error(f"ARM - Ошибка при обновлении параметра реестра: {name} в {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}:\n{e}")
                return False



        #Удаляем параметр реестра
        def delete_reg_value(hkey_const, subkey_path, name, item_id, gui_elements):
            if run_in_recovery:
                final_hkey, final_subkey = get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, run_in_recovery)
            else:
                final_hkey = hkey_const
                final_subkey = subkey_path
            try:
                gui_elements["focus_after_update"] = get_next_item_iid(gui_elements, item_id)

                with winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
                    logger.success(f"ARM - Удален параметр реестра: {name} из {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}")
                    return True
            except PermissionError:
                messagebox.showerror(random_string(), "Недостаточно прав для удаления из реестра. Требуются права администратора.")
                logger.error(f"ARM - Ошибка доступа при удалении параметра реестра: {name} из {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}")
                return False
            except Exception as e:
                messagebox.showerror(random_string(), f"Не удалось удалить параметр реестра '{name}'.\n{e}")
                logger.error(f"ARM - Ошибка при удалении параметра реестра: {name} из {ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}:\n{e}")
                return False



        #Удаляем файл
        def delete_file(file_path, file_name, item_id, gui_elements):
            file = Path(file_path)
            try:
                if file.exists():
                    gui_elements["focus_after_update"] = get_next_item_iid(gui_elements, item_id)
                    file.unlink()
                    logger.success(f"ARM - Удален файл: {file_path}")
                    return True
                return False
            except PermissionError:
                messagebox.showerror(random_string(), "Недостаточно прав для удаления файла.")
                logger.error(f"ARM - Ошибка доступа при удалении файла: {file_path}")
                return False
            except Exception as e:
                messagebox.showerror(random_string(), f"Не удалось удалить файл '{file.name}'.\n{e}")
                logger.error(f"ARM - Ошибка при удалении файла: {file_path}:\n{e}")
                return False



        #Вспомогательная функция для получения пути к папке задач
        def get_tasks_directory():
            #Если режим восстановления - используем букву вмонтированного диска
            if run_in_recovery:
                return Path(f"{current_disc}Windows\\System32\\Tasks")
            #Если обычная система - берем системный путь через переменную окружения
            return Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32" / "Tasks"



        #Вспомогательная функция для удаления пространства имен из тегов XML
        def strip_namespace(tag):
            if "}" in tag:
                return tag.split('}', 1)[1]
            return tag



        #Сохраняем кодировки UTF-16
        def save_xml_task(tree, file_path):
            try:
                #Windows Tasks часто требуют UTF-16 LE и BOM
                with open(file_path, "wb") as f:
                    tree.write(f, encoding="utf-16", xml_declaration=True)
                return True
            except Exception as e:
                logger.error(f"ARM - Ошибка сохранения XML задачи {file_path}:\n{e}")
                return False



        #Получаем Автозагрузку из Планировщика Задач (Универсальный метод через XML ИЛИ COM)
        def get_task_scheduler_startup():
            ARM_data = []

            if not run_in_recovery:
                manager = TaskSchedulerManager()
                com_tasks = manager.get_all_tasks()

                for task in com_tasks:
                    try:
                        #Получаем полный путь задачи
                        full_path = task.Path 
                        name = os.path.basename(full_path)
                        is_enabled = task.Enabled

                        #Попытка получить действие (Command)
                        action_path = "Нет ExecAction"
                        definition = task.Definition

                        for action in definition.Actions:
                            #TASK_ACTION_EXEC = 0 (константа COM)
                            if action.Type == 0: 
                                cmd = action.Path
                                args = action.Arguments
                                action_path = f"{cmd} {args}".strip()
                                break

                        #Получаем автора
                        author = definition.RegistrationInfo.Author

                        #Получаем дату создания
                        try:
                            date_created = str(task.Definition.RegistrationInfo.Date)
                        except Exception:
                            date_created = "01-01-1970 00:00:00"

                        action_path = "Неизвестно"
                        if task.Definition.Actions.Count > 0:
                            action = task.Definition.Actions.Item(1)
                            if action.Type == 0:
                                #Извлекаем путь к исполняемому файлу из свойства Path самого действия
                                raw_path = getattr(action, "Path", "Неизвестно")
                                if raw_path != "Неизвестно":
                                    action_path = os.path.abspath(raw_path)
            
                        ARM_data.append({
                            "Имя": name,
                            "Вкл/Выкл": "Включен" if is_enabled else "Отключен",
                            "Путь": action_path,
                            "Автор": author,
                            "Дата создания": date_created,
                            "TaskPath": full_path, 
                            "Enabled_raw": is_enabled
                        })
                    except Exception as e:
                        logger.error(f"ARM - Ошибка обработки COM-задачи {task.Path}:\n{e}")
                        ARM_data.append({
                            "Имя": task.Path,
                            "Вкл/Выкл": "Ошибка",
                            "Путь": "Ошибка чтения",
                            "Автор": "Ошибка",
                            "Дата создания": None,
                            "TaskPath": task.Path,
                            "Enabled_raw": False
                        })
                return ARM_data

            else:
                tasks_dir = get_tasks_directory()

                if not tasks_dir.exists():
                    logger.error(f"ARM - Папка задач не найдена: {tasks_dir}")
                    return ARM_data

                for root, _, files in os.walk(tasks_dir):
                    for file_name in files:
                        file_path = Path(root) / file_name

                        try:
                            #Парсим XML файл
                            tree = ET.parse(file_path)
                            xml_root = tree.getroot()

                            #Инициализируем переменные по умолчанию
                            name = file_name
                            is_enabled = True #По умолчанию задачи включены, если тег отсутствует
                            action_path = "Нет ExecAction"
                            author = "Система/Неизвестно"

                            #Проходим по дереву XML
                            #Так как namespace может меняться, ищем локальные имена тегов
                            for elem in xml_root.iter():
                                tag = strip_namespace(elem.tag)

                                if tag == "Author":
                                    author = elem.text if elem.text else author

                                elif tag == "Enabled":
                                    #Если текст "false", то задача выключена
                                    if elem.text and elem.text.lower() == "false":
                                        is_enabled = False

                                elif tag == "Command":
                                    #Ищем исполняемую команду
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
                                        break #Берем первое действие

                            ARM_data.append({
                                "Имя": name,
                                "Вкл/Выкл": "Включен" if is_enabled else "Отключен",
                                "Путь": action_path,
                                "Автор": author,
                                "TaskPath": str(file_path), #Полный путь к файлу XML
                                "Enabled_raw": is_enabled
                            })

                        except ET.ParseError:
                            #Это не XML или файл поврежден
                            continue
                        except Exception as e:
                            logger.error(f"ARM - Ошибка обработки файла задачи {file_name}:\n{e}")
                            ARM_data.append({
                                "Имя": file_name,
                                "Вкл/Выкл": "Ошибка",
                                "Путь": "Ошибка чтения",
                                "Автор": "Ошибка",
                                "TaskPath": str(file_path),
                                "Enabled_raw": False
                            })
                return ARM_data



        #Изменяем состояние задачи (Вкл/Выкл)
        def get_task_startup(task_path_str, enable, item_id, gui_elements):
            if not run_in_recovery:
                manager = TaskSchedulerManager()
                if manager.set_task_state_com(task_path_str, enable):
                    state = "включена" if enable else "отключена"
                    logger.success(f'ARM - Задача "{task_path_str}" успешно {state} через COM.')
                    gui_elements["focus_after_update"] = {"type": "iid", "value": item_id}
                    return True
                return False
            else: 
                task_path = Path(task_path_str)
                if not task_path.exists():
                    messagebox.showerror(random_string(), f"Файл задачи не найден:\n{task_path}")
                    return False
                try:
                    #Регистрируем все пространства имен для сохранения префиксов
                    ET.register_namespace('', "http://schemas.microsoft.com/windows/2004/02/mit/task")
                    tree = ET.parse(task_path)
                    root = tree.getroot()

                    ns = ""
                    if '}' in root.tag:
                        ns = root.tag.split('}')[0] + '}'

                    settings = root.find(f"{ns}Settings")
                    if settings is None:
                        settings = ET.SubElement(root, f"{ns}Settings")

                    enabled_tag = settings.find(f"{ns}Enabled")
                    if enabled_tag is None:
                        enabled_tag = ET.SubElement(settings, f"{ns}Enabled")

                    enabled_tag.text = "true" if enable else "false"

                    if save_xml_task(tree, task_path):
                        state = "включена" if enable else "отключена"
                        logger.success(f'ARM - Задача "{task_path.name}" успешно {state} через XML.')
                        gui_elements["focus_after_update"] = {"type": "iid", "value": item_id}
                        return True
                    return False
                except Exception as e:
                    logger.error(f"ARM - Ошибка XML:\n{e}")
                    messagebox.showerror(random_string(), f"Ошибка XML:\n{e}")
                    return False



        #Удаляем задачу из планировщика
        def delete_task_scheduler_task(task_path_str, task_name, item_id, gui_elements):
            if not run_in_recovery:
                manager = TaskSchedulerManager()
                if manager.delete_task_com(task_path_str):
                    logger.success(f'ARM - Задача "{task_path_str}" удалена через COM.')
                    gui_elements["focus_after_update"] = get_next_item_iid(gui_elements, item_id)
                    return True
                return False
            else: 
                try:
                    task_path = Path(task_path_str)
                    if task_path.exists():
                        gui_elements["focus_after_update"] = get_next_item_iid(gui_elements, item_id)
                        task_path.unlink()
                        logger.success(f"ARM - XML файл задачи удален: {task_path}")
                        return True
                    else:
                        messagebox.showerror(random_string(), "Файл задачи уже отсутствует.")
                        return False
                except Exception as e:
                    logger.error(f"ARM - Ошибка удаления XML файла:\n{e}")
                    messagebox.showerror(random_string(), f"Не удалось удалить файл:\n{e}")
                    return False



        #О Программе
        def about_ARM():
            messagebox.showinfo(random_string(), f"Мастер Автозагрузки - {autorun_master_version}")



        #Обработка смены вкладки
        def on_tab_change(event, gui_elements, ARM_CORE_GLOBALS):
            selected_tab = gui_elements["notebook"].tab(gui_elements["notebook"].select(), "text")
            if selected_tab != gui_elements["current_tab"]:
                gui_elements["current_tab"] = selected_tab
                set_treeview_columns(gui_elements)
                load_current_tab_data(gui_elements, ARM_CORE_GLOBALS)



        #Функция для преобразования типов
        def _to_sortable_type(val):
            try:
                #Попытка преобразовать в число
                return float(val)
            except (ValueError, TypeError):
                #Иначе вернуть как строку в нижнем регистре
                return str(val).lower()



        #Сортируем столбик по клику на заголовок
        def sort_treeview_column(gui_elements, col):
            tree = gui_elements.get("tree")
            if not tree:
                return

            items = tree.get_children("") 
            if not items:
                return

            gui_elements.setdefault("sort_direction", {})
            reverse = gui_elements["sort_direction"].get(col, "asc") == "desc"
            gui_elements["sort_direction"][col] = "desc" if not reverse else "asc"

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
            current_text = tree.heading(col, "text")
            tree.heading(col, text=current_text + arrow)



        #Обработчик события получения фокуса Treeview
        def handle_treeview_focus_in(gui_elements):
            tree = gui_elements.get("tree")
            if not tree:
                return

            items = tree.get_children("")

            if items:
                if not tree.selection():
                    first_item = items[0]
                    tree.selection_set(first_item)
                    tree.focus(first_item)



        #Установка столбиков, в зависимости от вкладки
        def set_treeview_columns(gui_elements):
            if gui_elements["tree"] and gui_elements["tree"].winfo_exists():
                gui_elements["tree"].destroy()

            current_frame = gui_elements["tabs"][gui_elements["current_tab"]]

            if gui_elements["vsb"] and gui_elements["vsb"].winfo_exists():
                gui_elements["vsb"].pack_forget()

            gui_elements["tree"] = ttk.Treeview(current_frame, selectmode="browse")
            gui_elements["tree"].pack(side="left", fill="both", expand=True)

            gui_elements["vsb"] = ttk.Scrollbar(current_frame, orient="vertical", command=gui_elements["tree"].yview)
            gui_elements["vsb"].pack(side="right", fill="y")
            gui_elements["tree"].configure(yscrollcommand=gui_elements["vsb"].set)

            gui_elements["tree"].bind("<Button-3>", lambda e: handle_right_click(e, gui_elements, ARM_CORE_GLOBALS))
            gui_elements["tree"].bind("<Key>", lambda e: handle_key_press(e, gui_elements, ARM_CORE_GLOBALS))
            gui_elements["tree"].bind("<c>", lambda e: handle_menu_key(e, gui_elements, ARM_CORE_GLOBALS))

            gui_elements["tree"].bind("<FocusIn>", lambda e: handle_treeview_focus_in(gui_elements))

            columns = []
            headings = {}

            if gui_elements["current_tab"] == "Пользовательская":
                columns = ("Имя Файла", "Дата создания", "Дата Изменения", "Дата Открытия")
                headings = dict(zip(columns, columns))
            elif gui_elements["current_tab"] == "Реестр":
                columns = ("Имя Параметра", "Значение Параметра", "Тип Параметра", "Путь Параметра")
                headings = dict(zip(columns, columns))
            elif gui_elements["current_tab"] == "Системная":
                columns = ("Имя Параметра", "Значение Параметра", "Тип Параметра", "Путь Параметра")
                headings = dict(zip(columns, columns))
            elif gui_elements["current_tab"] == "AppInit_DLLs":
                columns = ["Имя Параметра", "Битность", "Значение Параметра", "Путь Параметра"]
                headings = dict(zip(columns, columns))
            elif gui_elements["current_tab"] == "CmdLine":
                columns = ("Имя Параметра", "Значение Параметра", "Тип Параметра", "Путь Параметра")
                headings = dict(zip(columns, columns))
            elif gui_elements["current_tab"] == "Планировщик":
                columns = ("Имя", "Вкл/Выкл", "Путь", "Автор")
                headings = dict(zip(columns, columns))

            gui_elements["tree"]["columns"] = columns
            gui_elements["tree"]["show"] = "headings"

            for col in columns:
                gui_elements["tree"].heading(
                    col, 
                    text=headings.get(col, col),
                    command=lambda _col=col: sort_treeview_column(gui_elements, _col)
                )
                gui_elements["tree"].column(col, width=100, anchor=tk.W)

            if columns:
                gui_elements["tree"].column(columns[0], width=150, anchor=tk.W)
                if gui_elements["current_tab"] == "AppInit_DLLs":
                        gui_elements["tree"].column(columns[0], width=75, anchor=tk.W)
                        gui_elements["tree"].column(columns[1], width=15, anchor=tk.W)
                        gui_elements["tree"].column(columns[2], width=150, anchor=tk.W)
                        gui_elements["tree"].column(columns[3], width=75, anchor=tk.W)
                if gui_elements["current_tab"] in ["Реестр", "Системная", "CmdLine"]:
                        gui_elements["tree"].column(columns[0], width=100, anchor=tk.W)
                        gui_elements["tree"].column(columns[1], width=250, anchor=tk.W)
                        gui_elements["tree"].column(columns[2], width=50, anchor=tk.W)
                        gui_elements["tree"].column(columns[3], width=75, anchor=tk.W)
                if gui_elements["current_tab"] == "Планировщик":
                    gui_elements["tree"].column(columns[0], width=175, anchor=tk.W)
                    gui_elements["tree"].column(columns[1], width=65, anchor=tk.W)
                    gui_elements["tree"].column(columns[2], width=300, anchor=tk.W)
                    gui_elements["tree"].column(columns[3], width=50, anchor=tk.W)



        #Воссанавливываем фокус после обновления данных
        def restore_focus_after_update(gui_elements):
            tree = gui_elements["tree"]
            focus_info = gui_elements["focus_after_update"]
            gui_elements["focus_after_update"] = None

            if focus_info:
                target_iid = None

                if focus_info["type"] == "iid":
                    if tree.exists(focus_info["value"]):
                        target_iid = focus_info["value"]

                elif focus_info["type"] == "name":
                    name_to_find = focus_info["value"]
                    current_cols = tree["columns"]
                    name_col_index = current_cols.index("Имя Параметра") if "Имя Параметра" in current_cols else -1

                    if name_col_index != -1:
                        for item_id in tree.get_children(""):
                            values = tree.item(item_id, 'values')
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



        #Загружаем данные для активной вкладки и заполняем таблицу
        def load_current_tab_data(gui_elements, ARM_CORE_GLOBALS):
            tree = gui_elements["tree"]
            current_tab = gui_elements["current_tab"]

            for item in tree.get_children():
                tree.delete(item)

            if current_tab == "Пользовательская":
                gui_elements["treeview_data"] = get_user_startup(ARM_CORE_GLOBALS)
                columns = ["Имя Файла", "Дата создания", "Дата Изменения", "Дата Открытия"]
            elif current_tab == "Реестр":
                gui_elements["treeview_data"] = get_registry_startup(ARM_CORE_GLOBALS)
                columns = ["Имя Параметра", "Значение Параметра", "Тип Параметра", "Путь Параметра"]
            elif current_tab == "Системная":
                gui_elements["treeview_data"] = get_system_startup(ARM_CORE_GLOBALS)
                columns = ["Имя Параметра", "Значение Параметра", "Тип Параметра", "Путь Параметра"]
            elif current_tab == "AppInit_DLLs":
                gui_elements["treeview_data"] = get_dll_startup(ARM_CORE_GLOBALS)
                columns = ["Имя Параметра", "Битность", "Значение Параметра", "Путь Параметра"]
            elif current_tab == "CmdLine":
                if first_run:
                    messagebox.showinfo(random_string(), "В этой вкладке можно сразу включить отображение курсора в CmdLine.")
                gui_elements["treeview_data"] = get_cmdline_startup(ARM_CORE_GLOBALS)
                columns = ["Имя Параметра", "Значение Параметра", "Тип Параметра", "Путь Параметра"]
            elif current_tab == "Планировщик":
                if first_run:
                    messagebox.showinfo(random_string(), 'Во вкладке планировщик отображается так много задач, потому что вирусы могли модернизировать задачи, но такое крайне редко, поэтому вы можете отключить отображение задач без графа "создан". Для этого нажмите пункты в верхней панели окна: вид->Показывать только задачи с датой.')

                raw_tasks = get_task_scheduler_startup()
                
                if show_only_with_date.get():
                    gui_elements["treeview_data"] = [
                        t for t in raw_tasks 
                        if t.get("Дата создания") and t.get("Дата создания") not in ["", "Ошибка", "01-01-1970 00:00:00"]
                    ]
                else:
                    gui_elements["treeview_data"] = raw_tasks
                    
                columns = ["Имя", "Вкл/Выкл", "Путь", "Автор"]
            else:
                gui_elements["treeview_data"] = []
                columns = []

            for item_data in gui_elements["treeview_data"]:
                values = [item_data.get(col, "") for col in columns]
                unique_id = item_data.get("TaskPath") or str(hash(frozenset(item_data.items())))
                tree.insert("", "end", values=values, tags=("ARM_data",), iid=unique_id, open=True)

            restore_focus_after_update(gui_elements)



        #Вспомогательная функция для получения iid ближайшего элемента
        def get_next_item_iid(gui_elements, current_item_id):
            tree = gui_elements["tree"]
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



        #Контекстное Меню
        def show_context_menu(event, gui_elements, ARM_CORE_GLOBALS, item_data, item_id):
            master = gui_elements["master"]
            current_tab = gui_elements["current_tab"]
            reg_keys = ARM_CORE_GLOBALS["REG_KEYS"]

            menu = tk.Menu(master, tearoff=0)

            if current_tab != "Системная" and current_tab != "Пользовательская" and current_tab != "Планировщик" and current_tab != "CmdLine":
                create_menu = tk.Menu(menu, tearoff=0)

                if current_tab in ["Реестр", "AppInit_DLLs"]:
                    if current_tab == "Реестр":
                        hkey_const, subkey_path, _ = reg_keys["Реестр"][0]
                    elif current_tab == "AppInit_DLLs":
                        hkey_const, subkey_path, _, _ = reg_keys["AppInit_DLLs"][0]

                    for reg_type_str in CREATABLE_REG_TYPES:
                        create_menu.add_command(
                            label=f"Параметр {reg_type_str}",
                            command=lambda type=reg_type_str: prompt_for_new_reg_value(gui_elements, hkey_const, subkey_path, type)
                        )
                    menu.add_cascade(label="Создать", menu=create_menu)
                    menu.add_separator()

            if item_data:
                if current_tab == "Пользовательская":
                    file_path = item_data["Путь Параметра"]
                    file_name = item_data["Имя Файла"]

                    menu.add_command(label="Копировать Путь (Ctrl+C)", command=lambda: copy_to_clipboard(master, file_path))
                    menu.add_command(label="Копировать имя файла (Ctrl+Shift+C)", command=lambda: copy_to_clipboard(master, file_name))
                    menu.add_separator()
                    menu.add_command(label="Удалить Файл (Delete)", command=lambda: confirm_and_delete_file(gui_elements, file_path, file_name, item_id))

                elif current_tab in ["Реестр", "Системная", "AppInit_DLLs", "CmdLine"]:
                    reg_name = item_data["Имя Параметра"]
                    reg_path = item_data["Путь Параметра"]

                    menu.add_command(label="Копировать путь (Ctrl+C)", command=lambda: copy_to_clipboard(master, reg_path))
                    menu.add_command(label="Копировать имя параметра (Ctrl+Shift+C)", command=lambda: copy_to_clipboard(master, reg_name))
                    menu.add_separator()

                    if item_data.get("value_type") not in [winreg.REG_NONE, None]:
                        menu.add_command(label="Изменить (E)", command=lambda: open_edit_dialog(gui_elements, item_data, item_id))
                    else:
                         menu.add_command(label="Изменить (E)", state=tk.DISABLED)

                    if current_tab == "Реестр":
                        menu.add_command(label="Удалить Параметр (Delete)", command=lambda: confirm_and_delete_reg_value(gui_elements, item_data, item_id))

                elif current_tab == "Планировщик":
                    task_name = item_data["Имя"]
                    task_path_full = item_data["TaskPath"]
                    task_action_path = item_data["Путь"]
                    is_enabled = item_data["Enabled_raw"]

                    menu.add_command(label="Скопировать Путь (Ctrl+C)", command=lambda: copy_to_clipboard(master, task_action_path))
                    menu.add_separator()

                    if is_enabled:
                        menu.add_command(label="Отключить (O)", command=lambda: confirm_and_set_task_state(gui_elements, task_path_full, task_name, False, item_id))
                        menu.add_command(label="Включить (O)", state=tk.DISABLED)
                    else:
                        menu.add_command(label="Отключить (O)", state=tk.DISABLED)
                        menu.add_command(label="Включить (O)", command=lambda: confirm_and_set_task_state(gui_elements, task_path_full, task_name, True, item_id))
                    menu.add_separator()
                    menu.add_command(label="Удалить (Delete)", command=lambda: confirm_and_delete_task(gui_elements, task_path_full, task_name, item_id))

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()



        #Обработчик ПКМ
        def handle_right_click(event, gui_elements, ARM_CORE_GLOBALS):
            item_id = gui_elements["tree"].identify_row(event.y)
            gui_elements["tree"].selection_set(item_id)
            if item_id:
                selected_values = gui_elements["tree"].item(item_id, 'values')
                current_cols = gui_elements["tree"]["columns"]
                item_data = next((data for data in gui_elements["treeview_data"] if [str(data.get(k, "")) for k in current_cols] == list(selected_values)), None)
            else:
                item_data = None
            show_context_menu(event, gui_elements, ARM_CORE_GLOBALS, item_data, item_id)



        #Копируем текст в буфер обмена
        def copy_to_clipboard(master, text):
            master.clipboard_clear()
            master.clipboard_append(text)



        #Диалог редактирования
        def open_edit_dialog(gui_elements, item_data, item_id):
            master = gui_elements["master"]
            name = item_data["Имя Параметра"]
            current_value = str(item_data.get("Значение Параметра", ""))
            reg_type = item_data["value_type"]
            hkey_const = item_data["hkey"]
            subkey_path = item_data["subkey"]

            if reg_type == winreg.REG_MULTI_SZ:
                current_value = "\n".join(item_data.get("Значение Параметра", []))

            new_value = simpledialog.askstring(
                random_string(),
                f"Редактирование параметра:\n{name} ({REG_TYPE_MAP.get(reg_type, 'Неизвестный')})",
                initialvalue=current_value,
                parent=master
            )

            if new_value is not None:
                if update_reg_value(hkey_const, subkey_path, name, new_value, reg_type, item_id, gui_elements):
                    load_current_tab_data(gui_elements, ARM_CORE_GLOBALS)



        #Подтверждение и удаление файла
        def confirm_and_delete_file(gui_elements, file_path, file_name, item_id):
            if delete_file(file_path, file_name, item_id, gui_elements):
                load_current_tab_data(gui_elements, ARM_CORE_GLOBALS)



        #Подтверждение и удаление параметра реестра
        def confirm_and_delete_reg_value(gui_elements, item_data, item_id):
            name = item_data["Имя Параметра"]
            path = item_data["Путь Параметра"]
            hkey_const = item_data["hkey"]
            subkey_path = item_data["subkey"]

            if messagebox.askyesno(random_string(), f"Вы уверены, что хотите удалить параметр реестра:\n'{name}' из {path}?"):
                if delete_reg_value(hkey_const, subkey_path, name, item_id, gui_elements):
                    load_current_tab_data(gui_elements, ARM_CORE_GLOBALS)



        #Диалог для создания нового параметра реестра
        def prompt_for_new_reg_value(gui_elements, hkey_const, subkey_path, reg_type_str):
            master = gui_elements["master"]
            name = simpledialog.askstring(
                random_string(),
                f"Введите имя нового параметра реестра ({reg_type_str}) для\n{ARM_CORE_GLOBALS["HKEY_MAP"].get(hkey_const)}\\{subkey_path}:",
                parent=master
            )
            if name:
                if create_reg_value(hkey_const, subkey_path, name, reg_type_str, gui_elements):
                    load_current_tab_data(gui_elements, ARM_CORE_GLOBALS)



        #Подтверждение и изменение состояния задачи планировщика (Выкл или Вкл)
        def confirm_and_set_task_state(gui_elements, task_path_full, task_name, enable, item_id):
            if get_task_startup(task_path_full, enable, item_id, gui_elements):
                load_current_tab_data(gui_elements, ARM_CORE_GLOBALS)



        #Подтверждение и удаление задачи планировщика
        def confirm_and_delete_task(gui_elements, task_path_full, task_name, item_id):
            if delete_task_scheduler_task(task_path_full, task_name, item_id, gui_elements):
                load_current_tab_data(gui_elements, ARM_CORE_GLOBALS)



        #Вспомогательная функция для получения выбранного элемента
        def get_selected_item_data(gui_elements):
            tree = gui_elements["tree"]
            item_id = tree.focus()
            if not item_id:
                return None, None

            selected_values = tree.item(item_id, 'values')
            current_cols = tree["columns"]

            item_data = next((data for data in gui_elements["treeview_data"] if [str(data.get(k, "")) for k in current_cols] == list(selected_values)), None)
            return item_id, item_data



        #Обработчик нажатия клавиш
        def handle_key_press(event, gui_elements, ARM_CORE_GLOBALS):
            item_id, item_data = get_selected_item_data(gui_elements)

            keysym = event.keysym
            current_tab = gui_elements["current_tab"]
            tree = gui_elements["tree"]

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
                    sort_treeview_column(gui_elements, column_id)
                    return "break"

            if not item_data: return

            if keysym == "e" and not is_ctrl and current_tab not in ["Пользовательская", "Планировщик"]:
                if item_data.get("value_type") not in [winreg.REG_NONE, None]:
                    open_edit_dialog(gui_elements, item_data, item_id)
                return "break"

            elif keysym == "o" and not is_ctrl and current_tab == "Планировщик":
                task_name = item_data["Имя"]
                task_path_full = item_data["TaskPath"]
                is_enabled = item_data["Enabled_raw"]
                confirm_and_set_task_state(gui_elements, task_path_full, task_name, not is_enabled, item_id)
                return "break"

            elif keysym == "Delete" and current_tab not in ["Системная", "AppInit_DLLs", "CmdLine"]:
                if current_tab == "Пользовательская":
                    confirm_and_delete_file(gui_elements, item_data["Путь Параметра"], item_data["Имя Файла"], item_id)
                elif current_tab == "Реестр":
                    confirm_and_delete_reg_value(gui_elements, item_data, item_id)
                elif current_tab == "Планировщик":
                    confirm_and_delete_task(gui_elements, item_data["TaskPath"], item_data["Имя"], item_id)
                return "break"

            elif keysym == "c" and is_ctrl:
                if is_shift:
                    if current_tab != "Планировщик":
                        name_key = "Имя Файла" if current_tab == "Пользовательская" else "Имя Параметра"
                        copy_to_clipboard(gui_elements["master"], item_data.get(name_key, ""))
                else:
                    path_key = "Путь" if current_tab == "Планировщик" else "Путь Параметра"
                    copy_to_clipboard(gui_elements["master"], item_data.get(path_key, ""))
                return "break"



        #Обработчик клавиши Menu
        def handle_menu_key(event, gui_elements, ARM_CORE_GLOBALS):
            item_id, item_data = get_selected_item_data(gui_elements)

            tree = gui_elements["tree"]
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
            show_context_menu(mock_event, gui_elements, ARM_CORE_GLOBALS, item_data, item_id)
            return "break"



        #Обработчик закрытия окна
        def on_closing():
            GUI_ELEMENTS["master"].destroy()



        ARM = tk.Tk()
        GUI_ELEMENTS["master"] = ARM
        ARM.title(random_string())
        ARM.geometry("650x350")
        style = ttk.Style(ARM)
        style.theme_use("clam")

        show_only_with_date = tk.BooleanVar(value=False)

        ARM.protocol("WM_DELETE_WINDOW", on_closing) 

        GUI_ELEMENTS["current_tab"] = "Пользовательская"
        GUI_ELEMENTS["treeview_data"] = []
        GUI_ELEMENTS["focus_after_update"] = None

        menubar = tk.Menu(ARM)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(
            label="Показывать только задачи с датой", 
            variable=show_only_with_date,
            command=lambda: load_current_tab_data(GUI_ELEMENTS, ARM_CORE_GLOBALS)
        )
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        menubar.add_cascade(label="О программе", command=about_ARM)
        ARM.config(menu=menubar)

        GUI_ELEMENTS["notebook"] = ttk.Notebook(ARM)
        GUI_ELEMENTS["notebook"].pack(pady=10, padx=10, fill="both", expand=True)
        GUI_ELEMENTS["notebook"].bind("<<NotebookTabChanged>>", lambda e: on_tab_change(e, GUI_ELEMENTS, ARM_CORE_GLOBALS))

        tab_names = ["Пользовательская", "Реестр", "Системная", "AppInit_DLLs", "CmdLine", "Планировщик"]
        for tab_name in tab_names:
            frame = ttk.Frame(GUI_ELEMENTS["notebook"], padding="5 5 5 5")
            GUI_ELEMENTS["notebook"].add(frame, text=tab_name)
            GUI_ELEMENTS["tabs"][tab_name] = frame

        initial_frame = GUI_ELEMENTS["tabs"]["Пользовательская"]
        GUI_ELEMENTS["tree"] = ttk.Treeview(initial_frame, selectmode="browse")
        GUI_ELEMENTS["vsb"] = ttk.Scrollbar(initial_frame, orient="vertical", command=GUI_ELEMENTS["tree"].yview)
        GUI_ELEMENTS["tree"].configure(yscrollcommand=GUI_ELEMENTS["vsb"].set)
        GUI_ELEMENTS["tree"].pack(side="left", fill="both", expand=True)
        GUI_ELEMENTS["vsb"].pack(side="right", fill="y")

        GUI_ELEMENTS["tree"].bind("<Button-3>", lambda e: handle_right_click(e, GUI_ELEMENTS, ARM_CORE_GLOBALS))

        set_treeview_columns(GUI_ELEMENTS)
        load_current_tab_data(GUI_ELEMENTS, ARM_CORE_GLOBALS)

        ARM.mainloop()

    except Exception as e:
        comment = f"В Компоненте ARM произошла неизвестная ошибка!\n{e}"
        logger.error(comment)
        messagebox.showerror(random_string(), comment)
