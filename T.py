# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

# Локализация
from languages import l

import ctypes
import time
import sys
import os

not_loguru = False
not_tkinter = False
not_pillow = False
not_pystray = False
not_bytesio = False
not_multiprocessing = False
not_threading = False
not_signal = False

try:
    # Логирование Ошибок
    try:
        from config import LOG_PATH
    except:
        LOG_PATH = ""
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    from OF import Logger
    logger = Logger()
    logger.add()
except:
    try:
        from loguru import logger
        logger.exception(f'T - {l("import_error")} loguru+AES')
    except:
        import logging
        not_loguru = True
        # Создаём заглушку логгера
        class Loggers:
            def __init__(self):
                self.setup_fallback_logger()

            # Настраиваем стандартный логгер как замену
            def setup_fallback_logger(self):
                self.logger = logging.getLogger(__name__)
                self.logger.setLevel(logging.ERROR)

                # Если логгер уже имеет обработчики, не добавляем новые
                if not self.logger.handlers:
                    handler = logging.StreamHandler(sys.stdout)
                    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
                    handler.setFormatter(formatter)
                    self.logger.addHandler(handler)

            def debug(self, message):
                self.logger.debug(message)

            def info(self, message):
                self.logger.info(message)

            def warning(self, message):
                self.logger.warning(message)

            def error(self, message):
                self.logger.error(message)

            def critical(self, message):
                self.logger.critical(message)

            def success(self, message):
                self.logger.info(f'[SUCCESS] {message}')

            def exception(self, message):
                self.logger.exception(message)

            def add(self, *args, **kwargs):
                pass

        logger = Loggers()

        logger.exception(f'T - {l("import_error")} loguru! {l("replacement_is_used")}')

# Интерфейс
try:
    from tkinter import messagebox, simpledialog
    import tkinter as tk
except:
    not_tkinter = True
    logger.exception(f'T - {l("import_error")} tkinter')
    with open('fatal_error.txt', 'w') as f:
        f.write(f'{l("fatal_error")} {l("in_start_crowbar")}')
    os.startfile('fatal_error.txt')

try:
    # Рисование иконки в трее и вставка картинок
    from PIL import Image, ImageDraw, ImageFont
except:
    not_pillow = True
    logger.exception(f'T - {l("import_error")} Pillow')

# Движок иконки в трее
try:
    from pystray import MenuItem, Menu
    import pystray
except:
    not_pystray = True
    logger.exception(f'T - {l("import_error")} pystray')

# Работа с потоками
try:
    from io import BytesIO
except:
    not_bytesio = True
    logger.exception(f'T - {l("import_error")} BytesIO')

try:
    import multiprocessing
except:
    not_multiprocessing = True
    logger.exception(f'T - {l("import_error")} multiprocessing')

try:
    import threading
except:
    not_threading = True
    logger.exception(f'T - {l("import_error")} threading')

try:
    import signal
except:
    not_signal = True
    logger.exception(f'T - {l("import_error")} signal')

not_ap = False
not_arm = False
not_b = False
not_cc = False
not_config = False
not_e = False
not_ec = False
not_fe = False
not_fm = False
not_fr = False
not_rlp = False
not_cm = False
not_of = False
not_pm = False
not_r = False
not_rs = False
not_run = False
not_sau = False
not_sp = False
not_ua = False
not_um = False
not_console = False
not_rm = False
not_sim = False

# Импорт Компонентов
# from OBPC import OBPC, on_board_pc_version

try:
    from AES import AES
except:
    not_cc2 = True
    def AES(a=None, b=None, c=None):
        return "error"
    logger.exception(f'T - {l("component_import_error")} AES')

try:
    from AP import AP
except:
    not_ap = True
    logger.exception(f'T - {l("component_import_error")} AboutImage')

try:
    from ARM import ARM, AUTORUN_MASTER_VERSION
except:
    not_arm = True
    logger.exception(f'T - {l("component_import_error")} AutoRunMaster')

try:
    from RS import RS, RANDOM_STRING_VERSION
except:
    def RS(a=None):
        return "error"
    not_rs = True
    logger.exception(f'T - {l("component_import_error")} RandomString')

# try:
#     from B import B, browser_version
# except:
#     not_b = True
#     def B(a=None, b=None, c=None, d=None, e=None):
#         pass
#     logger.exception(f"T - {l("component_import_error")} Browser")

try:
    from CC import CC, CLEAR_CACHE_VERSION
except:
    not_cc = True
    logger.exception(f'T - {l("component_import_error")} ClearCache')

