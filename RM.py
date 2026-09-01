# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

import ctypes
from ctypes import wintypes, c_ulong
import threading
import time
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
import queue
import winreg

REGISTRY_MONITOR_VERSION = "0.2.11 Pre-Alpha"

# Загрузка библиотеки
ADVAPI32 = ctypes.WinDLL("advapi32", use_last_error=True)

# Константы
HCU = winreg.HKEY_CURRENT_USER
HLM = winreg.HKEY_LOCAL_MACHINE
HCR = winreg.HKEY_CLASSES_ROOT
HU = winreg.HKEY_USERS
HCC = winreg.HKEY_CURRENT_CONFIG

NOTIFY_FLAGS = (
    winreg.REG_NOTIFY_CHANGE_NAME |
    winreg.REG_NOTIFY_CHANGE_ATTRIBUTES |
    winreg.REG_NOTIFY_CHANGE_LAST_SET |
    winreg.REG_NOTIFY_CHANGE_SECURITY
)

# Права доступа
KEY_QUERY_VALUE = winreg.KEY_QUERY_VALUE
KEY_NOTIFY = winreg.KEY_NOTIFY
KEY_READ = KEY_QUERY_VALUE | KEY_NOTIFY
KEY_ENUMERATE_SUB_KEYS = winreg.KEY_ENUMERATE_SUB_KEYS

# Константы для WaitForSingleObject
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258
INFINITE = 0xFFFFFFFF

REGSAM = c_ulong

# Определение функций Windows API
def define_functions():
    # RegOpenKeyExW
    ADVAPI32.RegOpenKeyExW.argtypes = [
        wintypes.HANDLE,
        wintypes.LPCWSTR,
        wintypes.DWORD,
        REGSAM,
        ctypes.POINTER(wintypes.HANDLE)
    ]
    ADVAPI32.RegOpenKeyExW.restype = wintypes.LONG

    # RegCloseKey
    ADVAPI32.RegCloseKey.argtypes = [wintypes.HKEY]
    ADVAPI32.RegCloseKey.restype = wintypes.LONG

    # RegNotifyChangeKeyValue
    ADVAPI32.RegNotifyChangeKeyValue.argtypes = [
        wintypes.HKEY,
        wintypes.BOOL,
        wintypes.DWORD,
        wintypes.HANDLE,
        wintypes.BOOL
    ]
    ADVAPI32.RegNotifyChangeKeyValue.restype = wintypes.LONG

    # RegQueryValueExW
    ADVAPI32.RegQueryValueExW.argtypes = [
        wintypes.HKEY,
        wintypes.LPCWSTR,
        wintypes.LPDWORD,
        wintypes.LPDWORD,
        wintypes.LPBYTE,
        wintypes.LPDWORD
    ]
    ADVAPI32.RegQueryValueExW.restype = wintypes.LONG

    # RegEnumKeyExW
    ADVAPI32.RegEnumKeyExW.argtypes = [
        wintypes.HKEY,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD),
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.FILETIME)
    ]
    ADVAPI32.RegEnumKeyExW.restype = wintypes.LONG

    # RegQueryInfoKeyW
    ADVAPI32.RegQueryInfoKeyW.argtypes = [
        wintypes.HKEY,
        wintypes.LPWSTR, wintypes.LPDWORD, # lpClass, lpcchClass
        ctypes.POINTER(wintypes.DWORD), # nSubKeys
        ctypes.POINTER(wintypes.DWORD), # nMaxSubKeyLen
        ctypes.POINTER(wintypes.DWORD), # nMaxClassLen
        ctypes.POINTER(wintypes.DWORD), # nValues
        ctypes.POINTER(wintypes.DWORD), # nMaxValueNameLen
        ctypes.POINTER(wintypes.DWORD), # nMaxValueLen
        ctypes.POINTER(wintypes.DWORD), # nSecurityDescriptor
        ctypes.POINTER(wintypes.FILETIME) # lpftLastWriteTime
    ]
    ADVAPI32.RegQueryInfoKeyW.restype = wintypes.LONG

    # CreateEventW
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateEventW.argtypes = [
        ctypes.c_void_p,
        wintypes.BOOL,
        wintypes.BOOL,
        wintypes.LPCWSTR
    ]
    kernel32.CreateEventW.restype = wintypes.HANDLE

    # WaitForSingleObject
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD

    # ResetEvent
    kernel32.ResetEvent.argtypes = [wintypes.HANDLE]
    kernel32.ResetEvent.restype = wintypes.BOOL

    # CloseHandle
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    return kernel32, ADVAPI32



