#Данное Свободное Программное Обеспечение распространяется по лицензии GPL-2.0-only или GPL-2.0-or-later
#Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату (в случае её распространения), но вы обязаны выкладывать исходный код своей версии программы!
#ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ - ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v2.0 или более поздней версии.
#В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ - ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ.
#ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ - ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО ПРЕДОСТАВЛЯЕТ ЛИЦЕНЗИЯ GPL.
#Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
#Или в файле COPYING в архиве с установщиком программы
#Copyleft 🄯 NEO Organization Departament K 2024 - 2025
#Coded by @AnonimNEO (Telegram)

#Интерфейс
from tkinter import ttk, filedialog, messagebox, simpledialog
import tkinter as tk
#Дата и Время
from datetime import datetime
#Работа с реестром
import winreg as reg
#Работа с Файлами
import win32com.client
import shutil
import os
#Работа с Архивами
import zipfile
#Работа с выражениями
import ast
import re
#Логирование
from loguru import logger

#Чтение конфига
import config
#Запуск команд
from OF import run_command
#Случайные загаловки
from RS import random_string

settings_and_update_version = "1.0.6 Beta"

SETTINGS_BACKUP_PREFIX = "settings_backup"
ARCHIVE_PATH = "code_mount.zip"
ARCHIVE_PASSWORD = b"0000"
COMPILING_COMMAND = f"python -m nuitka --follow-imports --standalone --windows-console-mode=disable --onefile --enable-plugin=tk-inter --windows-icon-from-ico=icon\\T_icon.ico --lto=no T.py"
config_log_path = "Mount_Setup_Log.txt"

def compiling_mount():
    logger.info(f"Запуск Компиляции...\nЗапуск команды: {COMPILING_COMMAND}")
    if run_command(COMPILING_COMMAND) == 0:
        logger.info("Компиляция Компонента Trey завершена!")
        return True



def save_settings(settings_data, config_comments=None):
    if config_comments is None:
        config_comments = {} #Если комментарии не переданы, используем пустой словарь

    try:
        with open("config.py", "w", encoding="utf-8") as config_file:
            for key, value in settings_data.items():
                #Записываем комментарий, если он есть
                comment = config_comments.get(key)
                if comment:
                    #Комментарии всегда должны начинаться с "# "
                    config_file.write(f"# {comment}\n") 
                    
                #Записываем саму переменную
                if isinstance(value, (list, dict, set)):
                    #Используем repr для точного строкового представления сложных объектов
                    config_file.write(f"{key} = {repr(value)}\n")
                else:
                    #Используем repr для точного строкового представления всех остальных типов
                    config_file.write(f"{key} = {repr(value)}\n")

                #Добавляем пустую строку для лучшей читаемости
                config_file.write("\n") 

        logger.info("SAU - Настройки успешно сохранены в config.py")
        return True
    except Exception as e:
        comment = f"Ошибка при сохранении настроек:\n{e}"
        logger.error(f"SAU - {comment}")
        messagebox.showerror(random_string(), comment)
        return False



#Резервное копирование настроек
def backup_settings():
    try:
        backup_filename = f"{SETTINGS_BACKUP_PREFIX}{datetime.now().strftime("%d%m%Y_%H%M%S")}.py"
        backup_filepath = os.path.join(os.path.expanduser("~"), "Desktop", backup_filename)

        shutil.copy("config.py", backup_filepath)
