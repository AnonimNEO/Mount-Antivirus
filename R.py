# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

# Логирование Ошибок
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
# Работа с ОС
import win32com.client
import subprocess
# Работа с файлами
import os

from languages import l
from config import RESTART_WINDOWS, RESTART_WINDOWS_BAT

#global restart_windows_bat
RESTART_VERSION = "0.9.6 Beta"

# @logger.catch
def R():
    #global error
    error = 0
    #global restart_windows
    try:
        if RESTART_WINDOWS == "win32com":
            logger.info(f'R - {l("attempt_to_reboot")} WMI (win32com)')

            # Получаем объект WMI для управления операционной системой
            wmi = win32com.client.GetObject("winmgmts:{impersonationLevel=impersonate, (Shutdown)}\\\\.\\root\\cimv2")

            # Находим запущенный экземпляр операционной системы
            os_instance = wmi.ExecQuery("Select * from Win32_OperatingSystem")[0]

            # Вызываем метод Reboot (0 - успешный код, 2 - перезагрузка)
            # В отличие от InitiateSystemShutdown, этот метод не принимает таймаут напрямую,
            # но это более надёжный способ для win32com/WMI.
            os_instance.Reboot()
        elif RESTART_WINDOWS == "os":
            logger.info(f'R - {l("attempt_to_reboot")} os.system("shutdown /r /t {time_to_restart}")')
            os.system(f"shutdown /r /t {time_to_restart}")
        elif RESTART_WINDOWS == "subprocess":
            logger.info(f'R - {l("attempt_to_reboot")} subprocess.call (shutdown /r /t {time_to_restart})')
            subprocess.call(["shutdown", "/r", "/t", f"{time_to_restart}"])
        elif RESTART_WINDOWS == "bat":
            logger.info(f'R - {l("attempt_to_reboot")} bat-{l("file")}')
            with open(RESTART_WINDOWS_BAT, "w") as bat_file:
                bat_file.write(f"shutdown /r /t {time_to_restart}")
            os.startfile(RESTART_WINDOWS_BAT)
    except:
        logger.exception(f'R - {l("r_critical_error")} "{RESTART_WINDOWS}"')
        error += 1
        if error == 1:
            logger.info(f'R - {l("next_method")}: os')
            RESTART_WINDOWS = "os"
            R()
        if error == 2:
            logger.info(f'R - {l("next_method")}: subprocess')
            RESTART_WINDOWS = "subprocess"
            R()
        if error == 3:
            logger.info(f'R - {l("next_method")}: bat')
            RESTART_WINDOWS = "bat"
            R()
        if error < 5:
            logger.error(f'R - {l("all_method_used")}')
