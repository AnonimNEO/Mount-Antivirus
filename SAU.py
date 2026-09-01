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
from tkinter import ttk, filedialog, messagebox, simpledialog
import tkinter as tk
# Дата и Время
from datetime import datetime
# Работа с реестром
import winreg as reg
# Работа с Файлами
import win32com.client
import shutil
import os
# Работа с Архивами
import zipfile
# Работа с выражениями
import ast
import re
# Логирование
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
import threading

# Чтение конфига
import config
from config import THEME, DEFAULT_THEME, PROGRAM_AUTHENTICATION_CLYTH
from languages import l
# Запуск команд
from OF import run_command, apply_global_theme
# Случайные заголовки
from RS import RS

SETTINGS_AND_UPDATE_VERSION = "1.2.7 Beta"

def compiling_crowbar():
    global COMPILING_COMMAND
    logger.info(f'{l("launch")} {l("compilations")}...\n{l("launch")} {l("commands")}: {COMPILING_COMMAND}')
    result = run_command(COMPILING_COMMAND)
    if result == 0:
        logger.success(l("t_compilation_is_finish"))
        return True
    else:
        logger.error(f'{l("command_end_with_code")}: {result}')
        return False



def save_settings(settings_data, config_comments=None):
    if config_comments is None:
        config_comments = {} # Если комментарии не переданы, используем пустой словарь

    try:
        with open("config.py", "w", encoding="utf-8") as config_file:
            for key, value in settings_data.items():
                # Записываем комментарий, если он есть
                comment = config_comments.get(key)
                if comment:
                    # Комментарии всегда должны начинаться с "# "
                    config_file.write(f"# {comment}\n")

                # Записываем саму переменную
                if isinstance(value, (list, dict, set)):
                    # Используем repr для точного строкового представления сложных объектов
                    config_file.write(f"{key} = {repr(value)}\n")
                else:
                    # Используем repr для точного строкового представления всех остальных типов
                    config_file.write(f"{key} = {repr(value)}\n")

                # Добавляем пустую строку для лучшей читаемости
                config_file.write("\n")

        logger.success(f'SAU - {l("setting_saved_in")} config.py')
        return True
    except Exception as e:
        logger.exception(f'SAU - {l("settings_save_error")}')
        messagebox.showerror(RS(), l("settings_save_error"))
        return False



# Резервное копирование настроек
def backup_settings(export=False):
    try:
        global SETTINGS_BACKUP_PREFIX
        backup_filename = f"{SETTINGS_BACKUP_PREFIX}{datetime.now().strftime('%d%m%Y_%H%M%S')}.py"
        backup_filepath = os.path.join(os.path.expanduser("~"), "Desktop", backup_filename)

        shutil.copy("config.py", backup_filepath)

        logger.info(f'SAU - {l("settings_backup_created_ob_path")}: {backup_filepath}')

        if export:
            messagebox.showinfo(RS(), f'{l("settings_export_success")} {backup_filepath}')

        return backup_filepath
    except Exception as e:
        logger.exception(f'SAU - {l("settings_backup_created_error")}')
        messagebox.showerror(RS(), l("settings_backup_created_error"))
        if export:
            messagebox.showerror(RS(), f'{l("settings_export_error")}:\n{e}')
        return 0



# Распаковки архива
def extract_archive(ARCHIVE_PATH):
    try:
        if not os.path.exists(ARCHIVE_PATH):
            comment = f'SAU - {l("archive")} {ARCHIVE_PATH} {l("not_found")}.\n{l("not_compilation")}.'
            logger.error(comment)
            messagebox.showerror(RS(), comment)
            return False

        with zipfile.ZipFile(ARCHIVE_PATH, "r") as zip_ref:
            zip_ref.extractall("", pwd=ARCHIVE_PASSWORD)
        logger.info(f'SAU - {l("archive")} {ARCHIVE_PATH} {l("success_unpacked")}')
        return True
    except zipfile.BadZipFile:
        logger.error(f'SAU - {l("bad_archive")}')
        messagebox.showerror(RS(), l("bad_archive"))
        return False
    except Exception as e:
        logger.exception(f'SAU - {l("unpacked_archive_error")}')
        messagebox.showerror(RS(), l("unpacked_archive_error"))
        return False



