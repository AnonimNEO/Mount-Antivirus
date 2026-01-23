#Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
#Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
#ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
#В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
#ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
#Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
#Или в файле COPYING.txt в архиве с установщиком
#Copyleft 🄯 NEO Organization, Departament K 2024 - 2025
#Coded by @AnonimNEO (Telegram)

#Логирование Ошибок
from loguru import logger
#Работа с ОС
from ctypes import wintypes
import ctypes
import psutil

from OF import Psutil

edit_criticality_version = "0.3.2 Beta"

#Загрузка необходимых библиотек Windows
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
ntdll = ctypes.WinDLL("ntdll", use_last_error=True)

#Определение структур и констант
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_SET_INFORMATION = 0x0200
STATUS_SUCCESS = 0

#0x1D (29) - ProcessBreakOnTermination: используется для установки/запроса критичности.
#Значение (ULONG): 1 - критический, 0 - некритический
PROCESS_INFORMATION_CLASS_CRITICAL = 0x1D

#Определение функций Windows API
def define_functions():
    #kernel32.OpenProcess
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE

    #kernel32.CloseHandle
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    #ntdll.NtSetInformationProcess (Для установки критичности)
    ntdll.NtSetInformationProcess.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.ULONG]
    ntdll.NtSetInformationProcess.restype = wintypes.LONG

    #ntdll.NtQueryInformationProcess (Для запроса критичности)
    ntdll.NtQueryInformationProcess.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD, #ProcessInformationClass
        ctypes.c_void_p, #ProcessInformation
        wintypes.ULONG, #ProcessInformationLength
        ctypes.POINTER(wintypes.ULONG) #ReturnLength
    ]
    ntdll.NtQueryInformationProcess.restype = wintypes.LONG

    #ntdll.NtQuerySystemInformation
    ntdll.NtQuerySystemInformation.argtypes = [wintypes.DWORD, ctypes.c_void_p, wintypes.ULONG,
                                              ctypes.POINTER(wintypes.ULONG)]
    ntdll.NtQuerySystemInformation.restype = wintypes.LONG



#Получаем имя процесса
def get_process_name(process_id):
    process = psutil.Process(process_id)
    return process.name()



#Попытка получить текущий статус критичности процесса
def get_process_critical_status(process_id, run_in_recovery):
    if not run_in_recovery:
        import psutil
    elif run_in_recovery:
        psutil = Psutil()

    process_handle = None
    try:
        #Открываем процесс с правом на запрос информации
        process_handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, process_id)

        if not process_handle:
            return None

        #Переменная для хранения результата (ULONG, 4 байта)
        critical_value = wintypes.ULONG(0)
        return_length = wintypes.ULONG(0)

        #Вызываем NtQueryInformationProcess с классом 0x1D
        result = ntdll.NtQueryInformationProcess(
            process_handle,
            PROCESS_INFORMATION_CLASS_CRITICAL,
            ctypes.byref(critical_value),
            ctypes.sizeof(critical_value),
            ctypes.byref(return_length)
        )

        if result == STATUS_SUCCESS:
            return bool(critical_value.value)
        else:
            return None

    except Exception:
        return None
    finally:
        if process_handle:
            kernel32.CloseHandle(process_handle)



#Меняем значение критичности на процессе
def set_process_critical(process_id, critical):
    process_handle = None
    try:
        #Получаем handle процесса с правами на изменение и запрос информации
        process_handle = kernel32.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION, False, process_id)

        if not process_handle:
            process_name = get_process_name(process_id)
            logger.error(f"EC - Не удалось открыть процесс {process_name} (pid: {process_id}). Код ошибки: {ctypes.get_last_error()}")
            return False

        #Значение 1 для True (критический), 0 для False (некритический)
        critical_value = ctypes.c_ulong(1 if critical else 0)

        #Вызываем NtSetInformationProcess с классом 0x1D
        result = ntdll.NtSetInformationProcess(
            process_handle,
            PROCESS_INFORMATION_CLASS_CRITICAL,
            ctypes.byref(critical_value),
            ctypes.sizeof(critical_value)
        )

        kernel32.CloseHandle(process_handle)

        if result == STATUS_SUCCESS:
            status = "установлена" if critical else "снята"
            logger.success(f"EC - Критичность процесса {process_id} {status} (целевое: {critical})")
            return True
        else:
            logger.error(f"EC - Ошибка при изменения критичности. Код ошибки: {hex(result)}")
            return False

    except Exception as e:
        logger.error(f"EC - Неизвестная ошибка при изменении критичности:\n{e}")
        return False
    finally:
        if process_handle:
            kernel32.CloseHandle(process_handle)



def EC(process_id, critical, debug_mode=False):
    #Инициализация функций windows API
    define_functions()

    try:
        process_name = get_process_name(process_id)
        #Проверяем существование процесса
        if not psutil.pid_exists(process_id):
            if debug_mode:
                logger.error(f"EC - Процесс {process_name} (pid: {process_id}) не найден!")

        if set_process_critical(process_id, critical):
            logger.success(f"EC - Значение критичности процесса {process_name} (pid: {process_id}) изменено на critical")
        else:
            logger.error(f"EC - Значение критичности процесса {process_name} (pid: {process_id}) не было изменено")

    except Exception as e:
        logger.critical(f"В Компоненте EditCriticality произошла неизвестная ошибка:\n{e}")