#        with open(backup_filepath, "w") as backup_config:
#            for var_name, var_value in config.__dict__.items():
#                #Определяем тип переменной и создаем соответствующий виджет
#                if var_name in [
#                    "settings_path",
#                    "log_path",
#                    "images_path",
#                ]:
#                    var_type = "str_path"
#                elif var_name in ["clyth", "time_to_restart", "ultimate_load_cpu", "ultimate_load_ram"]:
#                    var_type = "int"
#                elif var_name in ["message", "alert_sound", "reboot_os", "force_software", "animation_defolt"]:
#                    var_type = "bool"
#                elif var_name in ["bad_process", "exceptions_proc"]:
#                    # Проверяем, является ли значение словарем.
#                    if isinstance(var_value, dict):
#                        var_type = "dict"
#                    else:
#                        var_type = "str_list"
#                else:
#                    var_type = "str"
#
#                #Определяем, является ли переменная критичной
#                critical = True if var_name in ["settings_path", "log_path", "images_path", "sound_alert_path", "clyth", "time_to_restart", "ultimate_load_cpu", "ultimate_load_ram", "message", "alert_sound", "reboot_os", "force_software", "bad_process", "exceptions_proc"] else False
#
#                #Форматирование значения для записи
#                if isinstance(var_value, bool):
#                    value_str = str(var_value)
#                elif isinstance(var_value, (int, float)):
#                    value_str = str(var_value)
#                elif isinstance(var_value, list):
#                    value_str = str(var_value)
#                else:
#                    value_str = str(var_value)
#
#                backup_config.write(f"{var_name}\n")
#                backup_config.write(f"Type: {var_type}\n")
#                backup_config.write(f"Value: {value_str}\n")
#                backup_config.write(f"Critical: {critical}\n")
#                backup_config.write("---\n") #Разделитель между переменными
        logger.info(f"SAU - Резервная копия настроек создана по пути: {backup_filepath}")
        return backup_filepath
    except Exception as e:
        comment = f"Ошибка при создании резервной копии:\n{e}"
        logger.error(f"SAU - {comment}")
        messagebox.showerror(random_string, comment)
        return 0



#Распаковки архива
def extract_archive():
    try:
        if not os.path.exists(ARCHIVE_PATH):
            comment = f"Архив {ARCHIVE_PATH} не найден.\nПерекомпиляция не возможна."
            logger.error(f"SAU - {comment}")
            messagebox.showerror(random_string, comment)
            return False

        with zipfile.ZipFile(ARCHIVE_PATH, "r") as zip_ref:
            zip_ref.extractall("", pwd=ARCHIVE_PASSWORD)
        logger.info(f"SAU - Архив {ARCHIVE_PATH} успешно распакован")
        return True
    except zipfile.BadZipFile:
        comment = f"Неверный формат архива или поврежденный архив."
        logger.error(f"SAU - {comment}")
        messagebox.showerror(random_string, comment)
        return False
    except Exception as e:
        comment = f"Ошибка при распаковке архива: {e}"
        logger.error(f"SAU - {comment}")
        messagebox.showerror(random_string, comment)
        return False



def move_all_files(src_folder, dest_folder):
    #Перемещает все содержимое указанной папки в другую папку
    try:
        for item in os.listdir(src_folder):
            src_path = os.path.join(src_folder, item)
            dest_path = os.path.join(dest_folder, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.move(src_path, dest_path)
        print(f"Содержимое {src_folder} перемещено в {dest_folder}.")
    except Exception as e:
        print(f"Ошибка при перемещении файлов: {e}")



def copy_files():
    new_image_path = simpledialog.askstring(title=random_string(), prompt="Введите каталог куда переместить изображения\nНичего не вводите если изображения уже в нужном каталоге\n(например вы просто обновляете программу)")

    copy = 1
    if not new_image_path or new_image_path == None:
        copy = 0

    try:
        if copy == 1:
            move_all_files("info_image\\", new_image_path)
    except PermissionError:
        messagebox.warning(random_string(), f"Недостаточно прав для копирования изображений\nв каталог - {new_image_path}")
    except FileNotFoundError:
        messagebox.warning(random_string(), "Ненайдены файлы для копирования")
    except Exception as e:
        messagebox.error(random_string(), "Ошибка при копировании изображений\nВозможно вы ввели неправильные данные, вы можете сами перместить файлы они находятся в каталоге с программой.")
        return False

    global path_to_copy
    path_to_copy = simpledialog.askstring(title=random_string(), prompt="Введите каталог куда переместить исполняемый файл\nвместе с именем файла, обязательно с расширением .exe!")

    if not path_to_copy or path_to_copy == None:
        return False

    try:
        shutil.copy("T.exe", path_to_copy)
    except PermissionError:
        messagebox.showwarning(random_string(), f"Недостаточно прав для копирования файла T.exe")
        return False
    except FileNotFoundError:
        messagebox.showwarning(random_string(), f"Ненайден файл T.exe для копирования")
        return False
    except Exception as e:
        messagebox.showerror(random_string(), f"Ошибка при копировании T.exe\nВозможно вы ввели неправильные данные, вы можете сами перместить файлы они находятся в каталоге с программой.")
        return False

    return True


#Создаём Ярлык
def create_lnk(target_path, shortcut_name):
    try:
        #Получаем путь к рабочему столу
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        shortcut_path = os.path.join(desktop_path, f"{shortcut_name}.lnk")

        #Создаем объект Shell
        shell = win32com.client.Dispatch("WScript.Shell")

        #Создаем ярлык
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path) #Рабочий каталог ярлыка
        shortcut.save() #Сохраняем ярлык

        logger.info(f"SAU - Ярлык успешно создан на рабочем столе.")
    except Exception:
        pass