def move_all_files(src_folder, dest_folder):
    # Перемещает все содержимое указанной папки в другую папку
    try:
        for item in os.listdir(src_folder):
            src_path = os.path.join(src_folder, item)
            dest_path = os.path.join(dest_folder, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.move(src_path, dest_path)
        logger.info(f'SAU - {l("content")} {src_folder} {l("moved")} {l("in")} {dest_folder}.')
    except Exception as e:
        logger.exception(f'SAU - {l("moved_error")}')



def copy_files():
    new_image_path = simpledialog.askstring(title=RS(), prompt=l("enter_path_to_image"))

    copy = 1
    if not new_image_path or new_image_path == None:
        copy = 0

    try:
        if copy == 1:
            move_all_files("info_image\\", new_image_path)
    except PermissionError:
        comment = f'{l("permission_error")} {l("for_copy_image")} - {new_image_path}'
        logger.warning(f"SAU - {comment}", e)
        messagebox.warning(RS(), f"{comment}\n{e}")
    except FileNotFoundError:
        messagebox.warning(RS(), f'{l("file_not_found")} {l("for_copy_file")}')
    except Exception as e:
        comment = f'SAU - {l("copy_error")} {l("copy_file_error")}'
        logger.exception(comment)
        messagebox.error(RS(), comment)
        return False

    global path_to_copy
    path_to_copy = simpledialog.askstring(title=RS(), prompt=l("enter_exe_name"))

    if not path_to_copy or path_to_copy == None:
        return False

    try:
        shutil.copy(f"{PROGRAM_NAME}.exe", path_to_copy)
    except PermissionError:
        comment = f'SAU - {l("permission_error")} {l("file_not_found")} {l("for_copy")} {PROGRAM_NAME}.exe'
        logger.error(comment, e)
        messagebox.showwarning(RS(), comment)
        return False
    except FileNotFoundError:
        comment = f'SAU - {l("file_not_found")} {PROGRAM_NAME}.exe'
        logger.error(comment, e)
        messagebox.showwarning(RS(), comment)
        return False
    except Exception as e:
        logger.exception(f'SAU - {l("copy_error")}')
        messagebox.showerror(RS(), f'{l("copy_error")} {PROGRAM_NAME}.exe\n{l("copy_exe_error")}.')
        return False

    return True


# Создаём Ярлык
def create_lnk(target_path, shortcut_name):
    try:
        # Получаем путь к рабочему столу
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        shortcut_path = os.path.join(desktop_path, f"{shortcut_name}.lnk")

        # Создаем объект Shell
        shell = win32com.client.Dispatch("WScript.Shell")

        # Создаем ярлык
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path) # Рабочий каталог ярлыка
        shortcut.save() # Сохраняем ярлык

        logger.info(f'SAU - {l("create_lnk_success")}.')
    except Exception as e:
        logger.exception(f'SAU - {l("create_lnk_error")}')



# Добавляем программу в автозапуск
def add_to_autorun(target_path):
    try:
        # Открываем ключ реестра для редактирования
        registry_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\", 0, reg.KEY_WRITE)

        # Заменяем значение
        reg.SetValueEx(registry_key, "Userinit", 0, reg.REG_SZ, f"C:\\Windows\\System32\\userinit.exe, {target_path}")

        # Закрываем ключ реестра
        reg.CloseKey(registry_key)
        logger.info(f'{l("meaning")} Userinit {l("successfully_changed_to")} C:\\Windows\\System32\\userinit.exe, {target_path}')

        return True
    except Exception as e:
        logger.exception(f'SAU - {l("add_to_autorun_error")}')
        return False



# Подготовка к перекомпиляции
def preparing_for_recompilation(settings_data, config_comments):
    backup_filepath = backup_settings()
    if not backup_filepath:
        return False

    if not save_settings(settings_data, config_comments):
        return False

    if not extract_archive(ARCHIVE_PATH):
        return False

    try:
        if os.path.exists("T.py"):
            os.rename("T.py", f"{PROGRAM_NAME}.py")
            logger.info(f'SAU - T.py {l("renamed")} -> {PROGRAM_NAME}.py')
        else:
            logger.error(f'SAU - {l("file")} T.py {l("not_found")} {l("renamed")}.')
    except Exception as e:
        raise Exception(f'SAU - {l("error")} {l("when_renaming")} {l("file2")}:\n{e}')

    if not compiling_crowbar():
        return False

    if not copy_files():
        return False

    create_lnk(path_to_copy, RS())

    if messagebox.askyesno(RS(), l("add_program_to_autorun")):
        if not add_to_autorun(path_to_copy):
            messagebox.showerror(RS(), f'{l("add_program_to_autorun_error")}\n{e}')

    return True



