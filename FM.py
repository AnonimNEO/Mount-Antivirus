#Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
#Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
#ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
#В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
#ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
#Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
#Или в файле COPYING.txt в архиве с установщиком
#Copyleft 🄯 NEO Organization, Departament K 2024 - 2025
#Coded by @AnonimNEO (Telegram)

#Интерфейс
from tkinter import ttk, messagebox, Menu, simpledialog
import tkinter as tk
#Дата и Время
from datetime import datetime
#Логирование
from loguru import logger
#Получение имени пользователя
import getpass
#Получение свойств файла
import win32api
import win32con
#Для поиска
import fnmatch
#Для получения списка дисков
import string
#Работа с файлами
import os.path
import shutil
import os

from OF import get_current_disc
from RS import random_string
from config import *

#Глобальная переменная версии
file_manager_version = "4.8.2 Beta"

def FM(run_in_recovery):
    try:
        #Получаем Имени текущего пользователя
        def get_user_name():
            try:
                user_name = getpass.getuser()
                return user_name
            except Exception as e:
                logger.error(f"FM - Ошибка получения имени пользователя!\n{e}")
                return default_user_name



        #Получение информации о файлах и каталогах
        def get_files_info(path):
            files_info = []

            #Добавляем ".." для подъема вверх, если это не корневой каталог
            parent_dir = os.path.dirname(path)
            if path.rstrip("\\/") != parent_dir.rstrip("\\/"): #Проверка, что мы не в корневом каталоге
                try:
                    stat = os.stat(parent_dir)
                    files_info.append({
                        "name": "..",
                        "path": parent_dir,
                        "size": 0,
                        "edited": stat.st_mtime,
                        "created": stat.st_ctime,
                        "type": "Папка",
                        "is_dir": True,
                        "ext": ""
                    })
                except Exception as e:
                    logger.warning(f"FM - Ошибка при получении информации о файле:\n{e}")

            #Получаем список файлов/каталогов
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    stat = os.stat(item_path)
                    is_dir = os.path.isdir(item_path)

                    #Определение типа
                    if is_dir:
                        file_type = "Каталог"
                        ext = ""
                    else:
                        ext = os.path.splitext(item)[1].lower()
                        if ext:
                            file_type = f"{ext.upper()[1:]} Файл"
                        else:
                            file_type = "Файл"

                    files_info.append({
                        "name": item,
                        "path": item_path,
                        "size": stat.st_size if not is_dir else 0,
                        "edited": stat.st_mtime,
                        "created": stat.st_ctime,
                        "type": file_type,
                        "is_dir": is_dir,
                        "ext": ext
                    })
                except (PermissionError, FileNotFoundError) as e:
                    #Пропускаем файлы, к которым нет доступа
                    logger.warning(f"FM - Пропущен файл: {item_path}\n{e}")
                    continue

            return files_info



        #Получаем доступные диски
        def get_available_drives():
            drives = []
            for drive in string.ascii_uppercase:
                if os.path.exists(drive + ":\\"):
                    drives.append(drive + ":\\")
            return drives



        #Переводим веса файла в более крупный формат
        def get_formatted_size(size):
            if not isinstance(size, (int, float)):
                return "Н/Д"

            if size == 0:
                return "" #Не показываем 0 для каталогов

            units = ["Байт", "КБ", "МБ", "ГБ", "ТБ"]
            unit_index = 0
            while size >= 1024 and unit_index < len(units) - 1:
                size /= 1024.0
                unit_index += 1
            return f"{size:.2f} {units[unit_index]}"



        #Форматируем Unix-таймштамп в читаемую строку
        def format_time(timestamp):
            if timestamp == 0:
                return ""
            try:
                return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")
            except Exception:
                return "Н/Д"



        class FileManagerApp:
            def __init__(self, FM):
                self.FM = FM
                self.FM.title(random_string())
                self.FM.geometry("700x400")

                self.user_name = get_user_name()

                self.key_actions = {
                    "Return": "handle_key_enter", #Enter - Открыть файл или каталог
                    "BackSpace": "on_back", #Backspace - Переход на уровень вверх
                    "Delete": "handle_key_delete", #Delete - Удалить выбранный элемент
                    "F5": "on_refresh", #F5 - Обновить
                    "F2": "handle_key_rename" #F2 - Переименовать
                }

                #Буфер обмена для Копирования/Вырезания
                self.clipboard_data = {"path": None, "action": None}

                #Словарь для хранения состояния каждой вкладки
                self.tabs_data = {}

                #Словарь для хранения состояния каждой вкладки
                self.tabs_data = {}

                #Создание верхней панели
                self.toolbar_frame = ttk.Frame(FM)
                self.toolbar_frame.pack(side="top", fill="x", padx=5, pady=(5, 0))

                self.create_toolbar_buttons()
                self.create_path_entry()

                #Создание Панели вкладок
                self.notebook = ttk.Notebook(FM)
                self.notebook.pack(side="top", fill="both", expand=True, padx=5, pady=5)
                self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

                #Создание Меню
                self.create_menu()

                #Добавление первой вкладки
                #При запуске предложить выбрать путь
                self.add_tab(path=None)

                #Фокусировка на окно
                self.FM.after(1, self.FM.focus_force)



            #Создает кнопок навигации
            def create_toolbar_buttons(self):
                button_frame = ttk.Frame(self.toolbar_frame)
                button_frame.pack(side="left")

                self.btn_back = ttk.Button(button_frame, text="<-", command=self.on_back, state="disabled", width=3)
                self.btn_back.pack(side="left", padx=(0, 2))

                self.btn_forward = ttk.Button(button_frame, text="->", command=self.on_forward, state="disabled", width=3)
                self.btn_forward.pack(side="left", padx=2)

                self.btn_up = ttk.Button(button_frame, text="↑", command=self.on_up, state="disabled", width=3)
                self.btn_up.pack(side="left", padx=2)

                self.btn_refresh = ttk.Button(button_frame, text="↻", command=self.on_refresh, state="normal", width=3)
                self.btn_refresh.pack(side="left", padx=(2, 5))

                ttk.Separator(button_frame, orient="vertical").pack(side="left", fill="y", padx=5)

                self.btn_new_tab = ttk.Button(button_frame, text="+", command=lambda: self.add_tab(path=None), width=3)
                self.btn_new_tab.pack(side="left", padx=(5, 2))

                self.btn_close_tab = ttk.Button(button_frame, text="-", command=self.on_close_tab, width=3)
                self.btn_close_tab.pack(side="left", padx=2)



            #Поле пути к текущему каталогу
            def create_path_entry(self):
                self.path_var = tk.StringVar()
                self.path_entry = ttk.Entry(self.toolbar_frame, textvariable=self.path_var, font=("Arial", 10))
                self.path_entry.pack(side="left", fill="x", expand=True, padx=5, ipady=2)

                #При нажатие Enter обновляем путь
                self.path_entry.bind("<Return>", self.on_path_enter)

                #Контекстное меню по ПКМ
                self.path_menu = Menu(self.FM, tearoff=0)
                self.path_menu.add_command(label="Копировать путь", command=self.copy_path_to_clipboard)
                self.path_menu.add_command(label="Вставить", command=self.paste_from_clipboard)
                self.path_entry.bind("<Button-3>", self.show_path_context_menu)



            #Создаём верхнее меню программы
            def create_menu(self):
                menubar = tk.Menu(self.FM)
                menubar.add_command(label="Поиск", command=self.open_search_dialog)
                menubar.add_command(label="О программе", command=self.about_FM)
                self.FM.config(menu=menubar)



            def add_tab(self, path=None):
                tab_frame = ttk.Frame(self.notebook, padding=5)

                #Создаем Таблицу и Скролл бар
                tree = ttk.Treeview(tab_frame, selectmode="browse", show="headings") 
                vsb = ttk.Scrollbar(tab_frame, orient="vertical", command=tree.yview)
                tree.configure(yscrollcommand=vsb.set)

                vsb.pack(side="right", fill="y")
                tree.pack(side="left", fill="both", expand=True)

                #Настройка колонок таблицы и сортировки
                columns = ("Имя", "Размер", "Тип", "Дата изменения")
                tree["columns"] = columns

                col_widths = {"Имя": 300, "Размер": 100, "Тип": 120, "Дата изменения": 150}

                tree.column("#0", width=0, stretch=tk.NO) #Убираем колонку по умолчанию

                for col in columns:
                    tree.heading(col, text=col, command=lambda c=col: self.on_tree_sort(c))
                    tree.column(col, width=col_widths.get(col, 150), anchor=tk.W if col != "Размер" else tk.E)

                #Бинды для таблицы
                tree.bind("<Double-1>", self.on_tree_double_click)

                tree.bind("<Button-3>", self.on_tree_right_click)

                #Привязка обработчика клавиш
                tree.bind("<Key>", self.on_key_press)

                #Привязка универсального обработчика клавиш
                tree.bind("<Key>", self.on_key_press)

                #Привязка кнопки "Контекстное меню" (Menu)
                tree.bind("<Menu>", self.on_key_context_menu)

                #Добавляем фрейм в панель
                self.notebook.add(tab_frame, text="Загрузка...")

                tab_id = str(tab_frame)

                #Сохраняем состояние вкладки
                self.tabs_data[tab_id] = {
                    "frame": tab_frame,
                    "tree": tree,
                    "vsb": vsb,
                    "path": None, #Будет установлен в load_directory
                    "files_info": [], #Кэш данных для сортировки
                    "history": [],
                    "history_index": -1,
                    "sort_col": "Имя",
                    "sort_dir": False #False = asc, True = desc
                }

                #Загружаем данные
                self.load_directory_for_tab(tab_id, path)

                #Активируем вкладку
                self.notebook.select(tab_id)

                all_item_ids = tree.get_children()
                first_item_id = all_item_ids[0]
                tree.focus(first_item_id)
                #tree.after(100, tree.focus_set)



            #Закрывает текущую вкладку
            def on_close_tab(self):
                if len(self.notebook.tabs()) <= 1:
                    return #Не даем закрыть последнюю вкладку

                selected_tab_id = self.get_current_tab_id()
                if selected_tab_id:
                    if selected_tab_id in self.tabs_data:
                        del self.tabs_data[selected_tab_id]
                    self.notebook.forget(selected_tab_id)



            #Смена вкладками
            def on_tab_changed(self, event):
                self.update_path_entry()
                self.update_toolbar_buttons()

                #Возвращаем клавиатурный фокус на таблицу
                data = self.get_current_tab_data()
                if data and data.get("tree"):
                    tree = data["tree"]
                    #Получаем ID элемента, который был в фокусе в этой вкладке
                    current_focus_id = tree.focus()

                    if current_focus_id:
                        #Если какой-то элемент уже был в фокусе, возвращаем фокус ему
                        tree.after(10, lambda: tree.focus(current_focus_id))
                    else:
                        #Если фокуса не было, то фокусируемся на первом элементе

                        all_items = tree.get_children()
                        if all_items:
                            tree.after(10, lambda: tree.focus(all_items[0]))
                        else:
                            tree.after(10, tree.focus_set)



            #Загружает данные о файлах для указанной вкладки по указанному пути
            def load_directory_for_tab(self, tab_id, path=None, is_history_nav=False):
                tab_data = self.tabs_data.get(tab_id)
                if not tab_data:
                    return

                #Если путь не передан, берем текущий из данных вкладки
                if path is None:
                    path = tab_data.get("path")

                    #Если пути всё еще нет (первый запуск), запрашиваем его
                    if run_in_recovery:
                        default_path = get_current_disc(run_in_recovery)
                    else:
                        default_path = "C:\\"
                    if not os.path.isdir(default_path):
                        default_path = drives[0] #Берем первый диск

                    chosen_path = simpledialog.askstring(random_string(),f"Введите путь\nДоступные диски: {get_available_drives()}", initialvalue=default_path)
                    if chosen_path:
                        path = chosen_path
                    else:
                        self.on_close_tab() #Пользователь нажал "Отмена"
                        return
                
                if not os.path.exists(path):
                    messagebox.showerror("Ошибка", f"Путь не найден: {path}")
                    #Возвращаем старый путь в поле ввода, если ввели неверный
                    self.update_path_entry()
                    return

                try:
                    files_info = get_files_info(path)
                    tab_data["path"] = path
                    tab_data["files_info"] = files_info
                    
                    #Сбрасываем поиск при обычном переходе
                    if "search_results" in tab_data:
                        tab_data["search_results"]["is_active"] = False

                    #Логика истории
                    if not is_history_nav:
                        if tab_data["history_index"] < len(tab_data["history"]) - 1:
                            tab_data["history"] = tab_data["history"][:tab_data["history_index"] + 1]
                        if not tab_data["history"] or tab_data["history"][-1] != path:
                            tab_data["history"].append(path)
                            tab_data["history_index"] = len(tab_data["history"]) - 1

                    self.populate_treeview(tab_data)
                    self.update_tab_title(tab_id, path)
                    
                    #Обновляем поле пути после успешной загрузки
                    self.update_path_entry()
                    self.update_toolbar_buttons()
                    
                except Exception as e:
                    logger.error(f"FM - Ошибка доступа к {path}: {e}")
                    messagebox.showerror("Ошибка", f"Нет доступа к: {path}")



            #Заполняет таблицу данными
            def populate_treeview(self, tab_data):
                tree = tab_data["tree"]
                files_info = tab_data["files_info"]
                sort_col = tab_data["sort_col"]
                sort_dir = tab_data["sort_dir"]

                tree.delete(*tree.get_children()) #Очистка

                #Сортировка
                sorted_files = self.sort_files(files_info, sort_col, sort_dir)

                #Заполнение таблицы
                for item in sorted_files:
                    size_str = get_formatted_size(item["size"])
                    mod_time_str = format_time(item["edited"])

                    values = (item["name"], size_str, item["type"], mod_time_str)

                    #iid (Item ID) - полный путь к файлу
                    tree.insert("", "end", iid=item["path"], values=values)

                    if item["is_dir"]:
                        tree.item(item["path"], tags=("directory",))

                tree.tag_configure("directory", foreground="#0000AA")

                #Получаем список ID всех элементов в таблице
                all_item_ids = tree.get_children()

                if all_item_ids:
                    #Если список не пуст, берем ID первого элемента
                    first_item_id = all_item_ids[0]

                    #Выделяем и ставим фокус на этот элемент
                    tree.selection_set(first_item_id)
                    tree.focus(first_item_id)
                else:
                    #Если каталог пустой, просто ставим фокус на саму таблицу
                    tree.focus_set()



            #Кнопка назад "<-"
            def on_back(self):
                data = self.get_current_tab_data()
                if data and data["history_index"] > 0:
                    data["history_index"] -= 1
                    path = data["history"][data["history_index"]]
                    self.load_directory_for_tab(self.get_current_tab_id(), path, is_history_nav=True)



            #Кнопка вперёд "->"
            def on_forward(self):
                data = self.get_current_tab_data()
                if data and data["history_index"] < len(data["history"]) - 1:
                    data["history_index"] += 1
                    path = data["history"][data["history_index"]]
                    self.load_directory_for_tab(self.get_current_tab_id(), path, is_history_nav=True)



            #Кнопка вверх "↑"
            def on_up(self):
                data = self.get_current_tab_data()
                if data and data["path"]:
                    parent_path = os.path.dirname(data["path"])
                    if parent_path != data["path"]: #Проверка, что не корневой каталог
                        self.load_directory_for_tab(self.get_current_tab_id(), parent_path)



            #Кнопка обновить "↻"
            def on_refresh(self):
                data = self.get_current_tab_data()
                if data and data["path"]:
                    self.load_directory_for_tab(self.get_current_tab_id(), data["path"], is_history_nav=True)



            #Нажатие Enter в поле пути
            def on_path_enter(self, event):
                new_path = self.path_var.get().strip()
                current_tab_id = self.get_current_tab_id()
                
                if current_tab_id and new_path:
                    #Вызываем загрузку директории для текущей вкладки
                    self.load_directory_for_tab(current_tab_id, new_path)
                    
                #Убираем фокус с поля ввода, чтобы горячие клавиши снова работали
                self.FM.focus_set()



            #Меню ПКМ
            def show_path_context_menu(self, event):
                try:
                    self.path_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.path_menu.grab_release()



            #Копируем текст в буфер обмена
            def copy_path_to_clipboard(self, all=True):
                if all:
                    self.FM.clipboard_clear()
                    self.FM.clipboard_append(self.path_var.get())
                elif not all:
                    try:
                        selected = self.path_entry.selection_get()
                        self.FM.clipboard_clear()
                        self.FM.clipboard_append(selected)
                    except tk.TclError:
                        pass #Ничего не выделено



            #Вставка из буфера обмена
            def paste_from_clipboard(self):
                try:
                    clipboard_data = self.FM.clipboard_get()
                    self.path_entry.delete(0, tk.END)
                    self.path_entry.insert(0, clipboard_data)
                except tk.TclError:
                    pass #Буфер обмена пуст



            #Обработка двойного клика
            def on_tree_double_click(self, event):
                data = self.get_current_tab_data()
                if not data: return

                tree = data["tree"]
                
                #Получаем идентификатор элемента, на котором был сделан клик
                item_id = tree.identify_row(event.y)
                
                #Если item_id пуст, значит, клик был не на элементе (возможно, на заголовке или на пустом месте)
                if not item_id:
                    #Проверяем, был ли клик на заголовке
                    region = tree.identify_region(event.x, event.y)
                    if region == "heading":
                        #Если на заголовке, то это был клик для сортировки.
                        #Прерываем обработку, чтобы не открывать выделенный элемент.
                        return

                #Если клик был на элементе
                item_id = tree.focus() #Получаем выделенный элемент (на который наведен фокус)

                if not item_id: return

                if os.path.isdir(item_id):
                    #Если это каталог, загружаем ее
                    self.load_directory_for_tab(self.get_current_tab_id(), item_id)
                elif os.path.isfile(item_id):
                    #Если это файл, открываем его
                    self.open_file(item_id)



            #меню по ПКМ
            def on_tree_right_click(self, event):
                data = self.get_current_tab_data()
                if not data: return

                tree = data["tree"]
                item_id = tree.identify_row(event.y)

                target_type = "item"
                target_path = item_id

                if not item_id:
                    #Клик на пустом месте
                    target_type = "directory"
                    target_path = data["path"] #Используем путь текущей вкладки
                    #Сбрасываем фокус, чтобы было понятно, что работаем не с элементом
                    tree.focus("")
                    tree.selection_remove(tree.selection())
                else:
                    #Клик на элементе
                    #Выделяем элемент, по которому кликнули
                    tree.selection_set(item_id)
                    tree.focus(item_id)

                menu = self.build_context_menu(target_type, target_path)

                #Показываем меню
                try:
                    menu.tk_popup(event.x_root, event.y_root)
                finally:
                    menu.grab_release()



            #Сортировка по нажатия на заголовок столбика
            def on_tree_sort(self, col):
                data = self.get_current_tab_data()
                if not data: return

                tree = data["tree"]

                if data["sort_col"] == col:
                    data["sort_dir"] = not data["sort_dir"]
                else:
                    data["sort_col"] = col
                    data["sort_dir"] = False #По умолчанию asc

                reverse = data["sort_dir"]

                #Обновляем заголовки (добавляем стрелочку)
                for c in tree["columns"]:
                    tree.heading(c, text=c) #Сбрасываем все

                arrow = " ▼" if reverse else " ▲"
                tree.heading(col, text=col + arrow)

                #Перезаполняем таблицу с новой сортировкой
                self.populate_treeview(data)



            #Обработка сочетаний клавиш
            def on_key_press(self, event):
                keysym = event.keysym

                #Получаем данные текущей вкладки
                data = self.get_current_tab_data()

                #Проверяем, активно ли состояние поиска
                is_search_active = (data and
                                    data.get("search_results") and
                                    data["search_results"].get("is_active"))

                if keysym == "BackSpace" and is_search_active:
                    #Если активен поиск и нажата Backspace, принудительно вызываем "Назад"
                    self.on_back()
                    return "break" #Останавливаем дальнейшую обработку клавиши

                shift_mask = 0x0001
                ctrl_mask = 0x0004 #Control

                is_ctrl_pressed = (event.state & ctrl_mask) != 0

                if is_ctrl_pressed:
                    if keysym == "n":
                        is_shift_pressed = (event.state & shift_mask) != 0
                        if is_shift_pressed:
                            #Ctrl + Shift + N
                            self.action_in_path("create_path")
                        else:
                            #Ctrl + N
                            self.action_in_path("create_file")
                        return "break"

                    if keysym == "c":
                        self.handle_copy()
                        return "break"
                    if keysym == "x":
                        self.handle_cut()
                        return "break"
                    if keysym == "v":
                        self.handle_paste()
                        return "break"

                    if keysym == "i":
                        self.show_properties()
                        return "break"

                action_name = self.key_actions.get(keysym)

                if action_name:
                    #Если для этой клавиши есть действие, получаем сам метод по его имени
                    action_method = getattr(self, action_name, None)

                    if action_method:
                        #Выполняем метод
                        if action_name == "handle_key_rename":
                            self.action_in_path("rename")
                        else:
                            action_method()

                        return "break"



            #Кнопка Enter
            def handle_key_enter(self):
                data = self.get_current_tab_data()
                if not data: return
                tree = data["tree"]
                item_id = tree.focus()
                if not item_id: return

                if os.path.isdir(item_id):
                    self.load_directory_for_tab(self.get_current_tab_id(), item_id)
                elif os.path.isfile(item_id):
                    self.open_file(item_id)



            #Кнопка Delete
            def handle_key_delete(self):
                data = self.get_current_tab_data()
                if not data: return

                tree = data["tree"]
                item_id = tree.focus()
                if not item_id: return

                #Защита от удаления ".." (пункт "вверх")
                if item_id.endswith(".."):
                    return

                #Удаляем элемент
                self.delete_item(item_id)



            #Получаем путь к выделенному файлу
            def get_focused_item_path(self):
                data = self.get_current_tab_data()
                if not data: return None
                tree = data["tree"]
                item_id = tree.focus()
                return item_id



            #Получаем автора файла
            def get_author_and_verison_file(self, path):
                if os.path.isdir(path):
                    return "Н/Д (Каталог)"

                version = "Н/Ж"
                author = "Н/Д"

                try:
                    #Получаем информацию о версии файла
                    fixed_info = win32api.GetFileVersionInfo(path, '\\')
                    if fixed_info:
                        ms = fixed_info["FileVersionMS"]
                        ls = fixed_info["FileVersionLS"]
                        version = (
                            f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}."
                            f"{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                        )

                    #Получаем язык и кодировку
                    lang, codepage = win32api.GetFileVersionInfo(path, "\\VarFileInfo\\Translation")[0]

                    #Формируем путь к строковым данным
                    str_info_path = f"\\StringFileInfo\\{lang:04x}{codepage:04x}\\"

                    #Пробуем получить разные поля, которые могут содержать "Автора"
                    author_keys = ["LegalCopyright", "CompanyName", "InternalName", "FileDescription"]

                    for key in author_keys:
                        try:
                            author_try = win32api.GetFileVersionInfo(path, str_info_path + key)
                            if author_try:
                                author = author_try
                                break #Нашли первое непустое значение
                        except Exception:
                            continue #Ключ не найден, пробуем следующий

                except Exception as e:
                    pass

                return version, author



            #Проверяет права доступа и возвращает Да или Нет
            def get_access_string(self, path, access_type):
                try:
                    #os.access проверяет права текущего пользователя
                    if os.access(path, access_type):
                        return "Да"
                    else:
                        return "Нет"
                except Exception as e:
                    logger.warning(f"FM - Ошибка проверки доступа для {path}:\n{e}")
                    return "Ошибка"



            #Свойства файла
            def show_properties(self):
                item_path = self.get_focused_item_path()

                #Не показываем свойства для ".." (вверх)
                if not item_path or item_path.endswith(".."):
                    return

                #Создаём окно свойств
                prop_win = tk.Toplevel(self.FM)
                prop_win.title(f"Свойства: {os.path.basename(item_path)}")
                prop_win.geometry("350x450")
                prop_win.transient(self.FM) #Связываем с главным окном
                prop_win.grab_set() #Делаем окно модальным
                prop_win.resizable(True, True) #Разрешим менять размер

                #Создаем главный фрейм с отступами
                main_frame = ttk.Frame(prop_win, padding=(10, 10, 10, 10))
                main_frame.pack(fill="both", expand=True)

                #Фрейм для таблицы и скроллбара
                tree_frame = ttk.Frame(main_frame)
                tree_frame.pack(fill="both", expand=True)

                #Создаем Таблицу
                tree = ttk.Treeview(tree_frame, columns=("param", "value"), show="headings", selectmode="none")
                vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
                tree.configure(yscrollcommand=vsb.set)

                tree.heading("param", text="Параметр", anchor=tk.W)
                tree.heading("value", text="Значение", anchor=tk.W)
                #Колонка "Параметр" - фиксированная, "Значение" - растягивается
                tree.column("param", width=150, stretch=False, anchor=tk.W)
                tree.column("value", width=350, stretch=True, anchor=tk.W)

                vsb.pack(side="right", fill="y")
                tree.pack(side="left", fill="both", expand=True)

                #Сбор информации
                properties_data = []
                try:
                    #Стандартная информация
                    stat = os.stat(item_path)
                    file_name = os.path.basename(item_path)
                    file_path = os.path.dirname(item_path)
                    file_size_bytes = stat.st_size

                    #Используем функцию форматирования
                    file_size_formatted = get_formatted_size(file_size_bytes)

                    created = format_time(stat.st_ctime) #Создан
                    edited = format_time(stat.st_mtime) #Изменен
                    accessed = format_time(stat.st_atime) #Открыт

                    #специфичная информация
                    version, author = self.get_author_and_verison_file(item_path)

                    #Права доступа
                    acc_read = self.get_access_string(item_path, os.R_OK)
                    acc_write = self.get_access_string(item_path, os.W_OK)
                    acc_exec = self.get_access_string(item_path, os.X_OK)

                    acc_modify = acc_write

                    acc_full = "Да" if (acc_read == "Да" and acc_write == "Да" and acc_exec == "Да") else "Нет"

                    #Формируем список для вывода
                    #Используем "---" как разделитель
                    properties_data = [
                        ("Имя", file_name),
                        ("Расположение", file_path),
                        ("Размер", file_size_formatted),
                        ("---", "---"),
                        ("Создан", created),
                        ("Изменён", edited),
                        ("Открыт", accessed),
                        ("---", "---"),
                        ("Версия файла", version),
                        ("Автор", author),
                        ("---", "---"),
                        ("Права доступа (для " + self.user_name + "):", ""),
                        ("Полный доступ", acc_full),
                        ("Чтение", acc_read),
                        ("Изменение", acc_modify),
                        ("Запись", acc_write),
                        ("Запуск", acc_exec),
                    ]

                except Exception as e:
                    logger.error(f"FM - Ошибка при сборе свойств для {item_path}:\n{e}")
                    tree.insert("", "end", values=("Ошибка", f"Не удалось прочитать свойства файла:\n{e}"))
                    properties_data = []

                #Заполнение таблицы
                #Настраиваем теги для выделения разделителей и заголовков
                tree.tag_configure("separator", background="#F0F0F0")
                tree.tag_configure("header", font=("Arial", 9, "bold"))

                for param, value in properties_data:
                    if param == "---":
                        #Вставляем пустую строку для разделения
                        item = tree.insert("", "end", values=("", ""), tags=("separator",))
                        tree.item(item, values=("", "")) #Очищаем значения
                    elif value == "":
                        #Это заголовок
                        tree.insert("", "end", values=(param, ""), tags=("header",))
                    else:
                        tree.insert("", "end", values=(param, value))

                #Кнопка OK
                ok_button = ttk.Button(main_frame, text="OK", command=prop_win.destroy, width=15)
                ok_button.pack(side="right", pady=(10, 0)) #Отступ сверху

                #Устанавливаем фокус на кнопку OK, чтобы Enter ее нажимал
                ok_button.after(100, ok_button.focus_set)

                #Привязываем <Return> (Enter) и <Escape> к закрытию окна
                prop_win.bind("<Return>", lambda e: prop_win.destroy())
                prop_win.bind("<Escape>", lambda e: prop_win.destroy())



            #Запрашиваем данные или имя
            def ask_for_name(self, title, prompt, initial_value=""):
                new_name = simpledialog.askstring(
                    title,
                    prompt,
                    initialvalue=initial_value,
                    parent=self.FM
                )

                if new_name is None: #Пользователь нажал "Отмена"
                    return None

                if not new_name.strip():
                    messagebox.showwarning(random_string(), "Имя не может быть пустым.", parent=self.FM)
                    return None

                #Проверка на недопустимые символы
                invalid_chars = '<>:"/\\|?*'
                if any(char in new_name for char in invalid_chars):
                    messagebox.showwarning(random_string(), f"Имя содержит недопустимые символы:\n{invalid_chars}", parent=self.FM)
                    return None

                return new_name



            #Действие с файлами и каталогами
            def action_in_path(self, action):
                data = self.get_current_tab_data()
                if not data: return

                tree = data["tree"]
                
                #Для создания (create_path, create_file) работаем с текущим каталогом
                if action in ["create_path", "create_file"]:
                    current_dir = data["path"]
                    old_name = "Новая папка" if action == "create_path" else "Новый файл"
                    old_path = None #Нет старого пути для создания
                else: #Для переименования
                    old_path = self.get_focused_item_path()

                    if not old_path or old_path.endswith(".."):
                        return #Нельзя переименовать ".." (вверх)

                    old_name = os.path.basename(old_path)
                    current_dir = os.path.dirname(old_path)

                #Проверяем, что текущий каталог существует
                if not os.path.isdir(current_dir):
                    messagebox.showerror(random_string(), f"Текущий каталог не найден: {current_dir}", parent=self.FM)
                    return

                new_name = self.ask_for_name(random_string(), f"Новое имя для:\n{old_name}", initial_value=old_name)

                if new_name is None:
                    return #Отмена

                if action == "rename" and new_name == old_name:
                    return #Имя не изменилось

                new_path = os.path.join(current_dir, new_name)

                if action != "rename" and os.path.exists(new_path):
                    messagebox.showerror(random_string(), f"Файл или папка с именем '{new_name}' уже существует.", parent=self.FM)
                    return
                elif action == "rename" and old_path != new_path and os.path.exists(new_path):
                    messagebox.showerror(random_string(), f"Файл или папка с именем '{new_name}' уже существует.", parent=self.FM)
                    return


                if action == "rename":
                    try:
                        os.rename(old_path, new_path)
                        logger.info(f"FM - Переименовано: {old_path} -> {new_path}")
                        self.on_refresh()

                        #Пытаемся восстановить фокус на переименованном файле
                        tree.after(100, lambda: self.focus_item_by_path(new_path))

                    except Exception as e:
                        logger.error(f"FM - Ошибка переименования:\n{e}")
                        messagebox.showerror(random_string(), f"Не удалось переименовать:\n{e}", parent=self.FM)

                elif action == "create_path":
                    try:
                        os.mkdir(new_path)
                        logger.info(f"FM - Создан каталог: {new_path}")
                        self.on_refresh()
                    except Exception as e:
                        logger.error(f"FM - Ошибка создания каталога\n{e}")
                        messagebox.showerror(random_string(), f"Не удалось создать каталог:\n{e}", parent=self.FM)

                elif action == "create_file":
                    #Запрос содержимого
                    content = simpledialog.askstring(random_string(), f"Введите содержимое для файла:\n{new_name}", parent=self.FM)

                    #Если пользователь нажал Отмена или не ввел содержимое
                    if content is None:
                         return 

                    try:
                        with open(new_path, "w") as new_file:
                            new_file.write(content)

                        logger.info(f"FM - Создан файл:\n{new_path}")
                        self.on_refresh()
                    except Exception as e:
                        logger.error(f"FM - Ошибка создания файла:\n{e}")
                        messagebox.showerror(random_string(), f"Не удалось создать файл:\n{e}", parent=self.FM)



            #Устанавливаем фокус на элемент
            def focus_item_by_path(self, item_path):
                try:
                    data = self.get_current_tab_data()
                    if not data or not data.get("tree"): return

                    tree = data["tree"]
                    if tree.exists(item_path):
                        tree.selection_set(item_path)
                        tree.focus(item_path)
                        tree.see(item_path) #Прокрутить до элемента
                except Exception as e:
                    logger.warning(f"FM - Не удалось восстановить фокус на {item_path}:\n{e}")



            #Создание Контенкстного меню
            def build_context_menu(self, target_type, target_path):
                menu = tk.Menu(self.FM, tearoff=0)
                data = self.get_current_tab_data()

                #Общие состояния
                paste_state = "normal" if self.clipboard_data["path"] else "disabled"

                if target_type == "item":
                    #Меню для Элемента
                    is_dir = os.path.isdir(target_path)
                    is_dotdot = target_path.endswith("..")
                    item_state = "disabled" if is_dotdot else "normal"

                    #Открыть и Вверх
                    if is_dotdot:
                        menu.add_command(label="Вверх", accelerator="Backspace", command=self.on_up)
                    elif is_dir:
                        #Используем lambda для отложенного вызова
                        menu.add_command(label="Открыть", accelerator="Enter", command=lambda: self.load_directory_for_tab(self.get_current_tab_id(), target_path))
                    else:
                        menu.add_command(label="Открыть", accelerator="Enter", command=lambda: self.open_file(target_path))

                    menu.add_separator()

                    #Вырезать, Копировать, Вставить
                    menu.add_command(label="Вырезать", accelerator="Ctrl+X",
                                     command=self.handle_cut, state=item_state)
                    menu.add_command(label="Копировать", accelerator="Ctrl+C",
                                     command=self.handle_copy, state=item_state)
                    menu.add_command(label="Вставить", accelerator="Ctrl+V",
                                     command=self.handle_paste, state=paste_state)

                    menu.add_separator()

                    #Переименовать и Удалить
                    menu.add_command(label="Переименовать", accelerator="F2",
                                     command=lambda: self.action_in_path("rename"), state=item_state)
                    menu.add_command(label="Удалить", accelerator="Delete",
                                     command=self.handle_key_delete, state=item_state)

                    menu.add_separator()

                    #Создать
                    sub_menu_create = tk.Menu(menu, tearoff=0)
                    sub_menu_create.add_command(label="Каталог", accelerator="Ctrl+Shift+N",
                                                command=lambda: self.action_in_path("create_path"))
                    sub_menu_create.add_command(label="Файл", accelerator="Ctrl+N",
                                                command=lambda: self.action_in_path("create_file"))
                    menu.add_cascade(label="Создать", menu=sub_menu_create)

                    menu.add_separator()

                    #Свойства
                    menu.add_command(label="Свойства", accelerator="Ctrl+I",
                                     command=self.show_properties, state=item_state)

                    #Копировать данные
                    menu.add_command(label="Копировать путь", command=lambda: self.copy_to_clipboard(target_path))
                    menu.add_command(label="Копировать имя", command=lambda: self.copy_to_clipboard(os.path.basename(target_path)))

                elif target_type == "directory":
                    #Меню для Каталога (пустого места) ---
                    current_dir_path = target_path

                    #Создать
                    sub_menu_create = tk.Menu(menu, tearoff=0)
                    sub_menu_create.add_command(label="Каталог", accelerator="Ctrl+Shift+N",
                                                command=lambda: self.action_in_path("create_path"))
                    sub_menu_create.add_command(label="Файл", accelerator="Ctrl+N",
                                                command=lambda: self.action_in_path("create_file"))
                    menu.add_cascade(label="Создать", menu=sub_menu_create)

                    menu.add_separator()

                    #Вставить и Обновить
                    menu.add_command(label="Вставить", accelerator="Ctrl+V",
                                     command=self.handle_paste, state=paste_state)
                    menu.add_command(label="Обновить", accelerator="F5", command=self.on_refresh)

                    menu.add_separator()

                    #Копировать путь
                    menu.add_command(label="Копировать путь", command=lambda: self.copy_to_clipboard(current_dir_path))

                return menu



            #Обработчик клавиш
            def on_key_context_menu(self, event):
                data = self.get_current_tab_data()
                if not data: return "break"

                tree = data["tree"]

                #Проверяем, нажат ли Ctrl
                ctrl_mask = 0x0004
                is_ctrl_pressed = (event.state & ctrl_mask) != 0

                x, y = 0, 0
                target_type = ""
                target_path = ""

                if is_ctrl_pressed:
                    #Меню для каталога (Ctrl + Menu)
                    target_type = "directory"
                    target_path = data["path"]
                    #Координаты: верхний левый угол таблицы
                    x = tree.winfo_rootx() + 10
                    y = tree.winfo_rooty() + 10
                else:
                    #Меню для элемента
                    target_type = "item"
                    target_path = self.get_focused_item_path()

                    if not target_path: #Ничего не выбрано
                        return "break"

                    #Координаты: под выбранным элементом
                    bbox = tree.bbox(target_path)
                    if not bbox: #Элемент не виден (например, прокручен)
                        #Просто покажем в углу
                        x = tree.winfo_rootx() + 10
                        y = tree.winfo_rooty() + 10
                    else:
                        x = tree.winfo_rootx() + bbox[0]
                        y = tree.winfo_rooty() + bbox[1] + bbox[3]

                #Создаём меню
                menu = self.build_context_menu(target_type, target_path)

                #Сохраняем ссылку на меню, чтобы отследить закрытие
                self.active_context_menu = menu

                #Привязываем событие <Unmap> (скрытие/закрытие) для очистки
                menu.bind("<Unmap>", self.on_context_menu_close, add="+")

                #Устанавливаем фокус на само меню
                menu.focus_set()

                try:
                    #Показываем меню
                    menu.tk_popup(x, y)
                finally:
                    menu.grab_release()

                return "break" #Прерываем дальнейшую обработку события



            #Возвращаем фокус на таблицу при закрытии меню
            def on_context_menu_close(self, event):
                if self.active_context_menu:
                    try:
                        #Отвязываем, чтобы избежать повторных вызовов
                        self.active_context_menu.unbind("<Unmap>")
                    except tk.TclError:
                        pass #Меню уже может быть уничтожено
                    self.active_context_menu = None



            #Копируем путь в буфер обмена
            def handle_copy(self):
                item_path = self.get_focused_item_path()
                if not item_path or item_path.endswith(".."):
                    return
                self.clipboard_data = {"path": item_path, "action": "copy"}
                logger.info(f"FM - Скопировано: {item_path}")



            #Помещаем объект в буфер обмена программы
            def handle_cut(self):
                item_path = self.get_focused_item_path()
                if not item_path or item_path.endswith(".."):
                    return
                self.clipboard_data = {"path": item_path, "action": "cut"}
                logger.info(f"FM - Вырезано: {item_path}")



            #Вставляем оюъект из буфера программы
            def handle_paste(self):
                if not self.clipboard_data["path"]:
                    messagebox.info(random_string(), "Буфер обмена пуст, вставка отменена.")
                    return

                src_path = self.clipboard_data["path"]
                action = self.clipboard_data["action"]

                data = self.get_current_tab_data()
                if not data or not data["path"]:
                    messagebox.info(random_string(), "Не выбран каталог для вставки.")
                    return #Некуда вставлять

                dest_dir = data["path"]
                dest_path = os.path.join(dest_dir, os.path.basename(src_path))

                #Проверка, что источник все еще существует
                if not os.path.exists(src_path):
                    messagebox.showerror(random_string(), f"Источник не найден (возможно, был перемещен):\n{src_path}")
                    self.clipboard_data = {"path": None, "action": None} #Очистить буфер
                    return

                #Защита от вставки в самого себя
                if os.path.normpath(src_path) == os.path.normpath(dest_path) or \
                   (os.path.isdir(src_path) and os.path.normpath(dest_dir).startswith(os.path.normpath(src_path))):
                    messagebox.showerror(random_string(), "Нельзя скопировать или переместить элемент сам в себя.")
                    return

                #Логика конфликта (Заменить или Пропустить)
                if os.path.exists(dest_path):
                    choice = messagebox.askquestion("Конфликт", f'Файл "{os.path.basename(dest_path)}" уже существует.\n\nЗаменить его?', icon="warning", type="yesno")

                    if choice == "no": #no означает пропустить
                        return
                    else: #yes означает заменить
                        try:
                            if os.path.isdir(dest_path):
                                shutil.rmtree(dest_path)
                            else:
                                os.remove(dest_path)
                        except Exception as e:
                            messagebox.showerror(random_string(), f"Не удалось заменить: {e}")
                            return

                #Выполнение действия (Копирование или Перемещение)
                try:
                    if action == "copy":
                        if os.path.isdir(src_path):
                            shutil.copytree(src_path, dest_path)
                        else:
                            shutil.copy2(src_path, dest_path)
                        logger.info(f"FM - Скопирован {src_path} в {dest_path}")

                    elif action == "cut":
                        shutil.move(src_path, dest_path)
                        logger.info(f"FM - Перемещён {src_path} в {dest_path}")
                        #Очищаем буфер после успешного перемещения
                        self.clipboard_data = {"path": None, "action": None}

                except Exception as e:
                    logger.error(f"FM - Ошибка вставки:\n{e}")
                    messagebox.showerror(random_string(), f"Не удалось {action}:\n{e}")

                self.on_refresh()



            #Вызывает диалог переименования для выделенного элемента
            def handle_key_rename(self):
                pass



            #Получаем ID текущей вкладки
            def get_current_tab_id(self):
                try:
                    return self.notebook.select()
                except tk.TclError:
                    return None #Нет вкладок



            #Данные для текущей вкладки
            def get_current_tab_data(self):
                tab_id = self.get_current_tab_id()
                if tab_id:
                    return self.tabs_data.get(tab_id)
                return None



            #Обновляет заголовок вкладки
            def update_tab_title(self, tab_id, path):
                name = os.path.basename(path)
                if not name: #Случай корня (C:\)
                    name = path.replace("\\", "").replace("/", "")

                if len(name) > 10:
                    title = name[:10] + "..."
                else:
                    title = name

                self.notebook.tab(tab_id, text=title)



            #Обновляем поле пути
            def update_path_entry(self):
                data = self.get_current_tab_data()
                if data and "path" in data:
                    self.path_var.set(data["path"])
                    #Прокручиваем текст в конец, чтобы видеть текущий каталог
                    self.path_entry.xview_moveto(1)
                else:
                    self.path_var.set("")



            #Обновление статусов доступности кнопок навигации
            def update_toolbar_buttons(self):
                data = self.get_current_tab_data()
                if data and data["path"]:
                    #История
                    self.btn_back.config(state="normal" if data["history_index"] > 0 else "disabled")
                    self.btn_forward.config(state="normal" if data["history_index"] < len(data["history"]) - 1 else "disabled")

                    #Кнопка "Вверх"
                    parent_path = os.path.dirname(data["path"])
                    self.btn_up.config(state="normal" if parent_path != data["path"] else "disabled")

                    self.btn_refresh.config(state="normal")
                else:
                    #Нет вкладок
                    self.btn_back.config(state="disabled")
                    self.btn_forward.config(state="disabled")
                    self.btn_up.config(state="disabled")
                    self.btn_refresh.config(state="disabled")



            #Сортировка таблицы
            def sort_files(self, files_list, col, reverse):
                def get_sort_key(item):
                    #Сначала всегда папки (и ".."), потом файлы
                    #".." всегда в самом верху
                    if item["name"] == "..":
                        sort_group = -1
                    elif item["is_dir"]:
                        sort_group = 0
                    else:
                        sort_group = 1

                    #Ключ сортировки в зависимости от колонки
                    if col == "Имя":
                        key = item["name"].lower()
                    elif col == "Размер":
                        key = item["size"]
                    elif col == "Тип":
                        key = item["type"]
                    elif col == "Дата изменения":
                        key = item["edited"]
                    else:
                        key = item["name"].lower()

                    return (sort_group, key) #Сортируем по группе, затем по ключу

                return sorted(files_list, key=get_sort_key, reverse=reverse)



            #Открываем файл
            def open_file(self, file_path):
                try:
                    os.startfile(file_path)
                except Exception as e:
                    logger.error(f"FM - Не удалось открыть файл {file_path}:\n{e}")
                    messagebox.showerror(random_string(), f"Не удалось открыть файл:\n{e}")



            #Удаляем объект
            def delete_item(self, path):
                try:
                    name = os.path.basename(path)
                    if not messagebox.askyesno(random_string(), f"Вы уверены, что хотите удалить '{name}'?\n\nЭтот элемент будет удален БЕЗВОЗВРАТНО."):
                        return

                    if os.path.isdir(path):
                        shutil.rmtree(path)
                        logger.info(f"FM - Удалён каталог: {path}")
                    else:
                        os.remove(path)
                        logger.info(f"FM - Удалён файл: {path}")

                    self.on_refresh()
                except Exception as e:
                    logger.error(f"FM - Ошибка удаления {path}:\n{e}")
                    messagebox.showerror(random_string(), f"Не удалось удалить:\n{e}")



            #Копируем текст в буфер обмена
            def copy_to_clipboard(self, text):
                self.FM.clipboard_clear()
                self.FM.clipboard_append(text)



            #О Программе
            def about_FM(self):
                messagebox.showinfo(random_string(), f"Файловый Менеджер {file_manager_version}\nCreated by NEO Organization\nPowered by Departament K\nCoded by @AnonimNEO\nCopyleft 🄯 NEO Organization 2024 - 2025")



            #Окно Поиска
            def open_search_dialog(self):
                #Создаем окно для диалога
                self.search_window = tk.Toplevel(self.FM)
                self.search_window.title(random_string())
                self.search_window.resizable(False, False)

                #Получаем данные текущей вкладки, чтобы определить начальный каталог
                current_data = self.get_current_tab_data()
                current_path = current_data["path"] if current_data else os.path.expanduser(default_path)

                #Переменные для хранения состояния
                self.search_text_var = tk.StringVar(self.search_window, value="")
                self.search_case_var = tk.BooleanVar(self.search_window, value=False) #С учётом регистра
                self.search_whole_word_var = tk.BooleanVar(self.search_window, value=False) #Слова целиком
                self.search_current_dir_var = tk.BooleanVar(self.search_window, value=True) #В текущем каталоге

                #Текстовое поле
                search_frame = ttk.Frame(self.search_window, padding="10 10 10 5")
                search_frame.pack(fill="x", expand=True)

                ttk.Label(search_frame, text="Текст для поиска:").pack(side="top", fill="x", pady=(0, 5))

                search_entry = ttk.Entry(search_frame, textvariable=self.search_text_var, width=50)
                search_entry.pack(side="top", fill="x", expand=True)
                search_entry.focus_set()

                #Привязываем Enter к выполнению поиска
                search_entry.bind("<Return>", lambda e: self.start_search(self.search_text_var.get()))

                #Галочки (Опции поиска)
                options_frame = ttk.Frame(self.search_window, padding="10 0 10 5")
                options_frame.pack(fill="x", pady=(0, 5))

                #Фрейм для выравнивания галочек в одну строку
                checkbox_frame = ttk.Frame(options_frame)
                checkbox_frame.pack(fill="x")

                #С учётом регистра
                ttk.Checkbutton(checkbox_frame,
                                text="с учётом регистра",
                                variable=self.search_case_var).pack(side="left", padx=5)

                #Слова целиком
                ttk.Checkbutton(checkbox_frame,
                                text="слова целиком",
                                variable=self.search_whole_word_var).pack(side="left", padx=5)

                #В текущем каталоге
                ttk.Checkbutton(checkbox_frame,
                                text="в текущем каталоге",
                                variable=self.search_current_dir_var).pack(side="left", padx=5)

                #Кнопка Поиска
                button_frame = ttk.Frame(self.search_window, padding="5 5 5 10")
                button_frame.pack(fill="x", side="bottom")

                #Добавляем разделитель для красоты
                ttk.Separator(self.search_window, orient="horizontal").pack(fill="x", padx=5)

                ttk.Button(button_frame,
                           text="Поиск",
                           command=lambda: self.start_search(self.search_text_var.get())).pack(side="right", padx=5)

                ttk.Button(button_frame,
                           text="Отмена",
                           command=self.search_window.destroy).pack(side="right")

                #Устанавливаем диалог модальным и центрируем
                self.search_window.transient(self.FM)
                self.search_window.grab_set()
                self.FM.wait_window(self.search_window)



            #Поиск
            def start_search(self, search_text):
                if not search_text:
                    messagebox.showwarning(random_string(), "Введите текст для поиска!")
                    return

                #Считываем настройки
                is_case_sensitive = self.search_case_var.get()
                is_whole_word = self.search_whole_word_var.get()
                is_single_dir = self.search_current_dir_var.get()

                #Получаем текущий путь для поиска
                data = self.get_current_tab_data()
                if not data:
                    messagebox.showerror(random_string(), "Нет активной вкладки для поиска.")
                    self.search_window.destroy()
                    return

                start_path = data["path"]

                #Закрываем окно поиска
                if self.search_window:
                    self.search_window.destroy()
                    self.search_window = None

                #Запускаем рекурсивный поиск
                messagebox.showinfo(random_string(), f"Начинаем поиск '{search_text}' в каталоге: {start_path}...")

                #Вызываем основной метод поиска
                search_results = self.recursive_search_files(
                    start_path,
                    search_text,
                    is_case_sensitive,
                    is_whole_word,
                    is_single_dir
                )

                #Обрабатываем результаты
                if not search_results:
                    messagebox.showinfo(random_string(), f'Файлы, содержащие "{search_text}"", не найдены.')
                    #Не меняем текущую вкладку
                    self.on_refresh() #Просто обновим, чтобы снять сообщение о загрузке
                    return

                #Обновляем текущую вкладку результатами
                self.show_search_results(data, search_results, start_path, search_text)



            #Рекурсивный поиск
            def recursive_search_files(self, start_path, search_text, case_sensitive, whole_word, single_dir):
                logger.info(f'FM - Начало поиска: {start_path}, Текст: "{search_text}", Одиночный каталог: {single_dir}')
                results = []

                #Подготовка поискового текста
                search_term = search_text if case_sensitive else search_text.lower()

                #Функция для проверки совпадения
                def match_criteria(name):
                    check_name = name if case_sensitive else name.lower()

                    if whole_word:
                        #Проверка на полное совпадение имени
                        return check_name == search_term
                    else:
                        #Проверка на вхождение подстроки или fnmatch (если есть *)
                        if "*" in search_text or "?" in search_text:
                            #fnmatch используется для сравнения с шаблоном
                            return fnmatch.fnmatch(name, search_text) #fnmatch сам обрабатывает регистр
                        else:
                            return search_term in check_name

                #Если ищем только в текущем каталоге, обходим только его
                if single_dir:
                    try:
                        for item_name in os.listdir(start_path):
                            if match_criteria(item_name):
                                item_path = os.path.join(start_path, item_name)
                                try:
                                    #Используем get_files_info для получения структурированной информации
                                    info = get_files_info(os.path.dirname(item_path))
                                    #Находим наш элемент в полученном списке
                                    found_item = next((i for i in info if i["path"] == item_path), None)
                                    if found_item:
                                        results.append(found_item)
                                except Exception as e:
                                    logger.warning(f"FM - Ошибка получения информации о файле/папке {item_path}:\n{e}")

                    except Exception as e:
                        logger.error(f"FM - Ошибка чтения каталога {start_path}:\n{e}")

                #Ищем рекурсивно
                else:
                    for root, dirs, files in os.walk(start_path, topdown=True):
                        #Ищем совпадения в именах каталогов
                        for dir_name in list(dirs):
                            if match_criteria(dir_name):
                                dir_path = os.path.join(root, dir_name)
                                try:
                                    #Добавляем информацию о каталоге
                                    stat = os.stat(dir_path)
                                    results.append({
                                        "name": dir_name,
                                        "path": dir_path,
                                        "size": 0,
                                        "edited": stat.st_mtime,
                                        "created": stat.st_ctime,
                                        "type": "Каталог",
                                        "is_dir": True,
                                        "ext": ""
                                    })
                                except Exception as e:
                                    logger.warning(f"FM - Ошибка получения информации о папке {dir_path}:\n{e}")

                        #Ищем совпадения в именах файлов
                        for file_name in files:
                            if match_criteria(file_name):
                                file_path = os.path.join(root, file_name)
                                try:
                                    info = get_files_info(root)
                                    found_item = next((i for i in info if i["path"] == file_path), None)
                                    if found_item:
                                        results.append(found_item)
                                except Exception as e:
                                    logger.warning(f"FM - Ошибка получения информации о файле {file_path}:\n{e}")

                logger.info(f"FM - Поиск завершен. Найдено результатов: {len(results)}")
                return results



            #Показываем результаты поиска в текущей вкладке
            def show_search_results(self, tab_data, search_results, searched_path, search_text):
                tab_id = self.get_current_tab_id()
                if not tab_id: return

                #Кэшируем результаты в отдельное поле для возможности вернуться
                tab_data["search_results"] = {
                    "path": searched_path, #Каталог, в котором искали
                    "text": search_text, #Запрос
                    "results": search_results, #Список найденных файлов/папок
                    "is_active": True #Флаг, что сейчас отображаются результаты поиска
                }

                #Обновляем историю и путь
                #Путь теперь - это наш запрос, но для отображения его храним в history
                search_display_path = f'Результаты поиска: "{search_text}" в "{searched_path}"'

                #ВАЖНО: В историю мы добавляем СПЕЦИАЛЬНУЮ СТРОКУ, которая пометит состояние поиска.
                #Это нужно, чтобы при нажатии "Назад" мы знали, что нужно ПОВТОРИТЬ ПОИСК.
                search_history_entry = f"SEARCH_RESULT:{search_text}:{searched_path}"

                if tab_data["history_index"] < len(tab_data["history"]) - 1:
                     tab_data["history"] = tab_data["history"][:tab_data["history_index"] + 1]

                tab_data["history"].append(search_history_entry)
                tab_data["history_index"] = len(tab_data["history"]) - 1

                #Временный путь для отображения
                tab_data["path"] = search_display_path

                #Перезаполняем Treeview
                tree = tab_data["tree"]
                tree.delete(*tree.get_children())

                #Для отображения в таблице используем наши результаты
                #Для сортировки мы переиспользуем поле files_info
                tab_data["files_info"] = search_results

                #Сортируем и заполняем
                self.populate_treeview(tab_data)

                #Обновляем GUI
                self.update_tab_title(tab_id, search_display_path)
                self.update_path_entry()
                self.update_toolbar_buttons()



        FM = tk.Tk()
        style = ttk.Style(FM)
        style.theme_use("clam")

        app = FileManagerApp(FM)

        #Обработка закрытия окна
        def on_closing():
            if messagebox.askokcancel(random_string(), "Вы уверены, что хотите выйти?"):
                FM.destroy()

        FM.protocol("WM_DELETE_WINDOW", on_closing)
        FM.mainloop()

    except Exception as e:
        comment = f"В FileManager произошла неизвестная ошибка!\n{e}"
        logger.critical(comment)
        messagebox.showerror(random_string(), comment)