#Добавляем программу в автозапуск
def add_to_autorun(target_path):
    try:
        #Открываем ключ реестра для редактирования
        registry_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\", 0, reg.KEY_WRITE)

        #Заменяем значение
        reg.SetValueEx(registry_key, "Userinit", 0, reg.REG_SZ, f"C:\\Windows\\System32\\userinit.exe, {target_path}")

        #Закрываем ключ реестра
        reg.CloseKey(registry_key)
        logger.info(f"Значение Userinit успешно изменено на C:\\Windows\\System32\\userinit.exe, {target_path}")

        return True
    except Exception as e:
        logger.error(f"SAU - Ошибка при добавлении программы в автозагрузку:{e}")
        return False



#Подготовка к перекомпиляции
def preparing_for_recompilation(settings_data):
    backup_filepath = backup_settings()
    if not backup_filepath:
        return False

    if not save_settings(settings_data):
        return False

    if not extract_archive():
        return False

    if not compiling_mount():
        return False

    if not copy_files():
        return False

    create_lnk(path_to_copy, random_string())

    if messagebox.askyesno(random_string(), "Добавить программу в автозагрузку?"):
        if not add_to_autorun(path_to_copy):
            messagebox.showerror(random_string(), f"Произошла ошибка во время добавления программы в автозагрузку.")

    return True



#Проверка является ли путь строкой
def validate_path(path):
    if not isinstance(path, str):
        return False, "Путь должен быть строкой."
    return True, ""



#Проверка на превышение значения в перменной
def validate_int_with_limit(value, max_value):
    try:
        num = int(value)
        if 1 <= num <= max_value:
            return True, ""
        else:
            return False, f"Число должно быть от 1 до {max_value}."
    except ValueError:
        return False, "Введите число!"



#Проверка является строка списком
def validate_string_list(value):
    list_varning = 'Пожалуйста введите список целиком, в формате: ["значение1", "значение2", и т.д"]'
    if not isinstance(value, str):
        return False, "Значение должно быть строкой!"
    #Разрешаем импорт как списков, так и словарей
    if not (value.startswith("[") and value.endswith("]")) and not (value.startswith("{") and value.endswith("}")):
        return False, list_varning
    try:
        ast.literal_eval(value)
        return True, ""
    except (SyntaxError, ValueError):
        return False, list_varning



#Проверка на то что значение является строкой
def validate_string(value):
    if not isinstance(value, str):
        return False, "Значение должно быть строкой!"
    return True, ""



