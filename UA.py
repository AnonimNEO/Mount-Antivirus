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
from tkinter import messagebox
from RS import RS
# Работа с реестром и списками
from typing import Tuple, Any
import winreg
import os
# Логирование
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger

# from OF2 import get_offline_reg_path, loaded_hive_names
from OF import get_offline_reg_path, loaded_hive_names
from languages import l

UNLOCK_ALL_VERSION = "1.2.10 Beta"

# Возвращает безопасное "нулевое" значение для сброса параметра
def get_new_value_for_type(reg_type: int) -> Tuple[Any, int]:
    if reg_type in (winreg.REG_DWORD, winreg.REG_QWORD):
        return 0, reg_type
    elif reg_type in (winreg.REG_SZ, winreg.REG_EXPAND_SZ):
        return "", reg_type
    elif reg_type == winreg.REG_MULTI_SZ:
        return [], reg_type
    elif reg_type == winreg.REG_BINARY:
        return b"", reg_type
    return None, reg_type



# Восстанавливает шрифты в реестре на основе файлов из C:\Windows\Fonts
def restore_fonts(UA_GLOBALS, RUN_IN_RECOVERY, DEBUG_MODE=False):
    try:
        fonts_dir = r"C:\Windows\Fonts"
        registry_key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"

        logger.info(f'UA - {l("start_recovery_font")}...')

        # Проверяем наличие каталога шрифтов
        if not os.path.isdir(fonts_dir):
            logger.critical(f'UA - {l("font_dir_not_found")}: {fonts_dir}')
            return False

        # Получаем корректный путь в зависимости от среды
        final_hkey, final_subkey = get_offline_reg_path(
            winreg.HKEY_LOCAL_MACHINE,
            registry_key,
            UA_GLOBALS,
            RUN_IN_RECOVERY
        )

        key_handle = None

        # Открываем ключ реестра для чтения и записи
        key_handle = winreg.OpenKey(
            final_hkey,
            final_subkey,
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE | winreg.KEY_ENUMERATE_SUB_KEYS
        )

        # Получаем список файлов шрифтов из папки
        font_files = os.listdir(fonts_dir)
        supported_extensions = (".ttf", ".otf")

        fonts_found = 0
        fonts_restored = 0

        # Обрабатываем каждый файл шрифта
        for font_file in font_files:
            if not font_file.lower().endswith(supported_extensions):
                continue

            fonts_found += 1
            # font_path = os.path.join(fonts_dir, font_file)

            try:
                # Формируем имя параметра в реестре
                font_name = os.path.splitext(font_file)[0]

                # Проверяем, есть ли уже такой параметр
                try:
                    current_value = winreg.QueryValueEx(key_handle, font_name)[0]
                    # Если значение пустое или не указывает на реальный файл, обновляем
                    if not current_value or not current_value.endswith(font_file):
                        winreg.SetValueEx(key_handle, font_name, 0, winreg.REG_SZ, font_file)
                        fonts_restored += 1
                        logger.success(f'UA - {l("font")} "{font_name}" {l("restored")}.')
                    else:
                        if DEBUG_MODE:
                            logger.debug(f'UA - {l("font")} "{font_name}" {l("restored")}.')

                except FileNotFoundError:
                    # Параметра нет в реестре, добавляем его
                    winreg.SetValueEx(key_handle, font_name, 0, winreg.REG_SZ, font_file)
                    fonts_restored += 1
                    logger.success(f'UA - {l("font")} "{font_name}" {l("add_in_registry")}.')

            except Exception as e:
                logger.exception(f'UA -  "{font_file}"')

        # Удаляем записи о шрифтах, которых нет в каталоге
        orphaned_count = 0
        try:
            i = 0
            while True:
                try:
                    param_name, param_value, _ = winreg.EnumValue(key_handle, i)

                    # Проверяем, существует ли указанный файл
                    if isinstance(param_value, str):
                        font_file_in_registry = os.path.basename(param_value)
                        full_path = os.path.join(fonts_dir, font_file_in_registry)

                        if not os.path.isfile(full_path):
                            winreg.DeleteValue(key_handle, param_name)
                            orphaned_count += 1
                            logger.warning(f'UA - {l("delete_orphan_font")} "{param_name}"')
                            continue

                    i += 1
                except OSError:
                    break
        except Exception as e:
            logger.exception(f'UA - {l("delete_orphan_font_error")}')

        logger.info(f'UA - {l("recovery_font_complete")}: {fonts_found}, {l("restored")}: {fonts_restored}, {l("removed_orphans")}: {orphaned_count}')
        return True

    except FileNotFoundError:
        logger.critical(f'UA - {l("key_not_found")}: {registry_key}')
        return False
    except PermissionError:
        logger.critical(f'UA - {l("permission_error")}: {registry_key}')
        return False
    except Exception as e:
        exception(f'UA - {l("recovery_font_error")}')
        return False
    finally:
        if key_handle:
            winreg.CloseKey(key_handle)



