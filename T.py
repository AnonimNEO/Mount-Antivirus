#Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
#Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
#ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
#В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
#ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
#Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
#Или в файле COPYING.txt в архиве с установщиком
#Copyleft 🄯 NEO Organization, Departament K 2024 - 2025
#Coded by @AnonimNEO (Telegram)

#Рисование иконки в трее и вставка картинок
from PIL import Image, ImageDraw, ImageFont
#Логирование Ошибок
from loguru import logger
#Получение прав Администратора
from elevate import elevate
#Движок иконки в трее
from pystray import MenuItem, Menu
import pystray
#Работа с потоками
#from threading import Thread
import threading
#Работа со временим
import time
#Работа с файлами и ОС
import os

#import ctypes
#ctypes import windll
#Устанавливаем DPI Awareness ПЕРЕД созданием любых графических объектов
#windll.shcore.SetProcessDpiAwareness(1)

#Глобализируем версии компонентов
global autorun_master_version, clear_cache_version, exit_version, file_manager_version, load_protection_version, unlocker_version, on_board_pc_version, other_komponents_version, restart_version, random_string_version, run_version, scarecrow_protection_verison

#Импорт Компонентов
from AP import AP
from ARM import ARM, autorun_master_version
from CC import CC, clear_cache_version
from config import *
from E import ask_exit, exit_version
from EC import edit_criticality_version
from FM import FM, file_manager_version
from LP import LP, load_protection_version
from MU import MU, unlocker_version
from OBPC import OBPC, on_board_pc_version
from OF import open_with, get_current_disc, load_bush, unload_bush, other_komponents_version
from PM import PM, process_manager_version
from R import R, restart_version
from RS import random_string_version
from Run import Run, run_version
from SAU import SAU, settings_and_update_version
from SP import SP, scarecrow_protection_version
from UA import UA, unlock_all_version

elevate()

#Глобальные Переменные
global T_log_txt, start_interface
font_trey = "arial.ttf"
trey_version = "2.0.2 Beta"

if not os.path.exists(log_path):
    os.makedirs(log_path)
logger.add(f"{log_path}\\{T_log_txt}", format="{time} {level} {message}", rotation="100 KB", compression="zip")

def check_is_recovery():
    #Проверка через реестр (характерно для среды установки/восстановления)
    try:
        import winreg
        # В WinPE этот ключ часто указывает на среду предустановки
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\Setup", 0, winreg.KEY_READ)
        setup_type, _ = winreg.QueryValueEx(reg_key, "SystemSetupInProgress")
        winreg.CloseKey(reg_key)
        if setup_type == 1:
            return True
    except Exception:
        pass

    #Проверка по наличию критических файлов
    #if os.path.exists("X:\\Windows\\"):
    #    return True

    return False

run_in_recovery = False
try:
    #Инициализация переменной
    try:
        run_in_recovery = check_is_recovery()
        if run_in_recovery:
            logger.warning("T - Запуск в среде восстановления Шindows")
        else:
            logger.info("T - Запуск в стандартной среде Шindows")
    except Exception as e:
        run_in_recovery = True
        logger.error(f"T - Ошибка при определении среды:\n{e}")

    if run_in_recovery:
        current_disc, found_disc = get_current_disc(run_in_recovery)
        if found_disc:
            logger.info(f"T - Загрузка кустов реестра с диска {current_disc}...")
            load_bush(current_disc)

except Exception as e:
    logger.error(f"T - Критическая ошибка: {e}")

#def set_dpi_awareness():
#    if run_in_recovery:
#        return
#    try:
#        #Пытаемся вызвать более современную функцию (Windows 8.1+)
#        ctypes.windll.shcore.SetProcessDpiAwareness(1)
#    except Exception:
#        try:
#            #Откат для старых систем (Windows Vista/7)
#            ctypes.windll.user32.SetProcessDPIAware()
#        except Exception as e:
#            logger.debug(f"T - Не удалось установить DPI Awareness: {e}")
#
#set_dpi_awareness()