#Создание виджета для ввода даных
def create_input_widget(frame, variable_name, variable_type, default_value, row_num):
    label = ttk.Label(frame, text=variable_name)
    label.grid(row=row_num, column=0, padx=3, pady=1, sticky=tk.W)

    #Валидация будет использоваться только в Entry, но ее нужно определить
    validation_command = frame.register(lambda P, var_type=variable_type: validate_path(var_type))
    
    #row_increment - переменная для отслеживания, сколько строк занял виджет (обычно 1, но 2, если есть метка ошибки снизу)
    row_increment = 1

    #Инициализируем переменные, которые будут возвращены
    var = tk.StringVar(value=str(default_value) if variable_type == "bool" or variable_type == "int" else default_value)
    widget = None
    column_span = 1 #По умолчанию 1, для str_path

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

        #Кнопка "Обзор" занимает столбец 2
        browse_button = ttk.Button(frame, text="Обзор", command=browse_path)
        browse_button.grid(row=row_num, column=2, padx=3, pady=1)
        #В этом случае поле ввода займет только столбец 1, оставляя место для кнопки в столбце 2.

    elif variable_type == "str_list":
        var.set(str(default_value))
        widget = ttk.Entry(frame, textvariable=var, validate="key", validatecommand=(validation_command, "%P"))
        column_span = 2

    else:
        var.set(default_value)
        widget = ttk.Entry(frame, textvariable=var, validate="key", validatecommand=(validation_command, "%P"))
        column_span = 2

    if widget:
        widget.grid(row=row_num, column=1, padx=3, pady=1, sticky=tk.EW, columnspan=column_span)

    #Создание метки ошибки
    error_label = ttk.Label(frame, text="", foreground="red")

    if column_span == 2:
        error_label.grid(row=row_num + 1, column=1, columnspan=2, padx=3, sticky=tk.W)
        row_increment = 2
    else:
        #Если поле ввода занимает только столбец 1 (т.е. есть кнопка "Обзор"), то метку ошибки размещаем в столбце 2 (на той же строке)
        error_label.grid(row=row_num, column=2, padx=3, pady=1, sticky=tk.W)
        row_increment = 1 #Виджет занял одну строку

    return var, widget, error_label, row_increment



#Чтение комментариев
def read_config_comments():
    comments = {}
    current_comment = ""
    try:
        #Пытаемся открыть файл config.py, находящийся в том же каталоге
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")
        with open("config.py", "r", encoding="utf-8") as f:
            for line in f:
                stripped_line = line.strip()

                #Если строка начинается с символа комментария, сохраняем ее
                if stripped_line.startswith("#"):
                    #Удаляем символ комментария и пробелы
                    current_comment = stripped_line[1:].strip()

                #Если строка похожа на объявление переменной (например, содержит "=")
                elif "=" in stripped_line and not stripped_line.startswith("#"):
                    #Извлекаем имя переменной до знака "="
                    var_name_match = re.match(r"^\s*([a-zA-Z_]\w*)\s*=", stripped_line)
                    if var_name_match:
                        var_name = var_name_match.group(1)
                        if current_comment:
                            comments[var_name] = current_comment
                        else:
                            #Если комментария нет, ставим пустую строку
                            comments[var_name] = ""
                        #Сбрасываем текущий комментарий после того, как он был использован
                        current_comment = ""
    except FileNotFoundError:
        logger.error("SAU - Файл config.py не найден для чтения комментариев.")
    except Exception as e:
        logger.error(f"SAU - Ошибка при чтении комментариев из config.py:\n{e}")

    return comments