# Мониторинг ключа реестра
class RegistryMonitor(threading.Thread):
    def __init__(self, hive, key_path, watch_subtree=True, event_queue=None, DEBUG_MODE=False):
        # hive: Куст реестра
        # key_path: Путь к ключу реестра
        # watch_subtree: Отслеживать ли подключи
        # event_queue: Очередь для передачи обнаруженных событий
        super().__init__()
        self.hive = hive
        self.key_path = key_path
        self.watch_subtree = watch_subtree
        self.stop_event = threading.Event()
        self.daemon = True
        self.event_queue = event_queue #  Сохраняем очередь

        self.kernel32, self.ADVAPI32 = define_functions()

        logger.info(f"RegistryMonitor инициализирован: {key_path}")

    def format_registry_data(self, data, reg_type):
        try:
            if reg_type == winreg.REG_SZ or reg_type == winreg.REG_EXPAND_SZ:
                # Пытаемся декодировать как utf-16-le, удаляя нулевые символы в конце
                return data.decode("utf-16-le").rstrip("\x00")
            elif reg_type == winreg.REG_DWORD:
                # Преобразуем в шестнадцатеричное представление
                return hex(int.from_bytes(data, byteorder="little"))
            elif reg_type == winreg.REG_BINARY:
                # Возвращаем в виде шестнадцатеричной строки
                return data.hex()
            elif reg_type == winreg.REG_MULTI_SZ:
                # Декодируем каждую строку, разделенную двойным нулевым символом
                return [s.decode("utf-16-le").rstrip("\x00") for s in data.split(b"\x00\x00") if s]
            elif reg_type == winreg.REG_QWORD:
                # Преобразуем в шестнадцатеричное представление (знаковое)
                return hex(int.from_bytes(data, byteorder="little", signed=True))
            else:
                # Для неизвестных типов возвращаем hex представление
                return f"Неизвестный тип ({reg_type}): {data.hex()}"
        except UnicodeDecodeError:
            # Если декодирование не удалось, возвращаем hex представление
            logger.warning(f"RM - Не удалось декодировать данные типа {reg_type} как utf-16-le. Возвращаем hex.")
            return data.hex()
        except Exception as e:
            # Обработка других возможных ошибок
            logger.warning(f"RM - Ошибка форматирования данных реестра (тип {reg_type}): {e}")
            return data.hex() # Возвращаем hex в случае ошибки

    def get_full_registry_snapshot(self, h_key, current_path=""):
        snapshot = {}
        try:
            # Получаем информацию о ключе
            class_name_buffer = ctypes.create_unicode_buffer(256)
            class_name_size = wintypes.DWORD(256)
            subkeys_count = wintypes.DWORD(0)
            max_subkey_len = wintypes.DWORD(0)
            max_class_len = wintypes.DWORD(0)
            values_count = wintypes.DWORD(0)
            max_value_name_len = wintypes.DWORD(0)
            max_value_len = wintypes.DWORD(0)
            security_descriptor = wintypes.DWORD(0)
            last_write_time = wintypes.FILETIME()

            # Исправлен вызов RegQueryInfoKeyW
            result_info = self.ADVAPI32.RegQueryInfoKeyW(
                h_key,
                class_name_buffer,
                ctypes.byref(class_name_size),
                None, # lpClass
                ctypes.byref(subkeys_count),
                ctypes.byref(max_subkey_len),
                ctypes.byref(max_class_len),
                ctypes.byref(values_count),
                ctypes.byref(max_value_name_len),
                ctypes.byref(max_value_len),
                ctypes.byref(security_descriptor),
                ctypes.byref(last_write_time)
            )

            if result_info != 0:
                logger.warning(f"RM - Не удалось получить информацию о ключе {current_path}: код {result_info}")
                return snapshot

            # Получаем значения ключа
            for i in range(values_count.value):
                value_name_buffer = ctypes.create_unicode_buffer(max_value_name_len.value + 1)
                value_name_size = wintypes.DWORD(ctypes.sizeof(value_name_buffer))
                value_type = wintypes.DWORD()
                value_data_buffer = ctypes.create_string_buffer(max_value_len.value)
                value_data_size = wintypes.DWORD(ctypes.sizeof(value_data_buffer))

                result = self.ADVAPI32.RegQueryValueExW(
                    h_key,
                    value_name_buffer,
                    None, # lpReserved
                    ctypes.byref(value_type),
                    value_data_buffer,
                    ctypes.byref(value_data_size)
                )

                if result == 0:
                    value_name = value_name_buffer.value
                    value_data = value_data_buffer.raw[:value_data_size.value]
                    formatted_data = self.format_registry_data(value_data, value_type.value)
                    snapshot[value_name] = {"type": value_type.value, "data": formatted_data}
        except Exception as e:
            logger.warning(f"RM - Ошибка при получении значений ключа {current_path}: {e}")

        # Получаем под-ключи
        for i in range(subkeys_count.value):
            subkey_name_buffer = ctypes.create_unicode_buffer(max_subkey_len.value + 1)
            subkey_name_size = wintypes.DWORD(ctypes.sizeof(subkey_name_buffer))
            subkey_class_buffer = ctypes.create_unicode_buffer(max_class_len.value + 1)
            subkey_class_size = wintypes.DWORD(ctypes.sizeof(subkey_class_buffer))

            result = self.ADVAPI32.RegEnumKeyExW(
                h_key,
                i,
                subkey_name_buffer,
                ctypes.byref(subkey_name_size),
                ctypes.byref(subkey_class_size), #  lpClass
                subkey_class_buffer,
                None, # lpReserved
                None # lpftLastWriteTime
            )

            if result == 0:
                subkey_name = subkey_name_buffer.value
                full_subkey_path = f"{current_path}\\{subkey_name}" if current_path else subkey_name

                h_subkey = wintypes.HKEY()
                subkey_result = self.ADVAPI32.RegOpenKeyExW(
                    h_key,
                    subkey_name,
                    0,
                    KEY_READ | KEY_ENUMERATE_SUB_KEYS,
                    ctypes.byref(h_subkey)
                )
                if subkey_result == 0:
                    snapshot[subkey_name] = self.get_full_registry_snapshot(h_subkey, full_subkey_path)
                    self.ADVAPI32.RegCloseKey(h_subkey)
                else:
                    logger.warning(f"RM - Не удалось открыть под-ключ {full_subkey_path}: код {subkey_result}")

        return snapshot

    # Сравнивает два снимка реестра и возвращает список изменений.
    def compare_snapshots(self, old_snapshot, new_snapshot, current_path=""):
        changes = []

        # Проверяем добавленные/измененные ключи и значения
        for key, new_data in new_snapshot.items():
            if key not in old_snapshot:
                # Новый ключ
                full_key_path = f"{current_path}\\{key}" if current_path else key
                changes.append(f"RM - Добавлен ключ: {full_key_path}")
                # Рекурсивно добавляем все его значения и под-ключи
                if isinstance(new_data, dict):
                    for sub_key, sub_data in new_data.items():
                        if isinstance(sub_data, dict): #  Это под-ключ
                            changes.extend(self.compare_snapshots(old_snapshot.get(key, {}), {sub_key: sub_data}, full_key_path))
                        else:
                            changes.append(f'RM - Добавлено значение: "{sub_key}" (Тип: {sub_data.get("type")}) = {sub_data.get("data")}')
                else:
                    changes.append(f'RM - Добавлено значение: "{key}" (Тип: {new_data.get("type")}) = {new_data.get("data")}')
            else:
                # Ключ существует, проверяем изменения в значениях
                old_data = old_snapshot[key]
                if isinstance(new_data, dict) and isinstance(old_data, dict):
                    # Рекурсивно сравниваем под-ключи
                    changes.extend(self.compare_snapshots(old_data, new_data, f"{current_path}\\{key}" if current_path else key))
                elif isinstance(new_data, dict) and not isinstance(old_data, dict):
                    # Ключ был значением, а стал словарем (под-ключом)
                    full_key_path = f"{current_path}\\{key}" if current_path else key
                    changes.append(f"RM - Изменен тип ключа: {full_key_path} (был значением, стал ключом)")
                    # Добавляем все новые значения и под-ключи
                    for sub_key, sub_data in new_data.items():
                        if isinstance(sub_data, dict):
                            changes.extend(self.compare_snapshots({}, {sub_key: sub_data}, full_key_path))
                        else:
                            changes.append(f'RM - Добавлено значение: "{sub_key}" (Тип: {sub_data.get("type")}) = {sub_data.get("data")}')
                elif not isinstance(new_data, dict) and isinstance(old_data, dict):
                    # Ключ был словарем, а стал значением
                    full_key_path = f"{current_path}\\{key}" if current_path else key
                    changes.append(f"RM - Изменен тип ключа: {full_key_path} (был ключом, стал значением)")
                    changes.append(f'RM - Новое значение: "{key}" (Тип: {new_data.get("type")}) = {new_data.get("data")}')
                elif not isinstance(new_data, dict) and not isinstance(old_data, dict):
                    # Сравниваем значения
                    if new_data.get("data") != old_data.get("data") or new_data.get("type") != old_data.get("type"):
                        full_key_path = f"{current_path}\\{key}" if current_path else key
                        changes.append(f'RM - Изменено значение: "{full_key_path}"')
                        changes.append(f'RM - Старое: (Тип: {old_data.get("type")}) = {old_data.get("data")}')
                        changes.append(f'RM - Новое: (Тип: {new_data.get("type")}) = {new_data.get("data")}')

        # Проверяем удаленные ключи и значения
        for key, old_data in old_snapshot.items():
            if key not in new_snapshot:
                full_key_path = f"{current_path}\\{key}" if current_path else key
                if isinstance(old_data, dict):
                    changes.append(f"RM - Удален ключ: {full_key_path}")
                    # Рекурсивно добавляем все его значения и под-ключи как удаленные
                    for sub_key, sub_data in old_data.items():
                        if isinstance(sub_data, dict):
                            changes.extend(self.compare_snapshots({sub_key: sub_data}, {}, full_key_path))
                        else:
                            changes.append(f'RM - Удалено значение: "{sub_key}" (Тип: {sub_data.get("type")}) = {sub_data.get("data")}')
                else:
                    changes.append(f'RM - Удалено значение: "{full_key_path}" (Тип: {old_data.get("type")}) = {old_data.get("data")}')

        return changes

    def run(self):
        h_key = None
        h_event = None
        previous_snapshot = {}

        try:
            # Открываем ключ реестра
            h_key = wintypes.HKEY()
            result = self.ADVAPI32.RegOpenKeyExW(
                self.hive,
                self.key_path,
                0,
                KEY_READ | KEY_ENUMERATE_SUB_KEYS,
                ctypes.byref(h_key)
            )

            if result != 0:
                logger.error(f"RM - Ошибка открытия ключа {self.key_path}: код {result}")
                if self.event_queue:
                    self.event_queue.put(f"RM - Ошибка открытия ключа ({self.key_path})")
                return

            logger.success(f"RM - Ключ открыт успешно: {self.key_path}")

            # Получаем начальный снимок реестра
            previous_snapshot = self.get_full_registry_snapshot(h_key, self.key_path)
            if previous_snapshot:
                self.event_queue.put(f"RM - Начальное состояние реестра ({self.key_path})")
                for key, data in previous_snapshot.items():
                    if isinstance(data, dict):
                        self.event_queue.put(f"Ключ: {key}")
                        for sub_key, sub_data in data.items():
                            if isinstance(sub_data, dict):
                                self.event_queue.put(f"Подключ: {sub_key}")
                            else:
                                self.event_queue.put(f'Значение: "{sub_key}" (Тип: {sub_data.get("type")}) = {sub_data.get("data")}')
                    else:
                        self.event_queue.put(f'Значение: "{key}" (Тип: {data.get("type")}) = {data.get("data")}')
                self.event_queue.put("RM - Конец сканирования начального состояния")
            else:
                if self.DEBUG_MODE:
                    self.event_queue.put(f"RM - Нет данных для отображения при инициализации ({self.key_path})")

            # Создаем событие для уведомлений
            h_event = self.kernel32.CreateEventW(None, True, False, None)
            if not h_event:
                logger.error(f"RM - Ошибка создания события")
                if self.event_queue:
                    self.event_queue.put(f"RM - Ошибка создания события ({self.key_path})")
                return

            # Основной цикл мониторинга
            while not self.stop_event.is_set():
                # Регистрируем уведомление об изменениях
                result = self.ADVAPI32.RegNotifyChangeKeyValue(
                    h_key,
                    self.watch_subtree,
                    NOTIFY_FLAGS,
                    h_event,
                    True # Асинхронное уведомление
                )

                if result != 0:
                    logger.error(f"RM - Ошибка регистрации уведомления: код {result}")
                    if self.event_queue:
                        self.event_queue.put(f"RM - Ошибка регистрации уведомления ({self.key_path})")
                    break

                # Ждем события с timeout секунду
                wait_result = self.kernel32.WaitForSingleObject(h_event, 1000)

                if wait_result == WAIT_OBJECT_0:
                    # Событие срабатывало — произошло изменение
                    logger.info(f"RM - Обнаружено изменение в {self.key_path}")

                    # Получаем новый снимок и сравниваем
                    current_snapshot = self.get_full_registry_snapshot(h_key, self.key_path)
                    changes = self.compare_snapshots(previous_snapshot, current_snapshot, self.key_path)

                    if changes:
                        self.event_queue.put(f"RM - Обнаружены изменения в {self.key_path}")
                        for change in changes:
                            self.event_queue.put(change)
                        self.event_queue.put("RM - Конец изменений")
                        previous_snapshot = current_snapshot # Обновляем снимок

                    # Сбрасываем событие для следующего уведомления
                    self.kernel32.ResetEvent(h_event)

                elif wait_result == WAIT_TIMEOUT:
                    # Timeout — ничего не изменилось, продолжаем ждать
                    pass

                else:
                    # Ошибка ожидания
                    logger.warning(f"RM - Ошибка ожидания события: {wait_result}")
                    if self.event_queue:
                        self.event_queue.put(f"RM - Ошибка ожидания события ({self.key_path})")

        except Exception as e:
            logger.exception("RM - Критическая ошибка в мониторе реестра")
            if self.event_queue:
                self.event_queue.put(f"RM - Критическая ошибка мониторинга реестра ({self.key_path}):\n{e}")

        finally:
            # Закрытие дескрипторов
            if h_key:
                self.ADVAPI32.RegCloseKey(h_key)
                logger.info(f"RM - Ключ закрыт: {self.key_path}")
                if self.event_queue:
                    self.event_queue.put(f"RM - Мониторинг реестра остановлен ({self.key_path})")

            if h_event:
                self.kernel32.CloseHandle(h_event)
                logger.info(f"RM - Событие закрыто")

    def stop(self):
        logger.info(f"RM - Остановка мониторинга: {self.key_path}")
        self.stop_event.set()
        self.join(timeout=5)