try:
    from config import LOG_PATH, T_LOG_TXT, THEME, DEFAULT_THEME, PROGRAM_AUTHENTICATION_CLYTH, START_INTERFACE, START_CASH, START_LP, DOCUMENTATION_HTML
    import config
except:
    not_config = True
    logger.exception(f'T - {l("import_error")} config!')

try:
    from E import E, EXIT_VERSION
except:
    not_e = True
    def E():
        pass
    logger.exception(f'T - {l("component_import_error")} Exit')

try:
    from EC import EC, EDIT_CRITICALITY_VERSION
except:
    not_ec = True
    def EC():
        pass
    logger.exception(f'T - {l("component_import_error")} EditCritical')

try:
    from FE import FE, FILE_EDITOR_VERSION
except:
    not_fe = True
    logger.exception(f'T - {l("component_import_error")} FileEditor')

try:
    from FM import FM, FILE_MANAGER_VERSION
except:
    not_fm = True
    logger.critical(f'T - {l("component_import_error")} FileManager')

try:
    from FR import FR, FILE_REPLACER_VERSION
except:
    not_fr = True
    logger.exception(f'T - {l("component_import_error")} FileReplacer')

try:
    from GFA import GFA, GET_FULL_ACCESS_VERSION
except:
    def GFA():
        pass
    logger.exception(f'T - {l("component_import_error")} GetFullAccess')

try:
    from RLP import RLP, REAL_TIME_PROTECT_VERSION
except:
    not_rlp = True
    logger.exception(f'T - {l("component_import_error")} RealTimeProtection')

try:
    from CM import CM, CROWBAR_MENU_VERSION
except:
    not_cm = True
    crowbar_menu_version = "error"
    def CM(a=None, b=None, c=None):
        pass
    logger.exception(f'T - {l("component_import_error")} MountUnlocker')

try:
    from OF import pac, apply_global_theme, get_offline_reg_path, Psutil, run_component, run_component_process, get_user_name, restart_ca, reg_file, run_command, open_with, get_current_disc, load_bush, unload_bush, enable_debug_mode, OTHER_FUNCTION_VERSION, decoy_mode, extract_filename_from_path, launch_ghost, documentation
except:
    not_of = True
    def restart_ca():
        while True:
            input(">>> Fatal error")
    def open_with():
        pass
    def enable_debug_mode():
        pass
    def pac():
        messagebox.showerror(RS(), f'{l("pac")} {l("not_available")}!')
    #def CMD():
    #    pass
    def decoy_mode(a=None, b=None):
        pass
    def extract_filename_from_path(a=None, b=None):
        pass
    def launch_ghost(a=None):
        pass
    def documentation():
        pass
    logger.exception(f'T - {l("component_import_error")} OtherFunction')

try:
    from PM import PM, PROCESS_MANAGER_VERSION
except:
    not_pm = True
    logger.exception(f'T - {l("component_import_error")} ProcessManager')

try:
    from R import R, RESTART_VERSION
except:
    not_r = True
    def R():
        pass
    logger.exception(f'T - {l("component_import_error")} Restart')

try:
    from Run import Run, RUN_VERSION
except:
    not_run = True
    logger.exception(f'T - {l("component_import_error")} Run')

try:
    from SAU import SAU, SETTINGS_AND_UPDATE_VERSION
except:
    not_sau = True
    logger.exception(f'T - {l("component_import_error")} SettingsAndUpdate')

try:
    from SP import SP, SCARECROW_PROTECTION_VERSION
except:
    not_sp = True
    logger.exception(f'T - {l("component_import_error")} ScarecrowProtection')

try:
    from UA import UA, check_and_restore_fonts_if_needed, UNLOCK_ALL_VERSION
except:
    not_ua = True
    def check_and_restore_fonts_if_needed(a=None, b=None):
        pass
    logger.exception(f'T - {l("component_import_error")} UnlockAll')

try:
    from UM import UM, USER_MANAGER_VERSION
except:
    not_um = True
    logger.exception(f'T - {l("component_import_error")} UserManager')

try:
    from SIM import SIM, SOFTWARE_INSTALLATION_MANAGER
except:
    nor_sim = True
    logger.exception(f'T - {l("component_import_error")} SoftwareInstallationManager')

try:
    from RM import REGISTRY_MONITOR_VERSION
except:
    not_rm = True
    logger.exception(f'T - {l("component_import_error")} RegistryMonitor')

# Импорт консоли разработчика
try:
    from Console import open_console, CROWBAR_CONSOLE_VERSION