# Проверка является ли путь строкой
def validate_path(path):
    if not isinstance(path, str):
        return False, l("path_must_string")
    return True, ""



# Проверка на превышение значения в переменной
def validate_int_with_limit(value, max_value):
    try:
        num = int(value)
        if 1 <= num <= max_value:
            return True, ""
        else:
            return False, f'{l("number_must_be_1_to")} {max_value}.'
    except ValueError:
        return False, l("enter_number")



# Проверка правильного синтаксиса списков
def validate_string_list(value):
    if not isinstance(value, str):
        return False, l("enter_string")

    s = value.strip()
    if not s:
        return False, l("field_cannot_be_empty")

    # Проверка базовых скобок
    if not ((s.startswith("[") and s.endswith("]")) or
            (s.startswith("(") and s.endswith(")")) or
            (s.startswith("{") and s.endswith("}"))):
        return False, f'{l("use")}: ["а"], ("а",), {1,2}, {"k":"v"}'

    try:
        # Пытаемся безопасно превратить строку в объект Python
        parsed = ast.literal_eval(s)

        # Проверяем, что результат — один из ожидаемых коллекций
        if isinstance(parsed, (list, tuple, set, dict)):
            return True, ""
        return False, l("must_list")

    except (SyntaxError, ValueError) as e:
        return False, f'{l("syntaxis_error")}: {e}'
    except Exception as e:
        return False, f'{l("invalid_format")}: {e}'



# Проверка на то что значение является строкой
def validate_string(value):
    if not isinstance(value, str):
        return False, l("enter_string")
    return True, ""



# Проверка на то что значение является словарём
def validate_dict_config(value):
    if not isinstance(value, dict):
        return False, l("must_be_dictionary")
    if "type" not in value:
        return False, f'{l("dictionary_must_contain_key")} "type"!'
    return True, ""



# Создание виджета для ввода данных
def create_input_widget(frame, variable_name, variable_type, default_value, row_num):
    label = ttk.Label(frame, text=variable_name)
    label.grid(row=row_num, column=0, padx=3, pady=1, sticky=tk.W)

    # Валидация будет использоваться только в Entry, но ее нужно определить
    validation_command = frame.register(lambda P, var_type=variable_type: validate_path(var_type))

    # row_increment - переменная для отслеживания, сколько строк занял виджет (обычно 1, но 2, если есть метка ошибки снизу)
    row_increment = 1

    # Инициализируем переменные, которые будут возвращены
    var = tk.StringVar(value=str(default_value) if variable_type in ("bool", "int") else default_value)
    widget = None
    column_span = 1 # По умолчанию 1, для str_path

    if variable_type == "bool":
        var.set(str(default_value))
        widget = ttk.Combobox(frame, textvariable=var, values=["True", "False"], state="readonly")
        column_span = 2

    elif variable_type == "int":
        var.set(str(default_value))
        widget = ttk.Entry(frame, textvariable=var, validate="key", validatecommand=(validation_command, "%P"))
        column_span = 2

    elif variable_type == "str_path":
        var.set(default_value)
        widget = ttk.Entry(frame, textvariable=var, validate="key", validatecommand=(validation_command, "%P"))

        def browse_path():
            path = filedialog.askdirectory()
            if path:
                var.set(path)

        # Кнопка "Обзор" занимает столбец 2
        browse_button = ttk.Button(frame, text=l("review"), command=browse_path)
        browse_button.grid(row=row_num, column=2, padx=3, pady=1)

    elif variable_type == "str_list":
        var.set(str(default_value))
        widget = ttk.Entry(frame, textvariable=var, validate="key", validatecommand=(validation_command, "%P"))
        column_span = 2

    elif variable_type == "dict":
        var.set(str(default_value))
        widget = ttk.Entry(frame, textvariable=var, validate="key", validatecommand=(validation_command, "%P"))
        column_span = 2

    else:
        var.set(default_value)
        widget = ttk.Entry(frame, textvariable=var, validate="key", validatecommand=(validation_command, "%P"))
        column_span = 2

    if widget:
        widget.grid(row=row_num, column=1, padx=3, pady=1, sticky=tk.EW, columnspan=column_span)

    # Создание метки ошибки
    error_label = ttk.Label(frame, text="", foreground="red")

    if column_span == 2:
        error_label.grid(row=row_num + 1, column=1, columnspan=2, padx=3, sticky=tk.W)
        row_increment = 2
    else:
        # Если поле ввода занимает только столбец 1 (т.е. есть кнопка "Обзор"), то метку ошибки размещаем в столбце 2 (на той же строке)
        error_label.grid(row=row_num, column=2, padx=3, pady=1, sticky=tk.W)
        row_increment = 1 # Виджет занял одну строку

    return var, widget, error_label, row_increment