# Сбрасывает указанные параметры в разделе реестра с учетом оффлайн-режима
def reset_reg_values(hkey_const, chapter, params, UA_GLOBALS, is_exception, RUN_IN_RECOVERY):
    """
    Функция для сброса значений реестра

    Аргументы:
    :hkey_const - Куст реестра (например HKEY_LOCAL_MACHINE или HKEY_CURRENT_USER).
    :chapter - путь к разделу реестра.
    :params - Список имён параметров, если список пустой значит все параметры.
    :UA_GLOBALS - Глобальная переменная офлайн путей к реестру.
    :is_exception - Список params это исключения или включения?
    :RUN_IN_RECOVERY - Код работает в среде восстановления?
    """
    key_handle = None
    hive_name = UA_GLOBALS["HKEY_MAP"].get(hkey_const, str(hkey_const))

    # Получаем корректный путь в зависимости от среды
    final_hkey, final_subkey = get_offline_reg_path(hkey_const, chapter, UA_GLOBALS, RUN_IN_RECOVERY)

    # logger.debug(f"UA - Обработка раздела: {hive_name}\\{chapter} (Режим исключений: {is_exception})")

    try:
        # Открываем ключ с правами на чтение и запись
        # KEY_QUERY_VALUE нужен для перечисления параметров, KEY_SET_VALUE для изменения
        key_handle = winreg.OpenKey(final_hkey, final_subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE | winreg.KEY_ENUMERATE_SUB_KEYS)

        targets = []

        if is_exception:
            # получаем список всех параметров в разделе
            try:
                i = 0
                while True:
                    # Получаем имя параметра по индексу
                    param_name, _, _ = winreg.EnumValue(key_handle, i)
                    # Если имени нет в списке исключений — добавляем в очередь на сброс
                    if param_name not in params:
                        targets.append(param_name)
                    i += 1
            except OSError:
                # OSError возникает, когда параметры для перечисления закончились
                pass
        else:
            # работаем только с тем, что передали в списке
            targets = params

        # Процесс сброса
        for param in targets:
            try:
                # Уточняем текущий тип параметра
                _, reg_type = winreg.QueryValueEx(key_handle, param)
                new_val, r_type = get_new_value_for_type(reg_type)

                if new_val is not None:
                    winreg.SetValueEx(key_handle, param, 0, r_type, new_val)
                    logger.success(f'UA - {l("parameter")} "{param}" {l("successfully_reset_to")} {hive_name}\\{chapter}')
                else:
                    logger.warning(f'UA - {l("unsupported_type_for")} "{param}" {l("in")} {hive_name}\\{chapter}')

            except FileNotFoundError:
                logger.debug(f'UA - {l("parameter")} "{param}" {l("not_found_pass")}.')
            except Exception as e:
                logger.exception(f'UA - {l("reset_error")} "{param}"')

        return True
    except FileNotFoundError:
        logger.warning(f'UA - {l("key_not_found")}: {hive_name}\\{chapter}')
        return False
    except PermissionError:
        logger.critical(f'UA - {l("permission_error")}: {hive_name}\\{chapter}')
        return False
    except Exception as e:
        logger.exception(f'UA - {l("read_key_error")} {chapter}')
        return False
    finally:
        if key_handle:
            winreg.CloseKey(key_handle)