#Главное Окно
def settings_mount():
    #Считываем комментарии из config.py
    config_comments = read_config_comments()

    window = tk.Tk()
    window.title(random_string())
    window.geometry("435x500")

    #Создание скроллбара
    main_frame = ttk.Frame(window)
    main_frame.pack(fill="both", expand=True, padx=5, pady=5)

    canvas = tk.Canvas(main_frame, bd=0, highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill="both", expand=True)

    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    #Используем bind_all для реакции на колесо мыши
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    frame = ttk.Frame(canvas)
    #Создаем внутреннее окно и сохраняем его ID
    canvas_window_id = canvas.create_window((0, 0), window=frame, anchor="nw")

    #Функция для привязки: она будет вызываться при изменении размера холста
    def on_canvas_configure(event):
        #Используем ID для установки ширины внутреннего фрейма равной ширине холста
        canvas.itemconfig(canvas_window_id, width=event.width)
        #Обновляем область прокрутки
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.bind("<Configure>", on_canvas_configure)

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=5, pady=5)

    #Создаем вкладки
    general_tab = ttk.Frame(notebook)
    notebook.add(general_tab, text=f"SettingsAndUpdate - {settings_and_update_version}")

    #Раздел для общих настроек
    general_frame = ttk.Frame(general_tab)
    general_frame.pack(padx=0, pady=0, fill="x")

    general_frame.grid_columnconfigure(0, weight=0)
    general_frame.grid_columnconfigure(1, weight=1)
    general_frame.grid_columnconfigure(2, weight=0)

    #Словарь для хранения виджетов
    widgets = {}

    #Создаем виджеты для каждой переменной из config.py
    row_counter = 0
    for var_name, var_value in config.__dict__.items():
        #Не пропускаем специальные переменные
        if var_name.startswith("__"):
            continue

        if var_name in globals() or var_name in locals():
            continue

        #Добавляем метку с комментарием перед созданием виджета
        comment_text = config_comments.get(var_name, "")
        if comment_text:
            comment_label = ttk.Label(general_frame, text=comment_text, foreground="gray")
            comment_label.grid(row=row_counter, column=0, columnspan=3, padx=5, pady=(2, 0), sticky=tk.W)
            row_counter += 1

        #Определяем тип переменной и создаем соответствующий виджет
        if var_name in [
            "settings_path",
            "log_path",
            "images_path",
        ]:
            var_type = "str_path"
        elif var_name in ["clyth", "ultimate_load_cpu", "ultimate_load_ram", "time_sleep_to_scan", "time_to_update_process_list", "time_to_close_window", "time_sleep_to_close_question", "time_sleep_to_close_question2", ]:
            var_type = "int"
        elif var_name in ["message", "alert_sound", "reboot_os", "force_software", "animation_defolt"]:
            var_type = "bool"
        elif var_name in ["bad_process", "exception_process"]:
            var_type = "str_list"
        else:
            var_type = "str"

        var, widget, error_label, row_increment_step = create_input_widget(general_frame, var_name, var_type, var_value, row_counter)
        widgets[var_name] = {
            "widget": widget,
            "var": var,
            "type": var_type,
            "error_label": error_label,
            "comment": comment_text,
        }
        #Увеличиваем счетчик на 1 или 2, в зависимости от того, есть ли метка ошибки снизу
        row_counter += row_increment_step



    #Экспорт настроек
    def export_settings():
        filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title=random_string(),
        )
        if not filepath:
            return

        try:
            with open(filepath, "w") as f:
                for var_name, widget_data in widgets.items():
                    value = widget_data["var"].get()
                    data_type = widget_data["type"]
                    critical = "True" if var_name in ["settings_path", "log_path", "images_path", "sound_alert_path", "cursor_path", "clyth", "time_to_restart", "ultimate_load_cpu", "ultimate_load_ram", "message", "alert_sound", "reboot_os", "force_software", "animation_defolt", "bad_process", "exceptions_proc"] else "False"
                    comment = widget_data.get("comment", "") #Получаем комментарий

                    #Записываем комментарий в файл экспорта
                    if comment:
                        f.write(f"#Comment: {comment}\n")

                    f.write(f"{var_name}\n")
                    f.write(f"Type: {data_type}\n")
                    f.write(f"Value: {value}\n")
                    f.write(f"Critical: {critical}\n")
                    f.write("---\n") #Разделитель между переменными
            comment = f"Настройки экспортированы в: {filepath}"
            logger.info(f"SAU - {comment}")
            messagebox.showinfo(random_string, comment)
        except Exception as e:
            comment = f"Ошибка при экспорте настроек: {e}"
            logger.error(f"SAU - {comment}")
            messagebox.showerror(random_string, comment)



    #Импорт настроек
    def import_settings():
        filepath = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt")],
        title=random_string(),
        )

        if not filepath:
            return

        try:
            with open(filepath, "r") as f:
                lines = f.readlines()
                imported_settings = {}
                i = 0
                error_var = 0
                problem_var = [] #Используем список для сбора проблемных переменных
                while i < len(lines):
                    try:
                        line = lines[i].strip()
                        if not line or line.startswith("---"):
                            i += 1
                            continue

                        #Читаем комментарий, если он есть
                        imported_comment = ""
                        if line.startswith("#Comment:"):
                            imported_comment = line.replace("#Comment: ", "")
                            i += 1
                            var_name = lines[i].strip()
                        else:
                            var_name = line

                        if not var_name: #Если переменная пустая после чтения комментария
                            i += 1
                            continue

                        data_type_line = lines[i+1].strip()
                        value_line = lines[i+2].strip()
                        critical_line = lines[i+3].strip()

                        data_type = data_type_line.replace("Type: ", "")
                        value = value_line.replace("Value: ", "")
                        critical = critical_line.replace("Critical: ", "").lower() == "true"

                        #Сохраняем импортированный комментарий
                        imported_settings[var_name] = (data_type, value, critical, imported_comment) 
                        i += 4
                        if i < len(lines) and lines[i].strip() == "---":
                            i += 1
                    except IndexError:
                        filed_str = f"Пропущена некорректно отформатированная строка при импорте, начиная с: {lines[i].strip()}"
                        logger.error(f"SAU - {filed_str}")
                        #Предупреждение о синтаксической ошибке
                        if messagebox.askyesno(random_string(), f"!ВНИМАНИЕ!\nНе удалось импортировать настройки, обнаружена синтаксическая ошибка в файле\nВозможно файл предназначен для другой версии программы, повреждён или вы выбрали не тот файл при импорте.\n\nПродолжить импорт (могут быть пропущены настройки)?"):
                            i += 1
                            continue
                        else:
                            return #Отмена импорта

                #Обновляем виджеты
                for var_name, widget_data in widgets.items():
                    if var_name in imported_settings:
                        #Распаковываем импортированный комментарий
                        data_type, value, _, imported_comment = imported_settings[var_name] 

                        if data_type == "bool":
                            widget_data["var"].set(value)
                        elif data_type == "int":
                            widget_data["var"].set(value)
                        #elif data_type == "str_list":
                        #.. логика парсинга списка, если она нужна при импорте ...
                        else:
                            widget_data["var"].set(value)

                        #Обновляем сохраненный комментарий в словаре widgets
                        widget_data["comment"] = imported_comment

                        #Сбрасываем ошибку при импорте
                        widget_data["error_label"].config(text="")
                    else:
                        logger.error(f"Переменная {var_name} не найдена в файле импорта.")
                        problem_var.append(var_name) #Добавляем в список
                        error_var = 1

                if error_var == 1:
                    #Показываем сообщение с отсутствующими переменными
                    messagebox.showerror(random_string(), f"!ВНИМАНИЕ!\nВ файле для импорта не найдены следующие переменные:\n{', '.join(problem_var)}\nВидимо файл импорта который вы выбрали рассчитан для более раней версии программы.\nЕсли вы просто обновляете программу проигнорируйте это сообщение и заполните путсые переменные.")
                else:
                    messagebox.showinfo(random_string(), "Настройки успешно импортированы.")

        except Exception as e:
            comment = f"Ошибка при импорте настроек:\n{e}"
            logger.critical(f"SAU - {comment}")
            messagebox.showerror(random_string(), comment)



    #Сохранение настроек
    def apply_settings():
        settings_data = {}
        config_comments_to_save = {}
        valid = True
        need_compilation = False

        for var_name, widget_data in widgets.items():
            value = widget_data["var"].get()
            var_type = widget_data["type"]
            error_label = widget_data["error_label"]
            error_label.config(text="") #Сбрасываем предыдущие ошибки
            config_comments_to_save[var_name] = widget_data["comment"]

            if not value and var_type != "bool":
                is_valid = False
                error_message = "Поле не может быть пустым!"
            elif var_type == "int":
                is_valid, error_message = validate_int_with_limit(value, 99)
            elif var_type == "str_path":
                is_valid, error_message = validate_path(value)
            elif var_type == "str_list":
                is_valid, error_message = validate_string_list(value)
                if is_valid:
                    try:
                        settings_data[var_name] = ast.literal_eval(value)
                    except (SyntaxError, ValueError):
                        is_valid = False
                        error_message = 'Некорректный формат списка/словаря: ["значение1", "значение2", и т.д"] или {"ключ": "значение"}'

            else:
                is_valid, error_message = validate_string(value)

            if not is_valid:
                error_label.config(text=error_message)
                widget_data["widget"].config(foreground="red")
                valid = False
            else:
                widget_data["widget"].config(foreground="black")

            #Сохраняем значения только если они валидны
            if is_valid:
                if var_type == "bool":
                    settings_data[var_name] = value == "True"
                elif var_type == "int":
                    settings_data[var_name] = int(value)
                elif var_type == "str_list":
                    #Сохраняем строковое представление
                    settings_data[var_name] = value 
                else:
                    settings_data[var_name] = value

        if not valid:
            messagebox.showerror(random_string(), "Исправьте ошибки ввода!")
            return

        #Проверка на необходимость перекомпиляции
        #for var_name, widget_data in widgets.items():
        #    #Проверяем только критичные переменные, которые требуют перекомпиляции
        #    if var_name in ["settings_path", "log_path", "images_path", "clyth", "time_to_restart", "ultimate_load_cpu", "ultimate_load_ram", "reboot_os", "force_software", "animation_default", "bad_process", "exceptions_process"]:
        #        # Получаем текущее значение из модуля config
        #        current_config_value = config.__dict__.get(var_name)
        #        # Получаем новое значение из виджетов (после преобразования типа, если это не str_list)
        #        new_value = settings_data.get(var_name)

        #        # Для str_list новое значение - это строка (например '["val1", "val2"]'), а старое - может быть списком.
        #        # Поэтому преобразуем оба в одинаковый строковый формат для сравнения.
        #        if var_name in ["bad_process", "exceptions_proc"]:
        #            current_config_str = str(current_config_value)
        #            # Новое значение (new_value) уже является строкой из Entry-поля
        #            new_value_str = new_value
                    
        #            # Иногда ast.literal_eval возвращает разные строковые представления (например, для словарей),
        #            # поэтому более надежно сравнить строковое представление того, что будет записано:
        #            # Приводим оба значения к одинаковому строковому представлению (которое будет записано в config.py)
        #            try:
        #                # Старое значение (из config) -> строковое представление (как если бы оно было только что записано)
        #                old_repr = repr(current_config_value)
        #                # Новое значение (из Entry) -> строковое представление (уже готово)
        #                new_repr = new_value
                        
        #                if old_repr != new_repr:
        #                     need_compilation = True
        #                     break
        #            except Exception as e:
        #                logger.error(f"Ошибка сравнения для {var_name}: {e}")
        #                need_compilation = True

        #        # Для всех остальных типов сравниваем напрямую
        #        else:
        #            if current_config_value != new_value:
        #                need_compilation = True
        #                break

        need_compilation = True

        if need_compilation:
            if messagebox.askyesno(random_string(), "Требуется перекомпиляция!\nСделать резервную копию настроек и перекомпилировать?\nПеред этим закройте все компоненты программы."):
                if preparing_for_recompilation(settings_data):
                    messagebox.showinfo(random_string(), "Установка завершена!\nВы можете начать пользоваться программой\nМы будем крайне благодарны если вы не только оставите отзыв, комментарий, или отправите нам лог-файлы программы ради её улучшения!\nУдачи в использовании!")
                else:
                    messagebox.showerror(random_string(), f"Ошибка при перекомпиляции. Старые бинарники остались без изменений.\nДля более подробной информации попробуйте проверить лог файл {config_log_path}, в каталоге программы.")
        else:
            #Если перекомпиляция не нужна, просто сохраняем настройки
            if save_settings(settings_data, config_comments_to_save):
                messagebox.showinfo(random_string(), "Настройки успешно сохранены.")



    #Кнопки
    button_frame = ttk.Frame(frame) 
    button_frame.pack(pady=5)

    export_button = ttk.Button(button_frame, text="Экспорт", command=export_settings)
    export_button.grid(row=0, column=0, padx=3)

    import_button = ttk.Button(button_frame, text="Импорт", command=import_settings)
    import_button.grid(row=0, column=1, padx=3)

    apply_button = ttk.Button(button_frame, text="Применить", command=apply_settings)
    apply_button.grid(row=0, column=2, padx=3)
    
    #Обновляем геометрию, чтобы скроллбар работал корректно
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    window.mainloop()

def SAU():
    extract_archive()
    try:
        settings_mount()
    except Exception as e:
        logger.critical(f"Во время установки произошла неизвестная ошибка:\n{e}")

if __name__ == "__main__":
    logger.add(config_log_path, format="{time} {level} {message}", rotation="10 MB", compression="zip")
    SAU()