except:
    not_console = True
    logger.exception(f'T - {l("component_import_error")} Console')

# Импорт движка скриптов
try:
    from CASH import CASH, CROWBAR_ANTIVIRUS_SCRIPTS_HANDLER_VERSION
except:
    not_cash = True
    logger.exception(f'T - {l("component_import_error")} CASH')

try:
    if not_pystray and not_cm:
        c = l("component")
        li = l("library")
        na = l("not_available")
        na2 = l("not_available2")

        components = {
            "AP": not_ap, "ARM": not_arm, "B": not_b, "CC": not_cc,
            "E": not_e, "EC": not_ec, "FM": not_fm, "FR": not_fr,
            "RLP": not_rlp, "CM": not_cm, "OF": not_of, "PM": not_pm,
            "R": not_r, "RS": not_rs, "Run": not_run, "SAU": not_sau,
            "SP": not_sp, "UA": not_ua, "UM": not_um, "Console": not_console,
            "CASH": not_cash, "SIM": not_sim, "RM": not_rm,
        }

        libraries = {
            "loguru": not_loguru, "tkinter": not_tkinter, "pillow": not_pillow, "pystray": not_pystray,
            "bytesio": not_bytesio, "multiprocessing": not_multiprocessing, "threading": not_threading, "signal": not_signal,
        }

        broken_components = (
                [f"{c} {name}: {na}" for name, status in components.items() if status] +
                [f"{li} {name}: {na2}" for name, status in libraries.items() if status]
        )

        critical_error = (
                f'{l("critical_fail_detect")}.\n'
                f'{l("damage")}:\n' +
                "\n".join(broken_components)
        )
        messagebox.showerror(RS(), critical_error)
except:
    logger.exception(f'T - {l("checking_damage_error")}')

global DEBUG_MODE
TREY_VERSION = "2.4.27 Beta"
ON_BOARD_PC_VERSION = l("not_stable")
DEBUG_MODE = False

