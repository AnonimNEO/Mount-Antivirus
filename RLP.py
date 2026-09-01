# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)



# ДАННЫЙ КОМПОНЕНТ НЕ ДОДЕЛАН, НЕ ГАРАНТИРОВАН ДАЖЕ ЗАПУСК



from tkinter import messagebox
from RS import RS
from loguru import logger
import psutil

# from EC import get_process_critical_status
def get_process_critical_status(a=None,b=None,c=None):
    pass

REAL_TIME_PROTECT_VERSION = "0.1.4 Pre-Alpha"

# Действие с процессами
def action_process(action, process_ids):
    if not isinstance(process_ids, (list, tuple)):
        process_ids = [process_ids]

    for pid in process_ids:
        try:
            proc = psutil.Process(int(pid))

            if action == "kill":
                proc.terminate()
            elif action == "suspend":
                proc.suspend()
            elif action == "resume":
                proc.resume()
            elif action == "edit_critical_to_false":
                EC(int(pid), False)
            elif action == "edit_critical_to_true":
                EC(int(pid), True)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as e:
            logger.critical(f"RLP - Ошибка при {action} для PID {pid}:\n{e}")

# Получаем имя процесса
def get_process_name(process_id):
    process = psutil.Process(process_id)
    return process.name()

# Получаем информацию о процессе
def get_process_info(proc, RUN_IN_RECOVERY):
    try:
        status = "Заморожен" if proc.status() == psutil.STATUS_STOPPED else "Запущен"

        # РЕАЛИЗОВАТЬ ПРОВЕРКУ НА АДМИНИСТРАТОРА
        is_elevated = False

        return {
            "PID": proc.pid,
            "Имя Процесса": proc.name(),
            "Путь к файлу": proc.exe() if proc.exe() else "Н/Д",
            "Пользователь": proc.username() if proc.username() else "Н/Д",
            "Критичность": get_process_critical_status(proc.pid, RUN_IN_RECOVERY),
            "Статус": status,
            "Администратор": is_elevated,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None
    except Exception as e:
        process_name = get_process_name(proc.pid)
        logger.error(f"PM - Ошибка при получении информации о процессе {process_name} (pid:{proc.pid}):\n{e}")
        return None

# Получаем список процессов
def get_process_list(list_type, RUN_IN_RECOVERY):
    all_processes = []
    for proc in psutil.process_iter(["pid", "name", "exe", "username", "status"]):
        info = get_process_info(proc, RUN_IN_RECOVERY)
        if info:
            all_processes.append(info)

    if list_type == "all_list":
        return all_processes
    elif list_type == "critical_list":
        return [p for p in all_processes if p["Критичность"]]
    elif list_type == "suspend_list":
        return [p for p in all_processes if p["Статус"] == "Заморожен"]
    return []

def RLP(RUN_IN_RECOVERY=False):
    SUSPEND_PROCESS = []
    system_name_process = (
        ("cmd.exe", r"C:\Windows\System32\cmd.exe"),
        ("notepad.exe", r"C:\Windows\notepad.exe"),
        ("calc.exe", r"C:\Windows\System32\calc.exe"),
        ("explorer.exe", r"C:\Windows\explorer.exe"),
        ("powershell.exe", r"C:\Windows\System32\powershell.exe"),
        ("taskmgr.exe", r"C:\Windows\System32\taskmgr.exe"),
        ("regedit.exe", r"C:\Windows\regedit.exe"),
        ("mspaint.exe", r"C:\Windows\System32\mspaint.exe"),
    )
    system_exception = [r"C:\Users\Adminus\Desktop\calc.exe"]

    if RUN_IN_RECOVERY:
        messagebox.showwarning(RS(), "RealTimeProtect невозможно запустить в среде восстановления")

    def warning_dialog(cause, p):
        if cause == "fake_system":
            cause_text = f'Процесс {p["Имя Процесса"]}({p["PID"]}), притворяется системным.\nТак как его файл расположен в: {p["Путь к файлу"]}'

    def stop_process(cause, p):
        action_process("suspend", p["PID"])
        SUSPEND_PROCESS.append(p["PID"])
        warning_dialog(cause, p)

    def check_system_process(PROCESS_LIST):
        logger.info("RLP - Проверка системных процессов...")
        for p in PROCESS_LIST:
            p_name = p["Имя"]
            p_exe = p["Путь к файлу"]

            for sys_name, sys_exe in system_name_process:
                if p_name == sys_name:
                    if p_exe != sys_exe:
                        stop_process(p)

    def filter_process_for_exception(PROCESS_LIST):
        for p in PROCESS_LIST:
            for except_sys_name in system_exception:
                if p["Путь к файлу"] == except_sys_name:
                    PROCESS_LIST.remove(p)

        return PROCESS_LIST

    while True:
        PROCESS_LIST = get_process_list("all_list", RUN_IN_RECOVERY)

        PROCESS_LIST = filter_process_for_exception(PROCESS_LIST)

        check_system_process(PROCESS_LIST)

if __name__ == "__main__":
    RLP(RUN_IN_RECOVERY=False)