# Чтение комментариев
def read_config(user_config=False):
    comments = {}
    current_comment = ""
    try:
        if user_config:
            config_path = filedialog.askopenfilename(title=RS(), filetypes=[("Python файлы", "*.py*")])
        else:
            # Пытаемся открыть файл config.py, находящийся в том же каталоге
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped_line = line.strip()

                # Если строка начинается с символа комментария, сохраняем ее
                if stripped_line.startswith("# "):
                    # Удаляем символ комментария и пробелы
                    current_comment = stripped_line[1:].strip()

                # Если строка содержит "="
                elif "=" in stripped_line and not stripped_line.startswith("# "):
                    # Извлекаем имя переменной до знака "="
                    var_name_match = re.match(r"^\s*([a-zA-Z_]\w*)\s*=", stripped_line)
                    if var_name_match:
                        var_name = var_name_match.group(1)
                        if current_comment:
                            comments[var_name] = current_comment
                        else:
                            # Если комментария нет, ставим пустую строку
                            comments[var_name] = ""
                        # Сбрасываем текущий комментарий после того, как он был использован
                        current_comment = ""
    except FileNotFoundError:
        logger.error(f'SAU - {l("file")} config.py')
    except Exception as e:
        logger.exception(f'SAU - {l("read_comments_error")} config.py')

    return comments