def Crowbar():
    if DEBUG_MODE:
        messagebox.showwarning(RS(), l("warning_debug_mode_on"))

    current_disc = None

    def check_is_recovery():
        if os.environ.get("WINPE") == "1":
            return True
        return False

    try:
        try:
            RUN_IN_RECOVERY = check_is_recovery()
            if RUN_IN_RECOVERY:
                logger.warning(f'T - {l("RUN_IN_RECOVERY")}')
            else:
                logger.info(f'T - {l("run_in_normal")}')
        except:
            RUN_IN_RECOVERY = True
            logger.exception(f'T - {l("environment_error")}')

        if RUN_IN_RECOVERY:
            current_disc, found_disc = get_current_disc(RUN_IN_RECOVERY)
            if found_disc:
                logger.info(f'T - {l("load_bush")} {current_disc}...')
                load_bush(current_disc)

    except:
        comment = f'T - {l("runtime_error")}'
        logger.exception(comment)
        messagebox.showerror(RS(), f'{comment}:\n{e}')

    check_and_restore_fonts_if_needed(RUN_IN_RECOVERY, DEBUG_MODE)

    # Основная программа
    try:
        current_theme = THEME[DEFAULT_THEME]
        if not RUN_IN_RECOVERY:
            try:
                _icon_buffer = None

                def create_image(width, height):
                    global _icon_buffer

                    icon_trey = Image.new("RGB", (width, height), (255, 0, 0))
                    square = ImageDraw.Draw(icon_trey)
                    square.rectangle((width // 2 - 10, height // 2 - 10, width // 2 + 10, height // 2 + 10), fill=(0, 0, 255))

                    font_paths = r"C:\Windows\Fonts\arial.ttf"

                    font = ImageFont.truetype(font_paths, 24)

                    if font is None:
                        font = ImageFont.load_default()
                        logger.warning(f'T - {l("use_default_font")}.')

                    text = "=]"
                    text_bbox = square.textbbox((0, 0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    text_position = (width // 2 - text_width // 2, height // 2 - text_height // 2)
                    square.text(text_position, text, fill=(255, 0, 0), font=font)

                    # Сохраняем буфер в глобальной переменной
                    _icon_buffer = BytesIO()
                    icon_trey.save(_icon_buffer, format="PNG")
                    _icon_buffer.seek(0)

                    return Image.open(_icon_buffer)

                def start_icon():
                    if RUN_IN_RECOVERY:
                        # logger.warning("T - Режим восстановления: Трей отключен.")
                        return
                    try:
                        icon.visible = True
                    except:
                        logger.exception(f'T - {l("trey_error")}')

                if RUN_IN_RECOVERY:
                    current_disc_r, found_disc = get_current_disc(RUN_IN_RECOVERY)
                else:
                    current_disc_r = "C:\\"

                # Создаём меню в зависимости от условия доступности компонента
                def create_menu_item(condition, enabled_text, enabled_func, component_name):
                    if condition:
                        disabled_text = f'[!] {l("component")} {component_name} {l("not_available")}.'
                        return MenuItem(disabled_text, lambda: None)
                    else:
                        return MenuItem(enabled_text, enabled_func)

                def t_enable_debug_mode():
                    global DEBUG_MODE
                    DEBUG_MODE = enable_debug_mode()

                menu_items = [
                    create_menu_item(not_arm, l("ARM"), lambda: run_component_process(ARM, RUN_IN_RECOVERY, current_theme, DEBUG_MODE), "ARM"),
                    create_menu_item(not_pm, l("PM"), lambda: run_component_process(PM, RUN_IN_RECOVERY, current_theme, DEBUG_MODE), "PM"),
                    create_menu_item(not_fm, l("FM"), lambda: run_component_process(FM, RUN_IN_RECOVERY, current_theme, DEBUG_MODE), "FM"),
                    create_menu_item(not_fr, l("FR"), lambda: run_component(FR, RUN_IN_RECOVERY, current_theme, DEBUG_MODE), "FR"),
                    create_menu_item(not_um, l("UM"), lambda: run_component(UM, current_theme, DEBUG_MODE), "UM"),
                    create_menu_item(not_fe, l("FE"), lambda: run_component(FE, None, current_theme), "FE"),
                    # create_menu_item(not_b, l("B"), lambda: run_component(B, RUN_IN_RECOVERY), "B"),
                    create_menu_item(not_sp, l("SP"), lambda: run_component(SP, RUN_IN_RECOVERY, current_disc_r, current_theme, DEBUG_MODE), "SP"),
                    create_menu_item(not_cc, l("CC"), lambda: run_component(CC, RUN_IN_RECOVERY), "CC"),
                ]

                if DEBUG_MODE:
                    menu_items.extend([
                        create_menu_item(not_sim, l("SIM"), lambda: run_component(SIM, RUN_IN_RECOVERY, current_theme, DEBUG_MODE), "SIM"),
                        create_menu_item(not_rlp, l("RLP"), lambda: run_component(RLP, RUN_IN_RECOVERY), "RLP"),
                        create_menu_item(not_console, l("Console"), lambda: open_console({
                            "run_component": run_component,
                            "run_component_process": run_component_process,
                            "RUN_IN_RECOVERY": RUN_IN_RECOVERY,
                            "current_theme": current_theme,
                            "DEBUG_MODE": DEBUG_MODE,
                            "AP": AP,
                            "ARM": ARM,
                            "B": B,
                            "CC": CC,
                            "AES": AES,
                            "CM": CM,
                            "config": config,
                            "EC": EC,
                            "FE": FE,
                            "FM": FM,
                            "FR": FR,
                            "GFA": GFA,
                            # OF
                            "Psutil": Psutil,
                            "run_component": run_component,
                            "apply_global_theme": apply_global_theme,
                            "get_offline_reg_path": get_offline_reg_path,
                            "get_current_disc": get_current_disc,
                            "load_bush": load_bush,
                            "unload_bush": unload_bush,
                            "get_user_name": get_user_name,
                            "open_with": open_with,
                            "reg_file": reg_file,
                            "run_command": run_command,
                            "decoy_mode": decoy_mode,
                            "launch_ghost": launch_ghost,
                            "extract_filename_from_path": extract_filename_from_path,
                            "PM": PM,
                            "RLP": RLP,
                            "RS": RS,
                            "Run": Run,
                            "SAU": SAU,
                            "SP": SP,
                            "UA": UA,
                            "UM": UM,
                            "logger": logger,
                        }, DEBUG_MODE), "Console"),
                    ])

                menu_items.extend([
                    #create_menu_item(not_of, "CMD", lambda: run_component(CMD), "OF"),
                    create_menu_item(not_of, l("open_with"), open_with, "OF"),
                    create_menu_item(not_of, l("enable_debug_mode"), t_enable_debug_mode, 'OF'),
                    create_menu_item(not_r, l("R"), R, "R")
                ])

                unlocker_menu = Menu(*menu_items)

                # Меню По ПКМ
                image = create_image(20, 20)
                del(_icon_buffer)
                menu = Menu(
                    create_menu_item(not_cm, f'{l("open")} {l("CM")}', lambda: run_component(CM, RUN_IN_RECOVERY, current_theme, DEBUG_MODE), "CM"),
                    MenuItem(l("utilities"), unlocker_menu),
                    create_menu_item(not_ua, l("UA"), lambda: UA(RUN_IN_RECOVERY, DEBUG_MODE), "UA"),
                    create_menu_item(not_run, l("Run"), lambda: run_component_process(Run, current_theme), "Run"),
                    create_menu_item(not_ap, l("AP"), lambda: run_component(AP,
                        AUTORUN_MASTER_VERSION,
                        CROWBAR_ANTIVIRUS_SCRIPTS_HANDLER_VERSION,
                        CLEAR_CACHE_VERSION,
                        CROWBAR_MENU_VERSION,
                        CROWBAR_CONSOLE_VERSION,
                        EXIT_VERSION,
                        EDIT_CRITICALITY_VERSION,
                        FILE_EDITOR_VERSION,
                        FILE_MANAGER_VERSION,
                        FILE_REPLACER_VERSION,
                        GET_FULL_ACCESS_VERSION,
                        ON_BOARD_PC_VERSION,
                        OTHER_FUNCTION_VERSION,
                        PROCESS_MANAGER_VERSION,
                        RESTART_VERSION,
                        REAL_TIME_PROTECT_VERSION,
                        REGISTRY_MONITOR_VERSION,
                        RANDOM_STRING_VERSION,
                        RUN_VERSION,
                        SETTINGS_AND_UPDATE_VERSION,
                        SOFTWARE_INSTALLATION_MANAGER,
                        SCARECROW_PROTECTION_VERSION,
                        TREY_VERSION,
                        UNLOCK_ALL_VERSION,
                        USER_MANAGER_VERSION
                    ), "AP"),
                    # create_menu_item(not_b, l("documentation"), lambda: run_component(B, documentation_html), "B"),
                    create_menu_item(not_tkinter, l("documentation"), documentation, "B"),
                    create_menu_item(not_sau, l("SAU"), lambda: run_component(SAU, current_theme), "SAU"),
                    create_menu_item(not_config, f'{l("pac")} - {PROGRAM_AUTHENTICATION_CLYTH}', pac, "config"),
                    create_menu_item(not_e, l("E"), E, "Exit")
                )

                icon = pystray.Icon("Crowbar_Antivirus_Icon", image, "Crowbar Antivirus", menu)

                if START_INTERFACE == "icon" or START_INTERFACE == "window":
                    try:
                        thread_icon = threading.Thread(target=icon.run)
                        thread_icon.daemon = True
                        thread_icon.start()

                        start_icon()
                    except:
                        logger.exception(f'T - {l("icon_start_error")}!')
                if START_LP:
                    run_component(RLP)

                if START_INTERFACE == "window" or START_INTERFACE == "only-windows":
                    run_component(CM, RUN_IN_RECOVERY, current_theme)

                if START_CASH:
                    try:
                        cash_thread = threading.Thread(target=CASH, args=(RUN_IN_RECOVERY, DEBUG_MODE), daemon=True)
                        cash_thread.start()
                    except:
                        logger.exception(f'T - {l("start_cash_error")}!')

                while True:
                    time.sleep(1)
            except:
                logger.exception(f'T - {l("icon_start_error")}!')
                CM(RUN_IN_RECOVERY, current_theme, current_disc)

        if RUN_IN_RECOVERY:
            CM(RUN_IN_RECOVERY, current_theme, current_disc)

    except:
        logger.exception(l("t_critical_error"))
        CM(RUN_IN_RECOVERY, current_theme, current_disc)
    finally:
        if RUN_IN_RECOVERY:
            logger.info(f'T - {l("unload_bush")}')

        if not RUN_IN_RECOVERY:
            signal.signal(signal.SIGTERM, restart_ca)

if __name__ == "__main__":
    try:
        multiprocessing.freeze_support()
    except:
        logger.exception(f'T - {l("multiprocessing_error")}')

    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            try:
                Crowbar()
            except Exception as e:
                comment = f'T - {l("t_critical_error")}'
                logger.exception(comment)
                if messagebox.askyesno(RS(), f'{comment}:\n{e}\n\n{l("restart_program")}?'):
                    Crowbar()
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    except Exception as e:
        admin_error = f'T - {l("admin_error")}'
        logger.exception(admin_error)
        messagebox.showerror(RS(), f'{admin_error}:\n{e}')
        restart_ca()