# Обработка файла hosts
def process_hosts_file(fix=False, exclude_hosts=None):
    # Проверяет файл hosts и при необходимости исправляет.
    # :param fix: если True, удаляем блокировки
    # :param exclude_hosts: список имен хостов, исключенных из блокировки
    hosts_path = os.path.join(os.environ["SystemRoot"], "System32", "drivers", "etc", "hosts")
    try:
        with open(hosts_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        blocked_hosts = []
        new_lines = []

        for line in lines:
            striped = line.strip()
            if not striped or striped.startswith("# "):
                new_lines.append(line)
                continue
            parts = striped.split()
            if len(parts) >= 2:
                ip, hostname = parts[0], parts[1]
                if ip in ("127.0.0.1", "0.0.0.0", "::1"):
                    blocked_hosts.append(hostname)
                    if not fix:
                        new_lines.append(line)
                    # если fix=True, пропускаем (удаляем блокировки)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        if blocked_hosts:
            logger.warning(f'UA - {l("block_detect")} hosts: {blocked_hosts}')
            if fix:
                # удаляем блокировки
                with open(hosts_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                logger.info(f'UA - {l("delete_block")}: {", ".join(blocked_hosts)}')
        return True
    except Exception as e:
        logger.exception(f'UA - {l("file_error")} hosts')
        return False



# Обработка файла hosts с исключениями
def process_hosts_with_exclusions(exclude_hosts=None):
    return process_hosts_file(fix=True, exclude_hosts=exclude_hosts)



# Разблокировка всего
def UA(RUN_IN_RECOVERY=False, DEBUG_MODE=False):
    """Разблокируем ограничения, главная функция Компонента Разблокировки Всего (точка входа)"""
    try:
        # system_hive = loaded_hive_names.get("SYSTEM", "Offline_SYSTEM")
        software_hive = loaded_hive_names.get("SOFTWARE", "Offline_SOFTWARE")
        user_hive = loaded_hive_names.get("USER", "Offline_USER")

        UA_GLOBALS = {
            "OFFLINE_HKEY_MAP": {
                winreg.HKEY_LOCAL_MACHINE: (winreg.HKEY_LOCAL_MACHINE, software_hive, r"Software"),
                winreg.HKEY_CURRENT_USER: (winreg.HKEY_LOCAL_MACHINE, user_hive, None)
            },
            "HKEY_MAP": {
                winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
                winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER"
            }
        }

        # Список политик для сброса
        # Мышь
        mouse_restore_success = reset_reg_values(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", ["SwapMouseButtons"], UA_GLOBALS, False, RUN_IN_RECOVERY)

        # Ограничения проводника
        explorer_restore_success = reset_reg_values(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", [], UA_GLOBALS, True, RUN_IN_RECOVERY)

        # Системные политики (HKCU)
        user_restore_success = reset_reg_values(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", [], UA_GLOBALS, True, RUN_IN_RECOVERY)

        # Системные политики (HKLM)
        system_restore_success = reset_reg_values(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", [], UA_GLOBALS, True, RUN_IN_RECOVERY)

        # Восстановление шрифтов
        font_restore_success = restore_fonts(UA_GLOBALS, RUN_IN_RECOVERY, DEBUG_MODE)

        # файл hosts
        host_restore_success = process_hosts_with_exclusions()

        # Сообщение перед входом в систему
        legal_text_success = reset_reg_values(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Polices\System", ["legalnoticecaption", "legalnoticetext"], UA_GLOBALS, False, RUN_IN_RECOVERY)

        restore_success = [mouse_restore_success, explorer_restore_success, user_restore_success, system_restore_success, font_restore_success, host_restore_success, legal_text_success]
        restore_text = [l("mouse"), l("explorer"), l("user"), l("systems"), l("fonts"), "IP", l("legal_notice")]

        i = 0
        ua_text = ""
        for r in restore_success:
            if r:
                ua_text += f'{l("blocks")} {restore_text[i]}: {l("unlock")}\n'
            else:
                ua_text += f'{l("blocks")} {restore_text[i]}: {l("unlock_error")}\n'
            i += 1

        messagebox.showinfo(RS(), f'{l("au_result")}:\n{ua_text}')
    except Exception as e:
        logger.exception(l("ua_critical_error"))
        messagebox.showerror(RS(), f'{l("ua_critical_error")}\n{e}')

    logger.info(f'UA - {l("component_work_complete")}.')



# Если все параметры имеют одинаковые значения или в значениях нет .ttf .otf, восстанавливаем шрифты
def check_and_restore_fonts_if_needed(RUN_IN_RECOVERY, DEBUG_MODE=False):
    """Проверяем есть ли закономерность в шрифтах - если да то восстанавливаем шрифты"""
    registry_key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"

    logger.info(f'UA - {l("check_fonts")}...')

    try:
        # Инициализируем UA_GLOBALS для получения корректного пути реестра
        software_hive = loaded_hive_names.get("SOFTWARE", "Offline_SOFTWARE")
        user_hive = loaded_hive_names.get("USER", "Offline_USER")

        UA_GLOBALS = {
            "OFFLINE_HKEY_MAP": {
                winreg.HKEY_LOCAL_MACHINE: (winreg.HKEY_LOCAL_MACHINE, software_hive, r"Software"),
                winreg.HKEY_CURRENT_USER: (winreg.HKEY_LOCAL_MACHINE, user_hive, None)
            },
            "HKEY_MAP": {
                winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
                winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER"
            }
        }

        final_hkey, final_subkey = get_offline_reg_path(
            winreg.HKEY_LOCAL_MACHINE, 
            registry_key, 
            UA_GLOBALS,
            RUN_IN_RECOVERY
        )

        key_handle = None

        try:
            key_handle = winreg.OpenKey(
                final_hkey, 
                final_subkey, 
                0, 
                winreg.KEY_QUERY_VALUE | winreg.KEY_ENUMERATE_SUB_KEYS
            )

            # Получаем все параметры шрифтов
            font_params = {}
            try:
                i = 0
                while True:
                    param_name, param_value, param_type = winreg.EnumValue(key_handle, i)
                    font_params[param_name] = param_value
                    i += 1
            except OSError:
                pass

            # Флаги для проверки
            needs_restore = False
            all_values_same = False
            no_ttf_otf = False

            if font_params:
                # Проверяем, все ли значения одинаковые
                unique_values = set(font_params.values())
                if len(unique_values) == 1:
                    all_values_same = True
                    logger.warning(f'UA - {l("all_fonts=")}')
                    needs_restore = True

                # Проверяем наличие .ttf или .otf файлов в реестре
                has_ttf_otf = any(
                    value.lower().endswith((".ttf", ".otf"))
                    for value in font_params.values()
                )
                
                if not has_ttf_otf:
                    no_ttf_otf = True
                    logger.warning(f'UA - {l("not_ttf_or_otf")}')
                    needs_restore = True

            # Если проблемы обнаружены, запускаем восстановление
            if needs_restore:
                logger.warning(f'UA - {l("font_problem_detect")}...')
                restore_fonts(UA_GLOBALS, RUN_IN_RECOVERY, DEBUG_MODE)
                return True
            else:
                if DEBUG_MODE:
                    logger.debug(f'UA - {l("restore_fonts_check_success")}')
                return False

        except FileNotFoundError:
            logger.critical(f'UA - {l("key_not_found")}: {registry_key}')
            return False
        except PermissionError:
            logger.critical(f'UA - {l("permission_error")}: {registry_key}')
            return False
        except Exception as e:
            logger.exception(f'UA - {l("check_fonts_error")}')
            return False
        finally:
            if key_handle:
                winreg.CloseKey(key_handle)

    except Exception as e:
        logger.exception(f'UA - {l("check_fonts_error")}')
        return False

if __name__ == "__main__":
    UA(False)