# Главное Окно
def crowbar_settings(current_theme):
    # Считываем комментарии из config.py
    config_comments = read_config()

    SAU_GUI = tk.Tk()
    SAU_GUI.title(RS())
    SAU_GUI.geometry("435x500")

    SAU_GUI.focus_set()

    apply_global_theme(SAU_GUI, current_theme)

    # Создание скроллбара
    main_frame = ttk.Frame(SAU_GUI)
    main_frame.pack(fill="both", expand=True, padx=5, pady=5)

    canvas = tk.Canvas(main_frame, bd=0, highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    # Используем bind_all для реакции на колесо мыши
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    frame = ttk.Frame(canvas)
    # Создаем внутреннее окно и сохраняем его ID
    canvas_window_id = canvas.create_window((0, 0), window=frame, anchor="nw")

    # Функция для привязки: она будет вызываться при изменении размера холста
    def on_canvas_configure(event):
        # Используем ID для установки ширины внутреннего фрейма равной ширине холста
        canvas.itemconfig(canvas_window_id, width=event.width)
        # Обновляем область прокрутки
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.bind("<Configure>", on_canvas_configure)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=5, pady=5)

    # Создаем вкладки
    general_tab = ttk.Frame(notebook)
    notebook.add(general_tab, text=f'{l("pac")} - {PROGRAM_AUTHENTICATION_CLYTH}')

    # Раздел для общих настроек
    general_frame = ttk.Frame(general_tab)
    general_frame.pack(padx=0, pady=0, fill="x")

    general_frame.grid_columnconfigure(0, weight=0)
    general_frame.grid_columnconfigure(1, weight=1)
    general_frame.grid_columnconfigure(2, weight=0)

    # Словарь для хранения виджетов
    widgets = {}

    # Функция для определения типа переменной
    def get_variable_type(var_name, var_value):
        type_mapping = {
            "str_path": ["settings_path", "log_path", "images_path"],
            "int": ["clyth", "ultimate_load_cpu", "ultimate_load_ram", "time_sleep_to_scan", 
                   "time_to_update_process_list", "time_to_close_window", "time_sleep_to_close_question", 
                   "time_sleep_to_close_question2"],
            "bool": ["message", "alert_sound", "reboot_os", "force_software", "animation_defolt"],
            "str_list": ["bad_process", "exception_process", "black_theme", "dark_theme", "white_theme", "red_theme", "gray_theme", "orange_theme", "lime_theme", "theme"],
        }

        # Проверяем если значение - это словарь с типом
        if isinstance(var_value, dict) and "type" in var_value:
            return var_value["type"], var_value.get("name", var_name)

        for var_type, var_list in type_mapping.items():
            if var_name in var_list:
                return var_type, var_name

        return "str", var_name

    # Создаем виджеты для каждой переменной из config.py
    row_counter = 0
    for var_name, var_value in config.__dict__.items():
        # Не пропускаем специальные переменные
        if var_name.startswith("__"):
            continue

        if var_name in globals() or var_name in locals():
            continue

        # Получаем тип и отображаемое имя переменной
        var_type, display_name = get_variable_type(var_name, var_value)

        # Извлекаем значение если переменная словарь
        actual_value = var_value.get("value", var_value) if isinstance(var_value, dict) and "value" in var_value else var_value

        # Добавляем метку с комментарием перед созданием виджета
        comment_text = config_comments.get(var_name, "")
        if comment_text:
            comment_label = ttk.Label(general_frame, text=comment_text, foreground="gray")
            comment_label.grid(row=row_counter, column=0, columnspan=3, padx=5, pady=(2, 0), sticky=tk.W)
            row_counter += 1

        var, widget, error_label, row_increment_step = create_input_widget(
            general_frame, display_name, var_type, actual_value, row_counter
        )
        widgets[var_name] = {
            "widget": widget,
            "var": var,
            "type": var_type,
            "error_label": error_label,
            "comment": comment_text,
        }
        # Увеличиваем счетчик на 1 или 2, в зависимости от того, есть ли метка ошибки снизу
        row_counter += row_increment_step

    # Удаляем объект
    def delete_item(path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                logger.info(f'SAU - {l("delete_dir")}: {path}')
            else:
                os.remove(path)
                logger.info(f"SAU - {file_delete}: {path}")

            return True
        except Exception as e:
            logger.exception(f'SAU - {l("delete_error")} {path}')
            messagebox.showerror(RS(), f'{l("delete_error")} {path}:\n{e}')



    # Сохранение настроек
    def apply_settings():
        settings_data = {}
        config_comments_to_save = {}
        valid = True

        for var_name, widget_data in widgets.items():
            value = widget_data["var"].get()
            var_type = widget_data["type"]
            error_label = widget_data["error_label"]
            error_label.config(text="") 
            config_comments_to_save[var_name] = widget_data["comment"]

            is_valid = True
            error_message = ""

            if not value and var_type != "bool":
                is_valid = False
                error_message = l("field_cannot_be_empty")
            
            elif var_type == "int":
                is_valid, error_message = validate_int_with_limit(value, 99)
                if is_valid:
                    settings_data[var_name] = int(value)
            
            elif var_type in ("str_list", "dict"): # Объединяем проверку коллекций
                is_valid, error_message = validate_string_list(value)
                if is_valid:
                    try:
                        # Если валидация прошла, сохраняем уже объект, а не строку
                        settings_data[var_name] = ast.literal_eval(value.strip())
                    except Exception as e:
                        is_valid = False
                        error_message = f'{l("parsing_error")}: {e}'
                        logger.exception(l("parsing_error"))

            elif var_type == "str_path":
                is_valid, error_message = validate_path(value)
                if is_valid:
                    settings_data[var_name] = value
            
            elif var_type == "bool":
                settings_data[var_name] = value == "True"
            
            else: # str
                is_valid, error_message = validate_string(value)
                if is_valid:
                    settings_data[var_name] = value

            if not is_valid:
                error_label.config(text=error_message)
                valid = False

        if not valid:
            messagebox.showerror(RS(), l("fix_problem_in_fields"))
            return

        if not messagebox.askyesno(RS(), l("recompilation_required_continue")):
            return

        # Блокируем интерфейс
        set_ui_state("disabled")

        def run_compilation():
            try:
                # Бэкап
                SAU_GUI.after(0, lambda: [compilation_label.config(text=l("create_backup")), progress_bar.config(value=10)])
                if not backup_settings(): raise Exception(l("create_backup_error"))

                # Сохранение настроек
                SAU_GUI.after(0, lambda: [compilation_label.config(text=l("save_settings")), progress_bar.config(value=25)])
                if not save_settings(settings_data, config_comments_to_save): raise Exception(l("save_settings_error"))

                # Распаковка исходного кода
                SAU_GUI.after(0, lambda: (compilation_label.config(text=l("unpacking_source_code")), progress_bar.config(value=40)))
                if not extract_archive(ARCHIVE_PATH): raise Exception(l("unpacking_source_code_error"))

                SAU_GUI.after(0, lambda: [compilation_label.config(text=l("preparing_files")), progress_bar.config(value=50)])
                if os.path.exists("T.py"):
                    if os.path.exists(f"{PROGRAM_NAME}.py"):
                        os.remove(f"{PROGRAM_NAME}.py")
                    os.rename("T.py", f"{PROGRAM_NAME}.py")
                    logger.info(f'SAU - {l("file")} {l("success")} {l("renamed")} {PROGRAM_NAME}.py')
                else:
                    # Если файла T.py нет, проверяем, вдруг он уже называется как нужно
                    if not os.path.exists(f"{PROGRAM_NAME}.py"):
                        raise Exception(f'{l("file")} T.py {l("not_found")} {l("in")} {l("archive")}!')

                # Компиляция
                SAU_GUI.after(0, lambda: [compilation_label.config(text=f'{l("compilation")} {l("in")} EXE...'), progress_bar.config(value=60)])
                if not compiling_crowbar(): raise Exception(f'{l("error")} {l("during_recompilation")}')
                # Копирование файлов
                SAU_GUI.after(0, lambda: [compilation_label.config(text=l("copying_files")), progress_bar.config(value=90)])

                def finalize():
                    if copy_files():
                        create_lnk(path_to_copy, RS())
                        progress_bar.config(value=100)
                        compilation_label.config(text=l("adding_to_autorun"))
                        if messagebox.askyesno(RS(), l("add_program_to_autorun")):
                            add_to_autorun(path_to_copy)
                        comment = f'{l("success")} {l("completed")}'
                        compilation_label.config(text=comment)
                        messagebox.showinfo(RS(), comment)
                    set_ui_state("normal")

                SAU_GUI.after(0, finalize)

            except Exception as e:
                messagebox.showerror(RS(), f'{l("error")} {l("during_recompilation")}:\n{e}')
                compilation_label.config(text=f'{l("error")} {l("during_recompilation")}')
                progress_bar.config(value=0)
                set_ui_state("normal")

        # Запуск потока
        threading.Thread(target=run_compilation, daemon=True).start()

    def delete_cache():
        if not messagebox.askyesno(RS(), l("delete_compiling_cache")):
            return

        global config_log_path
        # Файлы, которые нельзя удалять
        protected_names = [f'{PROGRAM_NAME}.exe", "config.py', config_log_path]
        
        # Расширения-исключения
        protected_extensions = (".txt", ".log", ".exe")

        current_dir = os.getcwd()
        deleted_count = 0

        try:
            for item in os.listdir(current_dir):
                if item.endswith(protected_extensions) or item in protected_names:
                    continue

                should_delete = False

                if item in ["dist", "build"] and os.path.isdir(item):
                    should_delete = True

                elif item.endswith(".py"):
                    should_delete = True

                elif item.endswith((".bin", ".pyd")):
                    should_delete = True

                if should_delete:
                    if delete_item(item): 
                        deleted_count += 1

            comment = f'{l("clean_completed_deleted_objects")}: {deleted_count}'
            logger.info(f"SAU - {comment}")
            messagebox.showinfo(RS(), comment)
        except Exception as e:
            logger.exception(f'SAU - {l("clean_cache_error")}')
            messagebox.showerror(RS(), l("clean_cache_error"))

    status_frame = ttk.Frame(frame)
    status_frame.pack(fill="x", side=tk.BOTTOM, pady=5)

    compilation_label = ttk.Label(status_frame, text=l("ready"))
    compilation_label.pack(side=tk.TOP, anchor="w", padx=5)

    progress_bar = ttk.Progressbar(status_frame, orient="horizontal", mode="determinate")
    progress_bar.pack(fill="x", padx=5, pady=2)
    progress_bar["value"] = 0

    # Список всех кнопок для быстрого управления доступом
    action_buttons = []

    # Переключает активность всех кнопок управления
    def set_ui_state(state="normal"):
        for btn in action_buttons:
            btn.config(state=state)

    def open_current_dir():
        try:
            os.startfile(os.getcwd())
        except Exception as e:
            logger.exception(f'{l("open_error")} {l("dir")}')

    def open_log_file():
        try:
            if os.path.exists(config_log_path):
                os.startfile(config_log_path)
            else:
                messagebox.showwarning(RS(), f'{l("not_found")} {l("log")}')
        except Exception as e:
            logger.exception(f'{l("open_error")} {l("log")}')

    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=5)

    export_button = ttk.Button(button_frame, text=l("export"), command=lambda:backup_settings(export=True))
    export_button.grid(row=0, column=0, padx=3, pady=2)
    
    import_button = ttk.Button(button_frame, text=l("import"), command=lambda:read_config(True))
    import_button.grid(row=0, column=1, padx=3, pady=2)

    delete_cache_button = ttk.Button(button_frame, text=l("delete_cache"), command=delete_cache)
    delete_cache_button.grid(row=0, column=2, padx=3, pady=2)

    apply_button = ttk.Button(button_frame, text=l("apply"), command=apply_settings)
    apply_button.grid(row=0, column=3, padx=3, pady=2)

    open_dir_button = ttk.Button(button_frame, text=f'{l("open")} {l("dir")}', command=open_current_dir)
    open_dir_button.grid(row=1, column=0, columnspan=2, padx=3, pady=2, sticky="ew")

    open_log_button = ttk.Button(button_frame, text=f'{l("open")} {l("log")}', command=open_log_file)
    open_log_button.grid(row=1, column=2, columnspan=2, padx=3, pady=2, sticky="ew")

    # Сохраняем ссылки для управления состоянием
    action_buttons.extend([
        export_button, import_button, delete_cache_button, 
        apply_button, open_dir_button, open_log_button
    ])

    # Обновляем геометрию, чтобы скроллбар работал корректно
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    SAU_GUI.mainloop()

