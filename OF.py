#Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
#Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
#ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
#В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
#ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
#Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
#Или в файле COPYING.txt в архиве с установщиком
#Copyleft 🄯 NEO Organization, Departament K 2024 - 2025
#Coded by @AnonimNEO (Telegram)

#Интерфейс
from tkinter import messagebox, filedialog, simpledialog
#Логирование Ошибок
from loguru import logger
#Работа с процессами
import subprocess
#Работа с реестром
import winreg
#Работа с файлами и ОС
#Условный импорт или использование заглушки
import os

from RS import random_string
from config import *

global load_bush
other_komponents_version = "0.5.2 Beta"

#Глобальные имена загруженных кустов
loaded_hive_names = {
    "SYSTEM": "Offline_SYSTEM",
    "SOFTWARE": "Offline_SOFTWARE",
    "USER": "Offline_USER"
}



#Глобальные имена для загрузки кустов
HIVE_MAP = {
    "SYSTEM": "Offline_SYSTEM",
    "SOFTWARE": "Offline_SOFTWARE",
    "USER": "Offline_USER"
}



#Список для отслеживания загруженных кустов
active_loaded_hives = []



#Заглушка, библиотеки psutil которая всегда возвращает False/None.
class Psutil:
    def cpu_percent(self, *args, **kwargs):
        return 0.0

    def virtual_memory(self, *args, **kwargs):
        class MemStub:
            percent = 0.0
            total = 1024 * 1024 #Имитируем 1МБ ОЗУ, чтобы не падал LP.py

        return MemStub()

    def disk_usage(self, *args, **kwargs):
        class DiskStub:
            percent = 0.0

        return DiskStub()

    #Добавлен метод для возврата пустого списка дисков
    def disk_partitions(self, *args, **kwargs):
        return []

    #Заглушка для всех остальных методов, чтобы не вызывать ошибку AttributeError
    def __getattr__(self, name):
        if name in ["sensors_temperatures", "net_io_counters", "process_iter"]:
            return lambda *args, **kwargs: None
        return lambda *args, **kwargs: False



#Получаем оффлайн-пути реестра
@logger.catch()
def get_offline_reg_path(hkey_const, subkey_path, ARM_CORE_GLOBALS, run_in_recovery):
    if run_in_recovery:
        psutil = Psutil()
    elif not run_in_recovery:
        import psutil

    if not run_in_recovery:
        #В онлайн-режиме возвращаем исходные константы
        return hkey_const, subkey_path

    offline_map = ARM_CORE_GLOBALS["OFFLINE_HKEY_MAP"]

    if hkey_const == winreg.HKEY_CURRENT_USER:
        #HKCU всегда перенаправляется на загруженный NTUSER.DAT
        new_hkey, temp_name, _ = offline_map[hkey_const]
        #Путь: HKEY_LOCAL_MACHINE\Offline_USER\{subkey_path}
        new_subkey_path = f"{temp_name}\\{subkey_path}"
        return new_hkey, new_subkey_path

    elif hkey_const == winreg.HKEY_LOCAL_MACHINE:
        #HKLM: Проверяем, начинается ли subkey_path с "Software"
        if subkey_path.lower().startswith(r"software"):
            new_hkey, temp_name, _ = offline_map[hkey_const]
            #Удаляем "Software" из начала subkey_path и добавляем имя загруженного куста
            path_after_software = subkey_path[len("Software"):].strip("\\")
            #Путь: HKEY_LOCAL_MACHINE\Offline_SOFTWARE\{путь_после_Software}
            new_subkey_path = f"{temp_name}\\{path_after_software}"
            return new_hkey, new_subkey_path

    return hkey_const, subkey_path



#Получаем диск с установленной шиндовс
@logger.catch
def get_current_disc(run_in_recovery=False):
    try:
        if run_in_recovery:
            #В WinPE ищем диск с папкой Windows, отличный от X:
            drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWYZ"]
            for drive in drives:
                if os.path.exists(os.path.join(drive, "Windows")):
                    logger.info(f"OF - Система найдена на {drive}")
                    return drive, True
            return "X:\\", False

        #Для обычной среды
        partitions = psutil.disk_partitions()
        for p in partitions:
            if "fixed" in p.opts and os.path.exists(os.path.join(p.mountpoint, "Windows")):
                return p.mountpoint, True
        return "C:\\", False
    except Exception as e:
        logger.critical(f"OF\get_current_disc - Неизвестаня ошибка:\n{e}")
        return "X:\\", False


#Загрузка кустов реестра
@logger.catch()
def load_bush(current_disc):
    global active_loaded_hives
    
    #Формируем пути к файлам
    if not os.path.isfile(f"{current_disc}\\Users\\{default_user_name}\\"):
        user_name = simpledialog.askstring(title=random_string(), prompt=f"Не найден пользователь {default_user_name}\nВведите нужное имя пользователя: ")
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
            logger.error(f"OF/load_bush - Файл куста не найден: {path}")
            continue

        #Если куст уже в списке активных, пропустим
        if name in active_loaded_hives:
            continue

        try:
            #Загрузка куста реестра
            winreg.LoadKey(winreg.HKEY_LOCAL_MACHINE, name, path)
            
            active_loaded_hives.append(name)
            logger.info(f"OF/load_bush - Куст {name} успешно загружен из {path}")
            success_count += 1
        except Exception as e:
            logger.error(f"OF/load_bush - Ошибка при загрузке куста {name} из {path}:\n{e}")

    #Возвращаем True, если загрузили хотя бы один куст
    return success_count > 0



#Выгружаем кусты реестра
@logger.catch()
def unload_bush():
    global active_loaded_hives

    for name in reversed(active_loaded_hives[:]):
        try:
            winreg.unloadkey(winreg.HKEY_LOCAL_MACHINE, name)
            active_loaded_hives.remove(name)
            logger.success(f"OF/unload_bush - Куст {name} успешно выгружен.")
        except Exception as e:
            logger.error(f"OF/unload_bush - Ошибка при выгрузке куста {name}:\n{e}")



#Получаем Имя текущего пользователя
@logger.catch
def get_user_name():
    try:
        user_name = os.getlogin()
        return user_name
    except Exception as e:
        logger.error(f"OF/get_user_name - Ошибка получения имени пользователя!\n{e}")
        return default_user_name



#Открыть С помощью
@logger.catch
def open_with():
    target_file_path = filedialog.askopenfilename(title="Выберите файл для открытия", filetypes=[("Все файлы", "*.*")])
    if target_file_path and os.path.isfile(target_file_path): #Проверка, что файл выбран и существует
        app_path = filedialog.askopenfilename(title="Выберите программу для открытия файла", filetypes=[("Все файлы", "*.*")])
        if app_path:
            try:
                subprocess.Popen([app_path, target_file_path])
            except Exception as e:
                logger.error(f"OF/open_with - Не удалось открыть файл '{target_file_path}'с помощью указанной программы '{app_path}'\n{e}")
                messagebox.showerror(random_string(), f"Не удалось открыть файл с помощью указанной программы:\n{e}")



@logger.catch
def reg_file(reg_file, reg_code):
    with open(reg_file, "w") as reg:
        reg.write(reg_code)
    try:
        os.startfile(reg_file)
    except Exception as e:
        logger.error(f"OF/reg_file - Ошибка при запуске {reg_file}\n{e}")



def run_command(command):
    try:
        #Запускает команду и ждём её завершения
        process = subprocess.run(command, shell=True)
        return process.returncode
    except Exception as e:
        logger.error(f"OF/run_command - Ошибка при выполнении команды - {command}")