#Основная программа
try:
    #if not run_in_recovery:
    #    #ИСПРАВЛЕНИЕ: Активируем DPI-Awareness для Windows
    #    try:
    #        ctypes.windll.shcore.SetProcessDpiAwareness(1) # Убирает ошибку модуля в pystray
    #    except Exception as e:
    #        logger.warning(f"T - Не удалось установить DPI Awareness: {e}")

    if not run_in_recovery:
        try:
            #Создание Иконки
            def create_image(width, height):
                image = Image.new("RGB", (width, height), (255, 0, 0))
                square = ImageDraw.Draw(image)
                square.rectangle(
                    (width // 2 - 10, height // 2 - 10, width // 2 + 10, height // 2 + 10),
                    fill=(0, 0, 255)
                )

                font = None
                #Список путей к шрифту Arial для разных сред
                font_paths = [font_trey, "C:\\Windows\\Fonts\\arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]

                for path in font_paths:
                    try:
                        font = ImageFont.truetype(path, 24)
                        break
                    except Exception:
                        continue

                if font is None:
                    font = ImageFont.load_default()
                    logger.warning("T - Используется шрифт по умолчанию")

                text = "=]"
                text_bbox = square.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_position = (width // 2 - text_width // 2, height // 2 - text_height // 2)
                square.text(text_position, text, fill=(255, 0, 0), font=font)
                return image

            def start_icon():
                if run_in_recovery:
                    logger.warning("T - Режим восстановления: Трей отключен.")
                    return 
                try:
                    icon.visible = True
                except Exception as e:
                    logger.error(f"T - Ошибка трея:\n{e}")

            #Создаем выпадающий список с функциями Анлокера
            unlocker_menu = Menu(
                MenuItem("Файловый Менеджер", lambda:FM(run_in_recovery)),
                MenuItem("Мастер Автозагрузки", lambda:ARM(run_in_recovery)),
                MenuItem("Scarecrow Protection", lambda:SP(run_in_recovery)),
                MenuItem("Запустить Очистку Temp", lambda:CC(run_in_recovery)),
                MenuItem("Открыть с Помощью", open_with),
                MenuItem("Перезапустить ПК", R)
            )

            #Меню По ПКМ
            image = create_image(20, 20)
            menu = Menu(
                MenuItem("Открыть Монтировка Анлокер", lambda:MU(run_in_recovery)),
                MenuItem("Утилиты", unlocker_menu),
                MenuItem("Запустить Load Protection", lambda:LP(run_in_recovery)),
                MenuItem("Менеджер Процессов", lambda:PM(run_in_recovery)),
                MenuItem("Разблокировка Всего", lambda:UA(run_in_recovery)),
                MenuItem("Запустить От Имени Админа", Run),
                MenuItem("О Программе", lambda:AP(autorun_master_version, clear_cache_version, exit_version, edit_criticality_version, file_manager_version, load_protection_version, unlocker_version, on_board_pc_version, other_komponents_version, process_manager_version, restart_version, random_string_version, run_version, scarecrow_protection_version, settings_and_update_version, trey_version, unlock_all_version)),
                MenuItem("Настройки", SAU),
                MenuItem("Выход", ask_exit)
            )

            icon = pystray.Icon("Mount_Antivirus_Icon", image, "Mount Antivirus", menu)

            if start_interface == "icon" or start_interface == "window":
                #Запускаем иконку в трее в отдельном потоке.
                thread_icon = threading.Thread(target=icon.run)
                thread_icon.daemon = True #Делаем поток демоном, чтобы он завершился при выходе основной программы
                thread_icon.start()

                start_icon()

            if start_obpc:
                #Запускаем Голосовое Управление (OBPC) в отдельном потоке.
                thread_obpc = threading.Thread(target=lambda:OBPC(run_in_recovery))
                thread_obpc.daemon = True
                thread_obpc.start()

            if start_lp:
                #Запускаем LoadProtection (LP) в отдельном потоке.
                thread_lp = threading.Thread(target=lambda:LP(run_in_recovery))
                thread_lp.daemon = True
                thread_lp.start()

            if start_interface == "window" or start_interface == "only-windows":
                MU(run_in_recovery)

            while True:
                time.sleep(1)
        except Exception as e:
            run_in_recovery = True
            logger.warning("T - Ошибка при запуске иконки, запуск в режиме рекавери...")

    if run_in_recovery:
        logger.info("T - Запуск в режиме рекавери...")
        MU(run_in_recovery)

except Exception as e:
    run_in_recovery = True
    logger.critical(f"В Компоненте Trey произошла неизвестная ошибка!\n{e}")
    logger.info("T - Запуск в режиме рекавери...")
    MU(run_in_recovery)
finally:
    if run_in_recovery:
        logger.info("T - Завершение работы, выгрузка кустов реестра...")
        unload_bush()
