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
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
import subprocess
import os

# from RS import RS
from languages import l

GET_FULL_ACCESS_VERSION = "0.4.9 Alpha"

# Проверяем, является ли путь ключом реестра
def is_registry_path(path):
    registry_prefixes = [
        "HKEY_LOCAL_MACHINE", "HKLM",
        "HKEY_CURRENT_USER", "HKCU",
        "HKEY_CLASSES_ROOT", "HKCR",
        "HKEY_CURRENT_CONFIG", "HKCC",
        "HKEY_USERS", "HKU"
    ]
    return any(path.upper().startswith(prefix) for prefix in registry_prefixes)



# Устанавливаем полные права на файл или каталог
def grant_file_access(path, username):
    if not os.path.exists(path):
        logger.error(f'GFA - {l("not_dir")}: {path}')
        return False

    try:
        cmd = ["icacls", path, "/grant", f"{username}:F", "/T", "/C"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.success(f'GFA - {l("full_access_set")}: {path}')
            return True
        else:
            logger.error(f'GFA - {l("error")} icacls: {result.stderr}')
            return False

    except Exception as e:
        logger.exception(f'GFA - {l("file_error")}')
        return False



# Устанавливаем полные права на ключ реестра
def grant_registry_access(path, full_username):
    try:
        import win32security
        import ntsecuritycon as con
        import winreg
        import pywintypes
    except ImportError as e:
        logger.critical(f'GFA - {l("import_error")}!\n{e}')
        return False

    try:
        registry_path = normalize_registry_path(path)

        # Разбираем путь на корневой ключ и под-путь
        parts = registry_path.split("\\", 1)
        root_key_name = parts[0].upper()
        subkey_path = parts[1] if len(parts) > 1 else ""

        root_keys = {
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
            "HKEY_USERS": winreg.HKEY_USERS
        }

        if root_key_name not in root_keys:
            # logger.error(f"GFA - Неизвестный ключ реестра: {root_key_name}")
            return False

        root_key = root_keys[root_key_name]

        # Открываем ключ с доступом администратора
        try:
            key = winreg.OpenKey(root_key, subkey_path, 0, winreg.KEY_ALL_ACCESS)
        except PermissionError:
            logger.error(f'GFA - {l("permission_error")} {l("to_access")}: {registry_path}')
            return False
        except FileNotFoundError:
            logger.error(f'GFA - {l("key_not_found")}: {registry_path}')
            return False

        # Получаем SID пользователя
        try:
            sid = win32security.LookupAccountName(None, full_username)[0]
        except Exception as e:
            logger.exception(f'GFA - {l("get_sid_error")} {full_username}')
            winreg.CloseKey(key)
            return False

        # Получаем текущий дескриптор безопасности из ключа реестра
        try:
            sec_desc = win32security.GetSecurityInfo(
                int(key),
                win32security.SE_REGISTRY_KEY,
                win32security.DACL_SECURITY_INFORMATION
            )
        except Exception as e:
            logger.exception(f'GFA - {l("get_description_error")}')
            winreg.CloseKey(key)
            return False

        # Получаем текущий DACL
        try:
            dacl = sec_desc.GetSecurityDescriptorDacl()
        except:
            dacl = None

        if dacl is None:
            dacl = win32security.ACL()

        # Добавляем полные права (GENERIC_ALL) для пользователя, используем константы из ntsecuritycon
        try:
            dacl.AddAccessAllowedAceEx(
                win32security.ACL_REVISION,
                con.CONTAINER_INHERIT_ACE | con.OBJECT_INHERIT_ACE,  #  Правильные флаги наследования
                con.GENERIC_ALL,
                sid
            )
        except Exception as e:
            logger.exception(f'GFA - {l("ace_error")}')
            winreg.CloseKey(key)
            return False

        # Устанавливаем новый DACL через дескриптор ключа
        try:
            sec_desc.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetSecurityInfo(
                int(key),
                win32security.SE_REGISTRY_KEY,
                win32security.DACL_SECURITY_INFORMATION,
                None,
                None,
                dacl,
                None
            )
        except Exception as e:
            logger.exception(f'GFA - {l("set_access_error")}')
            winreg.CloseKey(key)
            return False

        logger.success(f'GFA - {l("success_set_full_access")}: {registry_path}')
        winreg.CloseKey(key)
        return True

    except Exception as e:
        logger.exception(f'GFA - {l("regedit_error")}')
        return False



def normalize_registry_path(path):
    registry_map = {
        "HKLM": "HKEY_LOCAL_MACHINE",
        "HKCU": "HKEY_CURRENT_USER",
        "HKCR": "HKEY_CLASSES_ROOT",
        "HKCC": "HKEY_CURRENT_CONFIG",
        "HKU": "HKEY_USERS"
    }

    for short, full in registry_map.items():
        if path.upper().startswith(short + "\\"):
            path = full + path[len(short):]
            break

    return path



# Получаем полные права на файл, каталог или ключ реестра
def GFA(path, RUN_IN_RECOVERY=False):
    """
    Универсальная функция для получения полных прав на каталог, файл или ключ реестра
    path - путь к каталогу, файлу или ключ реестра
    RUN_IN_RECOVERY - Код работает в среде восстановления? Тогда True
    return - False при ошибке, True при удачном завершении операции
    """
    # if RUN_IN_RECOVERY:
    #     messagebox.showwarning(RS(), "Невозможно получить права в среде восстановления.")
    #     return False

    try:
        username = os.getenv("USERNAME")
        domain = os.getenv("USERDOMAIN")
        full_username = f"{domain}\\{username}"

        if is_registry_path(path):
            return grant_registry_access(path, full_username)
        else:
            return grant_file_access(path, username)

    except Exception as e:
        logger.exception(f'GFA - {l("error")}')
        return False
