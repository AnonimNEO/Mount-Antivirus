# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

# Зачем нужен данный модуль? Из-за UA возникала ошибка цикличного импорта так, что это своего рода заглушка. Так что имеем, что имеем.

# Логирование Ошибок
from loguru import logger
# Работа с реестром
import winreg

global load_bush
OTHER_FUNCTION2_VERSION = "0.6.5 Beta"

# Глобальные имена загруженных кустов
loaded_hive_names = {"SYSTEM": "Offline_SYSTEM", "SOFTWARE": "Offline_SOFTWARE", "USER": "Offline_USER"}

# Глобальные имена для загрузки кустов
HIVE_MAP = {"SYSTEM": "Offline_SYSTEM", "SOFTWARE": "Offline_SOFTWARE", "USER": "Offline_USER"}

# Список для отслеживания загруженных кустов
active_loaded_hives = []

# Заглушка, библиотеки psutil которая всегда возвращает False/None.
class Psutil:
    def cpu_percent(self, *args, **kwargs):
        return 0.0

    def virtual_memory(self, *args, **kwargs):
        class MemStub:
            percent = 0.0
            total = 1024 * 1024 # Имитируем 1МБ ОЗУ, чтобы не падал RLP.py

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
            path_after_software = subkey_path[len("Software"):].strip("\\")
            # Путь: HKEY_LOCAL_MACHINE\Offline_SOFTWARE\{путь_после_Software}
            new_subkey_path = f"{temp_name}\\{path_after_software}"
            return new_hkey, new_subkey_path

    return hkey_const, subkey_path