def SAU(current_theme):
    if messagebox.askyesno(RS(), l("sau_start_text")):
        global PROGRAM_NAME, ARCHIVE_PASSWORD
        SETTINGS_BACKUP_PREFIX = "settings_backup"
        # ARCHIVE_PATH = "crowbar_code.zip"
        ARCHIVE_PASSWORD = b"0000"
        PROGRAM_NAME = simpledialog.askstring(title=RS(), prompt=l("enter_program_name"))
        if not os.path.isfile("icon\\T_icon.ico"):
            messagebox.showinfo(RS(), l("icon_not_found"))
            ICON_PATH = filedialog.askopenfilename(title=RS(), filetypes=[("Иконка программы", "*.ico*")])
            if ICON_PATH:
                COMPILING_COMMAND = f"python -m nuitka --follow-imports --standalone --windows-console-mode=disable --onefile --enable-plugin=tk-inter --windows-icon-from-ico={ICON_PATH} --lto=no --mingw64 {PROGRAM_NAME}.py"
            else:
                COMPILING_COMMAND = f"python -m nuitka --follow-imports --standalone --windows-console-mode=disable --onefile --enable-plugin=tk-inter --lto=no --mingw64 {PROGRAM_NAME}.py"
        else:
            COMPILING_COMMAND = f"python -m nuitka --follow-imports --standalone --windows-console-mode=disable --onefile --enable-plugin=tk-inter --windows-icon-from-ico=icon\\T_icon.ico --lto=no --mingw64 {PROGRAM_NAME}.py"

        global ARCHIVE_PATH
        ARCHIVE_PATH = filedialog.askopenfilename(title=RS(), filetypes=[("Zip Архивы", "*.zip*")])
        extract_archive(ARCHIVE_PATH)
        try:
            crowbar_settings(current_theme)
        except Exception as e:
            logger.exception(l("sau_critical_error"))
    else:
        return

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    from elevate import elevate
    elevate()
    config_log_path = simpledialog.askstring(title=RS(), prompt=l("enter_log_name"))
    if config_log_path:
        logger.add(config_log_path, format="{time} {level} {message}", rotation="10 MB", compression="zip")
    current_theme = THEME[DEFAULT_THEME]
    SAU(current_theme)
