# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

FILE_MANAGER_VERSION = "4.11.14 Beta"

def FM(RUN_IN_RECOVERY=False, current_theme="dark", DEBUG_MODE=False):
    """Главгая функция Компонента ФайловогоМенеджера (точка входа)"""
    # Интерфейс
    from tkinter import ttk, messagebox, Menu, simpledialog
    import tkinter as tk
    # Дата и Время
    from datetime import datetime
    # Логирование
    try:
        from OF import Logger
        logger = Logger()
    except:
        from loguru import logger
    # Получение имени пользователя
    import getpass
    # Для поиска
    import threading
    import fnmatch
    # Для получения списка дисков
    import string
    # Работа с файлами
    import os.path
    import shutil
    import os

    from OF import pac, get_user_name, get_current_disc, apply_global_theme, create_menubar
    from languages import l
    from RS import RS
    from GFA import GFA
    from FE import FE

    try:
        # Получение информации о файлах и каталогах
        def get_files_info(path):
            files_info = []

            # Добавляем ".." для подъема вверх, если это не корневой каталог
            parent_dir = os.path.dirname(path)
            if path.rstrip("\\/") != parent_dir.rstrip("\\/"): # Проверка, что мы не в корневом каталоге
                try:
                    stat = os.stat(parent_dir)
                    files_info.append({
                        "name": "..",
                        "path": parent_dir,
                        "size": 0,
                        "edited": stat.st_mtime,
                        "created": stat.st_ctime,
                        "type": l("dir"),
                        "is_dir": True,
                        "ext": ""
                    })
                except:
                    logger.exception(f'FM - {l("metadata_error")}')

            # Получаем список файлов/каталогов
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    stat = os.stat(item_path)
                    is_dir = os.path.isdir(item_path)

                    # Определение типа
                    if is_dir:
                        file_type = l("dir")
                        ext = ""
                    else:
                        ext = os.path.splitext(item)[1].lower()
                        if ext:
                            file_type = f'{ext.upper()[1:]} {l("file")}'
                        else:
                            file_type = {l("file")}

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
                    # Пропускаем файлы, к которым нет доступа
                    logger.warning(f'FM - {l("skip_file")}: {item_path}\n{e}')
                    continue

            return files_info



        # Получаем доступные диски
        def get_available_disks():
            drives = []
            for drive in string.ascii_uppercase:
                if os.path.exists(drive + ":\\"):
                    drives.append(drive + ":\\")
            return drives



        # Переводим веса файла в более крупный формат
        def get_formatted_size(size):
            if not isinstance(size, (int, float)):
                return "Н/Д"

            if size == 0:
                return "" # Не показываем 0 для каталогов

            units = ["Байт", "КБ", "МБ", "ГБ", "ТБ"]
            unit_index = 0
            while size >= 1024 and unit_index < len(units) - 1:
                size /= 1024.0
                unit_index += 1
            return f"{size:.2f} {units[unit_index]}"



        # Форматируем Unix-таймштамп в читаемую строку
        def format_time(timestamp):
            if timestamp == 0:
                return ""
            try:
                return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")
            except Exception:
                return l("no_data")



        class FileManagerApp:
            def __init__(self, FM_GUI):
                self.FM_GUI = FM_GUI
                self.FM_GUI.title(RS())
                self.FM_GUI.geometry("700x400")

                self.user_name = get_user_name()

                self.key_actions = {
                    "Return": "handle_key_enter", # Enter - Открыть файл или каталог
                    "BackSpace": "on_back", # Backspace - Переход на уровень вверх
                    "Delete": "handle_key_delete", # Delete - Удалить выбранный элемент
                    "F5": "on_refresh", # F5 - Обновить
                    "F2": "handle_key_rename" # F2 - Переименовать
                }

                self.current_search_results = []
                self.search_results_lock = threading.Lock()

                # Буфер обмена для Копирования/Вырезания
                self.clipboard_data = {"path": None, "action": None}

                # Словарь для хранения состояния каждой вкладки
                self.tabs_data = {}

                # Создание верхней панели
                self.toolbar_frame = ttk.Frame(FM_GUI)
                self.toolbar_frame.pack(side="top", fill="x", padx=5, pady=(5, 0))

                self.create_toolbar_buttons()
                self.create_path_entry()

                # Создание Панели вкладок
                self.notebook = ttk.Notebook(FM_GUI)
                self.notebook.pack(side="top", fill="both", expand=True, padx=5, pady=5)
                self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

                # Создание Меню
                create_menubar(FM_GUI, RUN_IN_RECOVERY, "FM", self.open_search_dialog, DEBUG_MODE=DEBUG_MODE)

                # Добавление первой вкладки
                # При запуске предложить выбрать путь
                self.add_tab(None)

                # Фокусировка на окно
                self.FM_GUI.after(1, self.FM_GUI.focus_force)



            # Создает кнопок навигации
            def create_toolbar_buttons(self):
                button_frame = ttk.Frame(self.toolbar_frame)
                button_frame.pack(side="left")

                self.btn_back = ttk.Button(button_frame, text="←", command=self.on_back, state="disabled", width=3)
                self.btn_back.pack(side="left", padx=(0, 2))

                self.btn_forward = ttk.Button(button_frame, text="→", command=self.on_forward, state="disabled", width=3)
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



            # Поле пути к текущему каталогу
            def create_path_entry(self):
                self.path_var = tk.StringVar()
                self.path_entry = ttk.Entry(self.toolbar_frame, textvariable=self.path_var, font=("Arial", 10))
                self.path_entry.pack(side="left", fill="x", expand=True, padx=5, ipady=2)

                # При нажатии Enter обновляем путь
                self.path_entry.bind("<Return>", self.on_path_enter)

                # Контекстное меню по ПКМ
                self.path_menu = Menu(self.FM_GUI, tearoff=0)
                self.path_menu.add_command(label=l("copy_path"), command=self.copy_path_to_clipboard)
                self.path_menu.add_command(label=l("paste"), command=self.paste_from_clipboard)
                self.path_entry.bind("<Button-3>", self.show_path_context_menu)



            def add_tab(self, path=None):
                tab_frame = ttk.Frame(self.notebook, padding=5)

                # Создаем Таблицу и Скролл бар
                tree = ttk.Treeview(tab_frame, selectmode="extended", show="headings")
                vsb = ttk.Scrollbar(tab_frame, orient="vertical", command=tree.yview)
                tree.configure(yscrollcommand=vsb.set)

                vsb.pack(side="right", fill="y")
                tree.pack(side="left", fill="both", expand=True)

                # Настройка колонок таблицы и сортировки
                columns = (l("name"), l("size"), l("type"), f'{l("date")} {l("changes")}')
                tree["columns"] = columns

                col_widths = {l("name"): 300, l("size"): 100, l("type"): 120, f'{l("date")} {l("changes")}': 150}

                tree.column("# 0", width=0, stretch=tk.NO) # Убираем колонку по умолчанию

                for col in columns:
                    tree.heading(col, text=col, command=lambda c=col: self.on_tree_sort(c))
                    tree.column(col, width=col_widths.get(col, 150), anchor=tk.W if col != l("size") else tk.E)

                # Бинды для таблицы
                tree.bind("<Double-1>", self.on_tree_double_click)

                tree.bind("<Button-3>", self.on_tree_right_click)

                # Привязка обработчика клавиш
                tree.bind("<Key>", self.on_key_press)

                # Привязка универсального обработчика клавиш
                tree.bind("<Key>", self.on_key_press)

                # Привязка кнопки "Контекстное меню" (Menu)
                tree.bind("<Menu>", self.on_key_context_menu)

                # Добавляем фрейм в панель
                self.notebook.add(tab_frame, text=l("loading"))

                tab_id = str(tab_frame)

                # Сохраняем состояние вкладки
                self.tabs_data[tab_id] = {
                    "frame": tab_frame,
                    "tree": tree,
                    "vsb": vsb,
                    "path": None, # Будет установлен в load_directory
                    "files_info": [], # Кэш данных для сортировки
                    "history": [],
                    "history_index": -1,
                    "sort_col": l("name"),
                    "sort_dir": False # False = asc, True = desc
                }

                # Загружаем данные
                self.load_directory_for_tab(tab_id, path)

                # Активируем вкладку
                self.notebook.select(tab_id)

                all_item_ids = tree.get_children()
                first_item_id = all_item_ids[0]
                tree.focus(first_item_id)
                # tree.after(100, tree.focus_set)



            # Закрывает текущую вкладку
            def on_close_tab(self):
                if len(self.notebook.tabs()) <= 1:
                    return # Не даем закрыть последнюю вкладку

                selected_tab_id = self.get_current_tab_id()
                if selected_tab_id:
                    if selected_tab_id in self.tabs_data:
                        del self.tabs_data[selected_tab_id]
                    self.notebook.forget(selected_tab_id)



            # Смена вкладками
            def on_tab_changed(self, event):
                self.update_path_entry()
                self.update_toolbar_buttons()

                # Возвращаем клавиатурный фокус на таблицу
                data = self.get_current_tab_data()
                if data and data.get("tree"):
                    tree = data["tree"]
                    # Получаем ID элемента, который был в фокусе в этой вкладке
                    current_focus_id = tree.focus()

                    if current_focus_id:
                        # Если какой-то элемент уже был в фокусе, возвращаем фокус ему
                        tree.after(10, lambda: tree.focus(current_focus_id))
                    else:
                        # Если фокуса не было, то фокусируемся на первом элементе

                        all_items = tree.get_children()
                        if all_items:
                            tree.after(10, lambda: tree.focus(all_items[0]))
                        else:
                            tree.after(10, tree.focus_set)



            # Загружает данные о файлах для указанной вкладки по указанному пути
            def load_directory_for_tab(self, tab_id, path=None, is_history_nav=False):
                tab_data = self.tabs_data.get(tab_id)
                if not tab_data:
                    return

                # Если путь не передан, берем текущий из данных вкладки
                if path is None:
                    path = tab_data.get("path")

                    # Если пути всё еще нет (первый запуск), запрашиваем его
                    if RUN_IN_RECOVERY:
                        default_path = get_current_disc(RUN_IN_RECOVERY)
                        
                        # Если функция вернула кортеж, берем первый элемент
                        if isinstance(default_path, tuple) and len(default_path) > 0:
                            default_path = default_path[0]
                    else:
                        default_path = "C:\\"

                    # Получаем путь от пользователя
                    def open_enter_dialog():
                        result = {"path": None}

                        def cancel_enter_path():
                            result["path"] = None
                            path_window.destroy()

                        def ok_path():
                            result["path"] = path_text.get()
                            path_window.destroy()

                        # Создаем окно
                        path_window = tk.Toplevel(FM_GUI)
                        path_window.title(RS())
                        path_window.geometry("250x135")
                        path_window.attributes("-topmost", True)

                        # Делаем окно модальным
                        path_window.grab_set()

                        ttk.Label(path_window, text=f'{l("enter_path")}\n{l("available_disks")}: {get_available_disks()}').pack(pady=5, padx=10, anchor="w")

                        # Текстовое поле
                        path_text = tk.StringVar(value=default_path)
                        path_entry = ttk.Entry(path_window, textvariable=path_text, width=40)
                        path_entry.pack(pady=5, padx=10)
                        path_entry.focus_set()

                        button_frame = ttk.Frame(path_window)
                        button_frame.pack(pady=10)

                        ttk.Button(button_frame, text=l("cancel2"), command=cancel_enter_path).pack(side="left", padx=5)
                        ttk.Button(button_frame, text=l("ok"), command=ok_path).pack(side="left", padx=5)

                        # Привязки Enter и Esc
                        path_window.bind("<Return>", lambda e: ok_path())
                        path_window.bind("<Escape>", lambda e: cancel_enter_path())

                        # Ожидаем закрытия
                        FM_GUI.wait_window(path_window)

                        return result["path"]

                    chosen_path = open_enter_dialog()

                    if chosen_path:
                        path = chosen_path
                    else:
                        self.on_close_tab()
                        return


                if not os.path.exists(path):
                    messagebox.showerror(RS(), f'{l("path")} {l("not_found")}: {path}')
                    # Возвращаем старый путь в поле ввода, если ввели неверный
                    self.update_path_entry()
                    return

                try:
                    files_info = get_files_info(path)
                    tab_data["path"] = path
                    tab_data["files_info"] = files_info
                    
                    # Сбрасываем поиск при обычном переходе
                    if "search_results" in tab_data:
                        tab_data["search_results"]["is_active"] = False

                    # Логика истории
                    if not is_history_nav:
                        if tab_data["history_index"] < len(tab_data["history"]) - 1:
                            tab_data["history"] = tab_data["history"][:tab_data["history_index"] + 1]
                        if not tab_data["history"] or tab_data["history"][-1] != path:
                            tab_data["history"].append(path)
                            tab_data["history_index"] = len(tab_data["history"]) - 1

                    self.populate_treeview(tab_data)
                    self.update_tab_title(tab_id, path)
                    
                    # Обновляем поле пути после успешной загрузки
                    self.update_path_entry()
                    self.update_toolbar_buttons()
                except Exception as e:
                    logger.exception(f'FM - {l("permission_error")} {path}')
                    messagebox.showerror(RS(), f'{l("permission_error")}: {path}')



            # Заполняет таблицу данными
            def populate_treeview(self, tab_data):
                tree = tab_data["tree"]
                files_info = tab_data["files_info"]
                sort_col = tab_data.get("sort_col", l("name"))
                sort_dir = tab_data.get("sort_dir", False)

                tree.delete(*tree.get_children())

                sorted_files = self.sort_files(files_info, sort_col, sort_dir)

                # Заполнение таблицы
                for item in sorted_files:
                    size_str = get_formatted_size(item["size"])
                    mod_time_str = format_time(item["edited"])

                    values = (item["name"], size_str, item["type"], mod_time_str)

                    # iid (Item ID) - полный путь к файлу
                    tree.insert("", "end", iid=item["path"], values=values)

                    if item["is_dir"]:
                        tree.item(item["path"], tags=("directory",))

                tree.tag_configure("directory", foreground=current_theme["abg"])

                # Получаем список ID всех элементов в таблице
                all_item_ids = tree.get_children()

                if all_item_ids:
                    # Если список не пуст, берем ID первого элемента
                    first_item_id = all_item_ids[0]

                    # Выделяем и ставим фокус на этот элемент
                    tree.selection_set(first_item_id)
                    tree.focus(first_item_id)
                else:
                    # Если каталог пустой, просто ставим фокус на саму таблицу
                    tree.focus_set()



            # Кнопка назад "<-"
            def on_back(self):
                data = self.get_current_tab_data()
                if data and data["history_index"] > 0:
                    data["history_index"] -= 1
                    path = data["history"][data["history_index"]]
                    self.load_directory_for_tab(self.get_current_tab_id(), path, is_history_nav=True)



            # Кнопка вперёд "->"
            def on_forward(self):
                data = self.get_current_tab_data()
                if data and data["history_index"] < len(data["history"]) - 1:
                    data["history_index"] += 1
                    path = data["history"][data["history_index"]]
                    self.load_directory_for_tab(self.get_current_tab_id(), path, is_history_nav=True)



            # Кнопка вверх "↑"
            def on_up(self):
                data = self.get_current_tab_data()
                if data and data["path"]:
                    parent_path = os.path.dirname(data["path"])
                    if parent_path != data["path"]: # Проверка, что не корневой каталог
                        self.load_directory_for_tab(self.get_current_tab_id(), parent_path)



            # Кнопка обновить "↻"
            def on_refresh(self):
                data = self.get_current_tab_data()
                if data and data["path"]:
                    # Сохраняем текущий фокус перед обновлением
                    tree = data["tree"]
                    current_focus = tree.focus()
                    
                    self.load_directory_for_tab(self.get_current_tab_id(), data["path"], is_history_nav=True)
                    
                    # Восстанавливаем фокус, если элемент все еще существует
                    if current_focus and tree.exists(current_focus):
                        tree.after(50, lambda: self.focus_item_by_path(current_focus))



            # Нажатие Enter в поле пути
            def on_path_enter(self, event):
                new_path = self.path_var.get().strip()
                current_tab_id = self.get_current_tab_id()
                
                if current_tab_id and new_path:
                    # Вызываем загрузку директории для текущей вкладки
                    self.load_directory_for_tab(current_tab_id, new_path)
                    
                # Убираем фокус с поля ввода, чтобы горячие клавиши снова работали
                self.FM_GUI.focus_set()



            # Меню ПКМ
            def show_path_context_menu(self, event):
                try:
                    self.path_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.path_menu.grab_release()



            # Копируем текст в буфер обмена
            def copy_path_to_clipboard(self, all=True):
                if all:
                    self.FM_GUI.clipboard_clear()
                    self.FM_GUI.clipboard_append(self.path_var.get())
                elif not all:
                    try:
                        selected = self.path_entry.selection_get()
                        self.FM_GUI.clipboard_clear()
                        self.FM_GUI.clipboard_append(selected)
                    except tk.TclError:
                        pass # Ничего не выделено



            # Вставка из буфера обмена
            def paste_from_clipboard(self):
                try:
                    clipboard_data = self.FM_GUI.clipboard_get()
                    self.path_entry.delete(0, tk.END)
                    self.path_entry.insert(0, clipboard_data)
                except tk.TclError:
                    pass # Буфер обмена пуст



            # Обработка двойного клика
            def on_tree_double_click(self, event):
                data = self.get_current_tab_data()
                if not data: return

                tree = data["tree"]
                
                # Получаем идентификатор элемента, на котором был сделан клик
                item_id = tree.identify_row(event.y)
                
                # Если item_id пуст, значит, клик был не на элементе (возможно, на заголовке или на пустом месте)
                if not item_id:
                    # Проверяем, был ли клик на заголовке
                    region = tree.identify_region(event.x, event.y)
                    if region == "heading":
                        # Если на заголовке, то это был клик для сортировки.
                        # Прерываем обработку, чтобы не открывать выделенный элемент.
                        return

                # Если клик был на элементе
                item_id = tree.focus() # Получаем выделенный элемент (на который наведен фокус)

                if not item_id: return

                if os.path.isdir(item_id):
                    # Если это каталог, загружаем ее
                    self.load_directory_for_tab(self.get_current_tab_id(), item_id)
                elif os.path.isfile(item_id):
                    # Если это файл, открываем его
                    self.open_file(item_id)



            # меню по ПКМ
            def on_tree_right_click(self, event):
                data = self.get_current_tab_data()
                if not data: return

                tree = data["tree"]
                # Определяем, есть ли под курсором какой-то элемент
                item_under_cursor = tree.identify_row(event.y)

                # Если нажали на пустом месте
                if not item_under_cursor:
                    target_type = "directory"
                    target_path = data["path"] 
                else:
                    target_type = "item"
                    target_path = item_under_cursor

                menu = self.build_context_menu(target_type, target_path)

                try:
                    menu.tk_popup(event.x_root, event.y_root)
                finally:
                    menu.grab_release()



            # Сортировка по нажатия на заголовок столбика
            def on_tree_sort(self, col):
                data = self.get_current_tab_data()
                if not data: return
                tree = data["tree"]

                # Обновляем параметры сортировки
                if data["sort_col"] == col:
                    data["sort_dir"] = not data["sort_dir"]
                else:
                    data["sort_col"] = col
                    data["sort_dir"] = False
                reverse = data["sort_dir"]

                # Обновляем заголовки
                for c in tree["columns"]:
                    tree.heading(c, text=c)
                arrow = " ▼" if reverse else " ▲"
                tree.heading(col, text=col + arrow)

                # Перезаполняем таблицу с новой сортировкой
                self.populate_treeview(data)




            # Обработка сочетаний клавиш
            def on_key_press(self, event):
                keysym = event.keysym

                # Получаем данные текущей вкладки
                data = self.get_current_tab_data()

                # Проверяем, активно ли состояние поиска
                is_search_active = (data and
                                    data.get("search_results") and
                                    data["search_results"].get("is_active"))

                if keysym == "BackSpace" and is_search_active:
                    # Если активен поиск и нажата Backspace, принудительно вызываем "Назад"
                    self.on_back()
                    return "break" # Останавливаем дальнейшую обработку клавиши

                shift_mask = 0x0001
                ctrl_mask = 0x0004 # Control

                is_ctrl_pressed = (event.state & ctrl_mask) != 0

                if is_ctrl_pressed:
                    if keysym == "n":
                        is_shift_pressed = (event.state & shift_mask) != 0
                        if is_shift_pressed:
                            # Ctrl + Shift + N
                            self.action_in_path("create_path")
                        else:
                            # Ctrl + N
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
                    # Если для этой клавиши есть действие, получаем сам метод по его имени
                    action_method = getattr(self, action_name, None)

                    if action_method:
                        # Выполняем метод
                        if action_name == "handle_key_rename":
                            self.action_in_path("rename")
                        else:
                            action_method()

                        return "break"



            # Кнопка Enter
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



            # Вспомогательный метод для получения всех выделенных путей
            def get_selected_items_paths(self):
                data = self.get_current_tab_data()
                if not data: return []
                tree = data["tree"]
                return list(tree.selection())



            # Удаляем элемент
            def handle_key_delete(self):
                selected_paths = self.get_selected_items_paths()
                if not selected_paths: return

                paths_to_delete = [p for p in selected_paths if not p.endswith("..")]
                if not paths_to_delete: return

                count = len(paths_to_delete)

                if not messagebox.askyesno(RS(), f'{l("you_want_to_delete")} {count} {l("elements")}?' if count > 1 else f'{l("delete")} "{os.path.basename(paths_to_delete[0])}"?'):
                    return

                # Получаем текущую таблицу и данные
                data = self.get_current_tab_data()
                if not data:
                    return

                tree = data["tree"]

                # Находим все элементы в таблице (кроме удаляемых)
                all_items = tree.get_children()

                # Берем элемент, следующий за последним удаляемым, или предыдущий
                focus_target = None

                if all_items:
                    # Сортируем индексы удаляемых элементов
                    delete_indices = []
                    for path in paths_to_delete:
                        try:
                            idx = all_items.index(path)
                            delete_indices.append(idx)
                        except ValueError:
                            pass

                    if delete_indices:
                        max_delete_idx = max(delete_indices)
                        min_delete_idx = min(delete_indices)

                        # Пытаемся найти элемент после удаляемых
                        for idx in range(max_delete_idx + 1, len(all_items)):
                            if all_items[idx] not in paths_to_delete:
                                focus_target = all_items[idx]
                                break

                        # Если нет элемента после, берем элемент перед удаляемыми
                        if focus_target is None:
                            for idx in range(min_delete_idx - 1, -1, -1):
                                if all_items[idx] not in paths_to_delete:
                                    focus_target = all_items[idx]
                                    break

                # Удаляем файлы
                for path in paths_to_delete:
                    try:
                        try:
                            GFA(path, RUN_IN_RECOVERY)
                            print(2)
                        except:
                            print(1)
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                    except Exception as e:
                        logger.exception(f'FM - {l("delete_error")} {path}')
                        messagebox.showerror(RS(), f'{l("delete_error")} {os.path.basename(path)}:\n{e}')

                # Обновляем и восстанавливаем фокус
                self.on_refresh()

                # Восстанавливаем фокус после обновления
                if focus_target:
                    tree.after(100, lambda: self.focus_item_by_path(focus_target))




            def handle_copy(self):
                selected_paths = self.get_selected_items_paths()
                paths = [p for p in selected_paths if not p.endswith("..")]
                if not paths: return
                
                self.clipboard_data = {"paths": paths, "action": "copy"}
                if DEBUG_MODE:
                    logger.info(f'FM - {l("elements_copy")}: {len(paths)}')



            def handle_cut(self):
                selected_paths = self.get_selected_items_paths()
                paths = [p for p in selected_paths if not p.endswith("..")]
                if not paths: return

                self.clipboard_data = {"paths": paths, "action": "cut"}
                if DEBUG_MODE:
                    logger.info(f"FM - Вырезано элементов: {len(paths)}")



            def handle_paste(self):
                if "paths" not in self.clipboard_data or not self.clipboard_data["paths"]:
                    messagebox.showinfo(RS(), l("clipboard_is_empty"))
                    return

                src_paths = self.clipboard_data["paths"]
                action = self.clipboard_data["action"]
                data = self.get_current_tab_data()
                if not data or not data["path"]: return
                
                dest_dir = data["path"]

                for src_path in src_paths:
                    if not os.path.exists(src_path): continue
                    
                    dest_path = os.path.join(dest_dir, os.path.basename(src_path))
                    
                    # Проверка на копирование в самого себя
                    if os.path.normpath(src_path) == os.path.normpath(dest_path):
                        continue

                    try:
                        if action == "copy":
                            if os.path.isdir(src_path):
                                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                            else:
                                shutil.copy2(src_path, dest_path)
                        elif action == "cut":
                            shutil.move(src_path, dest_path)
                    except:
                        logger.exception(f'FM - {l("paste_error")} {src_path}')

                if action == "cut":
                    self.clipboard_data = {"paths": [], "action": None}

                self.on_refresh()



            # Получаем путь к выделенному файлу
            def get_focused_item_path(self):
                data = self.get_current_tab_data()
                if not data: return None
                tree = data["tree"]
                item_id = tree.focus()
                return item_id



            # Получаем автора файла
            def get_author_and_version_file(self, path):
                if os.path.isdir(path):
                    return f'{l("no_data")} ({l("dir")})'

                version = l("no_data")
                author = l("no_data")

                try:
                    # Получаем информацию о версии файла
                    fixed_info = win32api.GetFileVersionInfo(path, "\\")
                    if fixed_info:
                        ms = fixed_info["FileVersionMS"]
                        ls = fixed_info["FileVersionLS"]
                        version = (
                            f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}."
                            f"{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                        )

                    # Получаем язык и кодировку
                    lang, codepage = win32api.GetFileVersionInfo(path, "\\VarFileInfo\\Translation")[0]

                    # Формируем путь к строковым данным
                    str_info_path = f"\\StringFileInfo\\{lang:04x}{codepage:04x}\\"

                    # Пробуем получить разные поля, которые могут содержать "Автора"
                    author_keys = ["LegalCopyright", "CompanyName", "InternalName", "FileDescription"]

                    for key in author_keys:
                        try:
                            author_try = win32api.GetFileVersionInfo(path, str_info_path + key)
                            if author_try:
                                author = author_try
                                break # Нашли первое непустое значение
                        except Exception:
                            continue # Ключ не найден, пробуем следующий

                except:
                    pass

                return version, author



            # Проверяет права доступа и возвращает Да или Нет
            def get_access_string(self, path, access_type):
                try:
                    # os.access проверяет права текущего пользователя
                    if os.access(path, access_type):
                        return l("yse")
                    else:
                        return l("no")
                except:
                    logger.exception(f'FM - {l("access_check_error_for")} {path}')
                    return l("error")



            # Свойства файла
            def show_properties(self):
                item_path = self.get_focused_item_path()

                # Не показываем свойства для ".." (вверх)
                if not item_path or item_path.endswith(".."):
                    return

                # Создаём окно свойств
                prop_win = tk.Toplevel(self.FM_GUI)
                prop_win.title(f'{l("properties")}: {os.path.basename(item_path)}')
                prop_win.geometry("350x450")
                prop_win.transient(self.FM_GUI) # Связываем с главным окном
                prop_win.grab_set() # Делаем окно модальным
                prop_win.resizable(True, True) # Разрешим менять размер

                # Создаем главный фрейм с отступами
                main_frame = ttk.Frame(prop_win, padding=(10, 10, 10, 10))
                main_frame.pack(fill="both", expand=True)

                # Фрейм для таблицы и скроллбара
                tree_frame = ttk.Frame(main_frame)
                tree_frame.pack(fill="both", expand=True)

                # Создаем Таблицу
                tree = ttk.Treeview(tree_frame, columns=("param", "value"), show="headings", selectmode="none")
                vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
                tree.configure(yscrollcommand=vsb.set)

                tree.heading("param", text=l("parameter"), anchor=tk.W)
                tree.heading("value", text=l("meaning"), anchor=tk.W)
                # Колонка "Параметр" - фиксированная, "Значение" - растягивается
                tree.column("param", width=150, stretch=False, anchor=tk.W)
                tree.column("value", width=350, stretch=True, anchor=tk.W)

                vsb.pack(side="right", fill="y")
                tree.pack(side="left", fill="both", expand=True)

                # Сбор информации
                properties_data = []
                try:
                    # Стандартная информация
                    stat = os.stat(item_path)
                    file_name = os.path.basename(item_path)
                    file_path = os.path.dirname(item_path)
                    file_size_bytes = stat.st_size

                    # Используем функцию форматирования
                    file_size_formatted = get_formatted_size(file_size_bytes)

                    created = format_time(stat.st_ctime) # Создан
                    edited = format_time(stat.st_mtime) # Изменен
                    accessed = format_time(stat.st_atime) # Открыт

                    # специфичная информация
                    version, author = self.get_author_and_version_file(item_path)

                    # Права доступа
                    acc_read = self.get_access_string(item_path, os.R_OK)
                    acc_write = self.get_access_string(item_path, os.W_OK)
                    acc_exec = self.get_access_string(item_path, os.X_OK)

                    acc_modify = acc_write

                    acc_full = "Да" if (acc_read == l("yes") and acc_write == l("yes") and acc_exec == l("yes")) else l("no")

                    # Формируем список для вывода
                    # Используем "---" как разделитель
                    properties_data = [
                        (l("name"), file_name),
                        (l("location"), file_path),
                        (l("size"), file_size_formatted),
                        ("---", "---"),
                        (l("created"), created),
                        (l("changed"), edited),
                        (l("opened"), accessed),
                        ("---", "---"),
                        (l("file_version"), version),
                        (l("author"), author),
                        ("---", "---"),
                        (f'{l("access_for")} " + self.user_name + "):", "'),
                        (l("full_access"), acc_full),
                        (l("reading"), acc_read),
                        (l("changed"), acc_modify),
                        (l("record"), acc_write),
                        (l("launch"), acc_exec),
                    ]

                except:
                    logger.exception(f'FM - {l("collecting_properties_error")} {item_path}')
                    tree.insert("", "end", values=(l("error"), f'{l("read_file_properties_error")}:\n{e}'))
                    properties_data = []

                # Заполнение таблицы
                tree.tag_configure("separator")
                tree.tag_configure("header")

                for param, value in properties_data:
                    if param == "---":
                        # Вставляем пустую строку для разделения
                        item = tree.insert("", "end", values=("", ""), tags=("separator",))
                        tree.item(item, values=("", "")) # Очищаем значения
                    elif value == "":
                        # Это заголовок
                        tree.insert("", "end", values=(param, ""), tags=("header",))
                    else:
                        tree.insert("", "end", values=(param, value))

                # Кнопка OK
                ok_button = ttk.Button(main_frame, text="OK", command=prop_win.destroy, width=15)
                ok_button.pack(side="right", pady=(10, 0)) # Отступ сверху

                # Устанавливаем фокус на кнопку OK, чтобы Enter ее нажимал
                ok_button.after(100, ok_button.focus_set)

                # Привязываем <Return> (Enter) и <Escape> к закрытию окна
                prop_win.bind("<Return>", lambda e: prop_win.destroy())
                prop_win.bind("<Escape>", lambda e: prop_win.destroy())



            # Запрашиваем данные или имя
            def ask_for_name(self, title, prompt, initial_value=""):
                new_name = simpledialog.askstring(
                    title,
                    prompt,
                    initialvalue=initial_value,
                    parent=self.FM_GUI
                )

                if new_name is None: # Пользователь нажал "Отмена"
                    return None

                if not new_name.strip():
                    messagebox.showwarning(RS(), f'{l("name")} {l("not_empty")}', parent=self.FM_GUI)
                    return None

                # Проверка на недопустимые символы
                invalid_chars = '<>:"/\\|?*'
                if any(char in new_name for char in invalid_chars):
                    messagebox.showwarning(RS(), f'{l("name")} {l("invalid_characters")}:\n{invalid_chars}', parent=self.FM_GUI)
                    return None

                return new_name



            # Действие с файлами и каталогами
            def action_in_path(self, action):
                data = self.get_current_tab_data()
                if not data: return

                tree = data["tree"]
                
                # Для создания (create_path, create_file) работаем с текущим каталогом
                if action in ["create_path", "create_file"]:
                    current_dir = data["path"]
                    old_name = l("dir") if action == "create_path" else {l("file")}
                    old_path = None # Нет старого пути для создания
                else: # Для переименования
                    old_path = self.get_focused_item_path()

                    if not old_path or old_path.endswith(".."):
                        return # Нельзя переименовать ".." (вверх)

                    old_name = os.path.basename(old_path)
                    current_dir = os.path.dirname(old_path)

                # Проверяем, что текущий каталог существует
                if not os.path.isdir(current_dir):
                    messagebox.showerror(RS(), f'{l("current")} {l("dir")} {l("not_found")}: {current_dir}', parent=self.FM_GUI)
                    return

                new_name = self.ask_for_name(RS(), f'{l("new_name_for")}:\n{old_name}', initial_value=old_name)

                if new_name is None:
                    return # Отмена

                if action == "rename" and new_name == old_name:
                    return # Имя не изменилось

                new_path = os.path.join(current_dir, new_name)

                comment = f'{l("name_file_or_dir")} "{new_name}" {l("already_exists")}'
                if action != "rename" and os.path.exists(new_path):
                    messagebox.showerror(RS(), comment, parent=self.FM_GUI)
                    return
                elif action == "rename" and old_path != new_path and os.path.exists(new_path):
                    messagebox.showerror(RS(), comment, parent=self.FM_GUI)
                    return

                if action == "rename":
                    try:
                        os.rename(old_path, new_path)
                        logger.info(f'FM - {l("renamed")}: {old_path} -> {new_path}')
                        self.on_refresh()

                        # Пытаемся восстановить фокус на переименованном файле
                        tree.after(100, lambda: self.focus_item_by_path(new_path))

                    except Exception as e:
                        logger.exception(f'FM - {l("error")} {l("when_renaming")}')
                        messagebox.showerror(RS(), f'{l("error")} {l("when_renaming")}:\n{e}', parent=self.FM_GUI)

                elif action == "create_path":
                    try:
                        os.mkdir(new_path)
                        logger.info(f'FM - {l("created")} {l("dir")}: {new_path}')
                        self.on_refresh()
                    except Exception as e:
                        logger.exception(f'FM - {l("create_dir_error")}')
                        messagebox.showerror(RS(), f'{l("create_dir_error")}:\n{e}', parent=self.FM_GUI)

                elif action == "create_file":
                    # Запрос содержимого
                    content = simpledialog.askstring(RS(), f'{l("enter_data_file")}:\n{new_name}', parent=self.FM_GUI)

                    # Если пользователь нажал Отмена или не ввел содержимое
                    if content is None:
                         return 

                    try:
                        with open(new_path, "w") as new_file:
                            new_file.write(content)

                        logger.info(f'FM - {l("create_file")}:\n{new_path}')
                        self.on_refresh()
                    except Exception as e:
                        logger.exception(f'FM - {l("create_file_error")}')
                        messagebox.showerror(RS(), f'{l("create_file_error")}:\n{e}', parent=self.FM_GUI)



            # Устанавливаем фокус на элемент
            def focus_item_by_path(self, item_path):
                try:
                    data = self.get_current_tab_data()
                    if not data or not data.get("tree"): return

                    tree = data["tree"]
                    if tree.exists(item_path):
                        tree.selection_set(item_path)
                        tree.focus(item_path)
                        tree.see(item_path) # Прокрутить до элемента
                except:
                    logger.exception(f'FM - {l("restore_focus_error")} {item_path}')



            # Создание Контекстного меню
            def build_context_menu(self, target_type, target_path):
                menu = tk.Menu(self.FM_GUI, tearoff=0)
                data = self.get_current_tab_data()

                # Общие состояния
                paste_state = "normal" if self.clipboard_data["path"] else "disabled"

                if target_type == "item":
                    # Меню для Элемента
                    is_dir = os.path.isdir(target_path)
                    is_dotdot = target_path.endswith("..")
                    item_state = "disabled" if is_dotdot else "normal"

                    # Открыть и Вверх
                    if is_dotdot:
                        menu.add_command(label=l("up"), accelerator="Backspace", command=self.on_up)
                    elif is_dir:
                        # Используем lambda для отложенного вызова
                        menu.add_command(label=l("open"), accelerator="Enter", command=lambda: self.load_directory_for_tab(self.get_current_tab_id(), target_path))
                    else:
                        menu.add_command(label=l("open"), accelerator="Enter", command=lambda: self.open_file(target_path))

                    menu.add_separator()

                    # Вырезать, копировать, вставить
                    menu.add_command(label=l("cut"), accelerator="Ctrl+X",
                                     command=self.handle_cut, state=item_state)
                    menu.add_command(label=l("copy"), accelerator="Ctrl+C",
                                     command=self.handle_copy, state=item_state)
                    menu.add_command(label=l("paste"), accelerator="Ctrl+V",
                                     command=self.handle_paste, state=paste_state)

                    menu.add_separator()

                    # Переименовать и Удалить
                    menu.add_command(label=l("rename"), accelerator="F2",
                                     command=lambda: self.action_in_path("rename"), state=item_state)
                    menu.add_command(label=l("delete"), accelerator="Delete",
                                     command=self.handle_key_delete, state=item_state)

                    menu.add_separator()

                    # Полные права и редактор
                    menu.add_command(label=l("get_full_access"), command=lambda:GFA(self.get_focused_item_path(), RUN_IN_RECOVERY))
                    menu.add_command(label=l("edit_file"), command=lambda:FE(self.get_focused_item_path()))

                    # Создать
                    sub_menu_create = tk.Menu(menu, tearoff=0)
                    sub_menu_create.add_command(label=l("dir"), accelerator="Ctrl+Shift+N",
                                                command=lambda: self.action_in_path("create_path"))
                    sub_menu_create.add_command(label=l("file"), accelerator="Ctrl+N",
                                                command=lambda: self.action_in_path("create_file"))
                    menu.add_cascade(label=l("create"), menu=sub_menu_create)

                    menu.add_separator()

                    # Свойства
                    menu.add_command(label=l("properties"), accelerator="Ctrl+I",
                                     command=self.show_properties, state=item_state)

                    # Копировать данные
                    menu.add_command(label=l("copy_path"), command=lambda: self.copy_to_clipboard(target_path))
                    menu.add_command(label=f'{l("copy")} {l("name")}', command=lambda: self.copy_to_clipboard(os.path.basename(target_path)))

                elif target_type == "directory":
                    # Меню для Каталога (пустого места)
                    current_dir_path = target_path

                    # Создать
                    sub_menu_create = tk.Menu(menu, tearoff=0)
                    sub_menu_create.add_command(label=l("dir"), accelerator="Ctrl+Shift+N",
                                                command=lambda: self.action_in_path("create_path"))
                    sub_menu_create.add_command(label=l("file"), accelerator="Ctrl+N",
                                                command=lambda: self.action_in_path("create_file"))
                    menu.add_cascade(label=l("create"), menu=sub_menu_create)

                    menu.add_separator()

                    # Вставить и Обновить
                    menu.add_command(label=l("paste"), accelerator="Ctrl+V",
                                     command=self.handle_paste, state=paste_state)
                    menu.add_command(label=l("update"), accelerator="F5", command=self.on_refresh)

                    menu.add_separator()

                    # Копировать путь
                    menu.add_command(label=l("copy_path"), command=lambda: self.copy_to_clipboard(current_dir_path))

                return menu



            # Обработчик клавиш
            def on_key_context_menu(self, event):
                data = self.get_current_tab_data()
                if not data: return "break"

                tree = data["tree"]

                # Проверяем, нажат ли Ctrl
                ctrl_mask = 0x0004
                is_ctrl_pressed = (event.state & ctrl_mask) != 0

                x, y = 0, 0
                target_type = ""
                target_path = ""

                if is_ctrl_pressed:
                    # Меню для каталога (Ctrl + Menu)
                    target_type = "directory"
                    target_path = data["path"]
                    # Координаты: верхний левый угол таблицы
                    x = tree.winfo_rootx() + 10
                    y = tree.winfo_rooty() + 10
                else:
                    # Меню для элемента
                    target_type = "item"
                    target_path = self.get_focused_item_path()

                    if not target_path: # Ничего не выбрано
                        return "break"

                    # Координаты: под выбранным элементом
                    bbox = tree.bbox(target_path)
                    if not bbox: # Элемент не виден (например, прокручен)
                        # Просто покажем в углу
                        x = tree.winfo_rootx() + 10
                        y = tree.winfo_rooty() + 10
                    else:
                        x = tree.winfo_rootx() + bbox[0]
                        y = tree.winfo_rooty() + bbox[1] + bbox[3]

                # Создаём меню
                menu = self.build_context_menu(target_type, target_path)

                # Сохраняем ссылку на меню, чтобы отследить закрытие
                self.active_context_menu = menu

                # Привязываем событие <Unmap> (скрытие/закрытие) для очистки
                menu.bind("<Unmap>", self.on_context_menu_close, add="+")

                # Устанавливаем фокус на само меню
                menu.focus_set()

                try:
                    # Показываем меню
                    menu.tk_popup(x, y)
                finally:
                    menu.grab_release()

                return "break" # Прерываем дальнейшую обработку события



            # Возвращаем фокус на таблицу при закрытии меню
            def on_context_menu_close(self, event):
                if self.active_context_menu:
                    try:
                        # Отвязываем, чтобы избежать повторных вызовов
                        self.active_context_menu.unbind("<Unmap>")
                    except tk.TclError:
                        pass # Меню уже может быть уничтожено
                    self.active_context_menu = None



            # Копируем путь в буфер обмена
            def handle_copy(self):
                item_path = self.get_focused_item_path()
                if not item_path or item_path.endswith(".."):
                    return
                self.clipboard_data = {"path": item_path, "action": "copy"}
                if DEBUG_MODE:
                    logger.info(f"FM - Скопировано: {item_path}")



            # Помещаем объект в буфер обмена программы
            def handle_cut(self):
                item_path = self.get_focused_item_path()
                if not item_path or item_path.endswith(".."):
                    return
                self.clipboard_data = {"path": item_path, "action": "cut"}
                if DEBUG_MODE:
                    logger.info(f"FM - Вырезано: {item_path}")



            # Вставляем объект из буфера программы
            def handle_paste(self):
                if not self.clipboard_data["path"]:
                    messagebox.info(RS(), l("clipboard_is_empty"))
                    return

                src_path = self.clipboard_data["path"]
                action = self.clipboard_data["action"]

                data = self.get_current_tab_data()
                if not data or not data["path"]:
                    messagebox.info(RS(), l("not_dir_selected"))
                    return # Некуда вставлять

                dest_dir = data["path"]
                dest_path = os.path.join(dest_dir, os.path.basename(src_path))

                # Проверка, что источник все еще существует
                if not os.path.exists(src_path):
                    messagebox.showerror(RS(), f'{l("source_file_not_found")}:\n{src_path}')
                    self.clipboard_data = {"path": None, "action": None} # Очистить буфер
                    return

                # Защита от вставки в самого себя
                if os.path.normpath(src_path) == os.path.normpath(dest_path) or \
                   (os.path.isdir(src_path) and os.path.normpath(dest_dir).startswith(os.path.normpath(src_path))):
                    messagebox.showerror(RS(), l("dont_copy_in_in"))
                    return

                # Логика конфликта (Заменить или Пропустить)
                if os.path.exists(dest_path):
                    choice = messagebox.askquestion(RS(), f'{l("file")} "{os.path.basename(dest_path)}" {l("already_exists")}.\n\n{l("replace_it")}', icon="warning", type="yesno")

                    if choice == "no": # no означает пропустить
                        return
                    else: # yes означает заменить
                        try:
                            if os.path.isdir(dest_path):
                                shutil.rmtree(dest_path)
                            else:
                                os.remove(dest_path)
                        except Exception as e:
                            logger.exception(f'FM - {l("replace_file_not_found")}')
                            messagebox.showerror(RS(), f'{l("replace_file_not_found")}:\n{e}')
                            return

                # Выполнение действия (Копирование или Перемещение)
                try:
                    if action == "copy":
                        if os.path.isdir(src_path):
                            shutil.copytree(src_path, dest_path)
                        else:
                            shutil.copy2(src_path, dest_path)
                        logger.info(f'FM - {src_path} {l("copied2")} {l("in")} {dest_path}')

                    elif action == "cut":
                        shutil.move(src_path, dest_path)
                        logger.info(f"FM - Перемещён {src_path} в {dest_path}")
                        # Очищаем буфер после успешного перемещения
                        self.clipboard_data = {"path": None, "action": None}

                except Exception as e:
                    logger.exception(f'FM - {l("paste_error")}')
                    messagebox.showerror(RS(), f'{l("paste_error")} {action}:\n{e}')

                self.on_refresh()



            # Вызывает диалог переименования для выделенного элемента
            def handle_key_rename(self):
                pass



            # Получаем ID текущей вкладки
            def get_current_tab_id(self):
                try:
                    return self.notebook.select()
                except tk.TclError:
                    return None # Нет вкладок



            # Данные для текущей вкладки
            def get_current_tab_data(self):
                tab_id = self.get_current_tab_id()
                if tab_id:
                    return self.tabs_data.get(tab_id)
                return None



            # Обновляет заголовок вкладки
            def update_tab_title(self, tab_id, path):
                name = os.path.basename(path)
                if not name: # Случай корня (C:\)
                    name = path.replace("\\", "").replace("/", "")

                if len(name) > 10:
                    title = name[:10] + "..."
                else:
                    title = name

                self.notebook.tab(tab_id, text=title)



            # Обновляем поле пути
            def update_path_entry(self):
                data = self.get_current_tab_data()
                if data and "path" in data:
                    self.path_var.set(data["path"])
                    # Прокручиваем текст в конец, чтобы видеть текущий каталог
                    self.path_entry.xview_moveto(1)
                else:
                    self.path_var.set("")



            # Обновление статусов доступности кнопок навигации
            def update_toolbar_buttons(self):
                data = self.get_current_tab_data()
                if data and data["path"]:
                    # История
                    self.btn_back.config(state="normal" if data["history_index"] > 0 else "disabled")
                    self.btn_forward.config(state="normal" if data["history_index"] < len(data["history"]) - 1 else "disabled")

                    # Кнопка "Вверх"
                    parent_path = os.path.dirname(data["path"])
                    self.btn_up.config(state="normal" if parent_path != data["path"] else "disabled")

                    self.btn_refresh.config(state="normal")
                else:
                    # Нет вкладок
                    self.btn_back.config(state="disabled")
                    self.btn_forward.config(state="disabled")
                    self.btn_up.config(state="disabled")
                    self.btn_refresh.config(state="disabled")



            # Сортировка таблицы
            def sort_files(self, files_list, col, reverse):
                def get_sort_key(item):
                    # Сначала всегда папки (и ".."), потом файлы
                    # ".." всегда в самом верху
                    if item["name"] == "..":
                        sort_group = -1
                    elif item["is_dir"]:
                        sort_group = 0
                    else:
                        sort_group = 1

                    # Ключ сортировки в зависимости от колонки
                    if col == l("name"):
                        key = item["name"].lower()
                    elif col == l("size"):
                        key = item["size"]
                    elif col == l("type"):
                        key = item["type"]
                    elif col == f'{l("date")} {l("changes")}':
                        key = item["edited"]
                    else:
                        key = item["name"].lower()

                    return (sort_group, key) # Сортируем по группе, затем по ключу

                return sorted(files_list, key=get_sort_key, reverse=reverse)



            # Открываем файл
            def open_file(self, file_path):
                try:
                    os.startfile(file_path)
                except Exception as e:
                    logger.exception(f'FM - {l("open_file_error")} {file_path}')
                    messagebox.showerror(RS(), f'{l("open_file_error")}:\n{e}')



            # Копируем текст в буфер обмена
            def copy_to_clipboard(self, text):
                self.FM_GUI.clipboard_clear()
                self.FM_GUI.clipboard_append(text)



            # Окно Поиска
            def open_search_dialog(self):
                # Создаем окно для диалога
                self.search_window = tk.Toplevel(self.FM_GUI)
                self.search_window.title(RS())
                self.search_window.resizable(False, False)

                # Переменные для хранения состояния
                self.search_text_var = tk.StringVar(self.search_window, value="")
                self.search_case_var = tk.BooleanVar(self.search_window, value=False) # С учётом регистра
                self.search_whole_word_var = tk.BooleanVar(self.search_window, value=False) # Слова целиком
                self.search_current_dir_var = tk.BooleanVar(self.search_window, value=True) # В текущем каталоге

                # Текстовое поле
                search_frame = ttk.Frame(self.search_window, padding="10 10 10 5")
                search_frame.pack(fill="x", expand=True)

                ttk.Label(search_frame, text=l("text_for_search")).pack(side="top", fill="x", pady=(0, 5))

                search_entry = ttk.Entry(search_frame, textvariable=self.search_text_var, width=50)
                search_entry.pack(side="top", fill="x", expand=True)
                search_entry.focus_set()

                # Привязываем Enter к выполнению поиска
                search_entry.bind("<Return>", lambda e: self.start_search(self.search_text_var.get()))

                # Галочки (Опции поиска)
                options_frame = ttk.Frame(self.search_window, padding="10 0 10 5")
                options_frame.pack(fill="x", pady=(0, 5))

                # Фрейм для выравнивания галочек в одну строку
                checkbox_frame = ttk.Frame(options_frame)
                checkbox_frame.pack(fill="x")

                # С учётом регистра
                ttk.Checkbutton(checkbox_frame,
                                text=l("match_case"),
                                variable=self.search_case_var).pack(side="left", padx=5)

                # Слова целиком
                ttk.Checkbutton(checkbox_frame,
                                text=l("whole_words"),
                                variable=self.search_whole_word_var).pack(side="left", padx=5)

                # В текущем каталоге
                ttk.Checkbutton(checkbox_frame,
                                text=l("in_current_dir"),
                                variable=self.search_current_dir_var).pack(side="left", padx=5)

                # Кнопка Поиска
                button_frame = ttk.Frame(self.search_window, padding="5 5 5 10")
                button_frame.pack(fill="x", side="bottom")

                # Добавляем разделитель для красоты
                ttk.Separator(self.search_window, orient="horizontal").pack(fill="x", padx=5)

                ttk.Button(button_frame,
                           text=l("search"),
                           command=lambda: self.start_search(self.search_text_var.get())).pack(side="right", padx=5)

                ttk.Button(button_frame,
                           text=l("cancel2"),
                           command=self.search_window.destroy).pack(side="right")

                # Устанавливаем диалог модальным и центрируем
                self.search_window.transient(self.FM_GUI)
                self.search_window.grab_set()
                self.FM_GUI.wait_window(self.search_window)



            # Поиск
            def start_search(self, search_text):
                if not search_text:
                    messagebox.showwarning(RS(), l("enter_text_for_search"))
                    return

                # Получаем данные текущей вкладки для определения начального пути
                data = self.get_current_tab_data()
                if not data:
                    messagebox.showerror(RS(), l("not_current_tab_for_search"))
                    if self.search_window:
                        self.search_window.destroy()
                    return

                start_path = data["path"]

                # Очищаем предыдущие результаты поиска, если они были
                self.current_search_results = []
                self.search_results_lock = threading.Lock() # Создаем новый лок для каждого поиска

                # Очищаем таблицу перед началом нового поиска
                tree = data["tree"]
                tree.delete(*tree.get_children())

                # Считываем настройки
                is_case_sensitive = self.search_case_var.get()
                is_whole_word = self.search_whole_word_var.get()
                is_single_dir = self.search_current_dir_var.get()

                # Закрываем окно поиска
                if self.search_window:
                    self.search_window.destroy()
                    self.search_window = None

                # Запускаем поиск в отдельном потоке
                search_thread = threading.Thread(
                    target=self.search_in_thread,
                    args=(start_path, search_text, is_case_sensitive, is_whole_word, is_single_dir, data),
                    daemon=True
                )
                search_thread.start()

                # Обновляем заголовок вкладки, чтобы показать, что идет поиск
                tab_id = self.get_current_tab_id()
                if tab_id:
                    self.notebook.tab(tab_id, text=l("search"))

                # Сообщаем пользователю, что поиск начался
                messagebox.showinfo(RS(), l("fm_search_text"))



            # Обрабатывает поиск, подгружая результаты по мере их нахождения
            def search_in_thread(self, start_path, search_text, is_case_sensitive, is_whole_word, is_single_dir, data):
                try:
                    # Получаем генератор результатов поиска
                    generator = self.recursive_search_files(start_path, search_text, is_case_sensitive, is_whole_word, is_single_dir)

                    # Итерируемся по результатам и добавляем их в таблицу постепенно
                    for item in generator:
                        with self.search_results_lock:
                            self.current_search_results.append(item)
                        # Используем FM_GUI.after для безопасного обновления GUI из другого потока
                        self.FM_GUI.after(0, self.add_search_result_to_table, item)

                except Exception as e:
                    logger.exception(f'FM - {l("search_error")}')
                    self.FM_GUI.after(0, lambda err=e: messagebox.showerror(RS(), f'{l("search_error")}: {str(err)}'))
                finally:
                    # После завершения поиска, финализируем его
                    self.FM_GUI.after(0, lambda: self.finalize_search(data, start_path, search_text))
                    self.FM_GUI.after(0, lambda: messagebox.showinfo(RS(), l("search_completed")))

            # Сортируем результаты и обновляет таюлицу
            def finalize_search(self, data, start_path, search_text):
                tab_id = self.get_current_tab_id()
                if not tab_id:
                    return

                # Используем FM_GUI.after для безопасного обновления GUI из другого потока
                self.FM_GUI.after(0, self._finalize_search_gui, tab_id, data, start_path, search_text)



            def _finalize_search_gui(self, tab_id, data, start_path, search_text):
                try:
                    # Получаем все собранные результаты поиска
                    with self.search_results_lock:
                        search_results = self.current_search_results.copy()

                    data["sort_col"] = l("name")
                    data["sort_dir"] = False

                    # Функции повтор поиска не работают.
                    # Создаем специальную строку для пути и истории поиска
                    search_display_path = f'{l("search_result")}: "{search_text}" {l("in")} "{start_path}"'
                    # search_history_entry = f"SEARCH_RESULT:{search_text}:{start_path}"

                    # Обновляем историю навигации
                    if data["history_index"] < len(data["history"]) - 1:
                        data["history"] = data["history"][:data["history_index"] + 1]
                    # data["history"].append(search_history_entry)
                    data["history_index"] = len(data["history"]) - 1

                    # Устанавливаем путь для отображения
                    data["path"] = search_display_path

                    # Сохраняем результаты поиска для сортировки
                    data["files_info"] = search_results

                    # Сортируем и заполняем таблицу
                    self.populate_treeview(data)

                    # Обновляем GUI
                    self.update_tab_title(tab_id, search_display_path)
                    self.update_path_entry()
                    self.update_toolbar_buttons()

                    # Сбрасываем состояние поиска
                    if "search_results" in data:
                        data["search_results"]["is_active"] = False

                except Exception as e:
                    logger.exception(f'FM - {l("search_error")}')
                    messagebox.showerror(RS(), f'{l("search_error")}:\n{e}')



            # Добавляет один результат в таблицу
            def add_search_result_to_table(self, item):
                tab_data = self.get_current_tab_data()
                if not tab_data:
                    return
                tree = tab_data["tree"]

                # Используем FM_GUI.after для безопасного обновления GUI из другого потока
                self.FM_GUI.after(0, self._add_search_result_to_table_gui, item, tree)

            def _add_search_result_to_table_gui(self, item, tree):
                try:
                    size_str = get_formatted_size(item["size"])
                    mod_time_str = format_time(item["edited"])

                    # Добавляем элемент в таблицу
                    tree.insert("", "end", iid=item["path"], values=(item["name"], size_str, item["type"], mod_time_str))
                    if item["is_dir"]:
                        tree.item(item["path"], tags=("directory",))
                except:
                    logger.exception(f'FM - {l("search_error")}')



            # Рекурсивный поиск файлов
            def recursive_search_files(self, start_path, search_text, case_sensitive, whole_word, single_dir):
                # Подготовка поискового текста
                search_term = search_text if case_sensitive else search_text.lower()

                # Функция для проверки совпадения
                def match_criteria(name):
                    check_name = name if case_sensitive else name.lower()

                    if whole_word:
                        return check_name == search_term
                    else:
                        # Если в поисковом тексте есть символы подстановки, используем fnmatch
                        if "*" in search_text or "?" in search_text:
                            return fnmatch.fnmatch(name, search_text)
                        else:
                            return search_term in check_name

                # Если ищем только в текущем каталоге
                if single_dir:
                    try:
                        for item_name in os.listdir(start_path):
                            if match_criteria(item_name):
                                item_path = os.path.join(start_path, item_name)
                                try:
                                    # Получаем информацию о файле/каталоге
                                    parent_dir = os.path.dirname(item_path)
                                    all_items_in_dir = get_files_info(parent_dir)
                                    found_item = next((i for i in all_items_in_dir if i["path"] == item_path), None)
                                    if found_item:
                                        yield found_item # Возвращаем найденный элемент
                                except:
                                    logger.exception(f'FM - {l("info_file_error")} {item_path}')
                    except:
                        logger.exception(f'FM - {l("read_dir_error")} {start_path}')

                # Рекурсивный поиск
                else:
                    for root, dirs, files in os.walk(start_path, topdown=True):
                        # Ищем совпадения в именах каталогов
                        for dir_name in list(dirs):
                            if match_criteria(dir_name):
                                dir_path = os.path.join(root, dir_name)
                                try:
                                    stat = os.stat(dir_path)
                                    yield {
                                        "name": dir_name,
                                        "path": dir_path,
                                        "size": 0,
                                        "edited": stat.st_mtime,
                                        "created": stat.st_ctime,
                                        "type": l("dir"),
                                        "is_dir": True,
                                        "ext": ""
                                    }
                                except:
                                    logger.exception(f'FM - {l("read_dir_error")} {dir_path}')

                        # Ищем совпадения в именах файлов
                        for file_name in files:
                            if match_criteria(file_name):
                                file_path = os.path.join(root, file_name)
                                try:
                                    # Получаем информацию о файле
                                    parent_dir = os.path.dirname(file_path)
                                    all_items_in_dir = get_files_info(parent_dir)
                                    found_item = next((i for i in all_items_in_dir if i["path"] == file_path), None)
                                    if found_item:
                                        yield found_item # Возвращаем найденный элемент
                                except:
                                    logger.exception(f'FM - {l("read_file_error")} {file_path}')



        FM_GUI = tk.Tk()

        apply_global_theme(FM_GUI, current_theme)

        FileManagerApp(FM_GUI)

        # Обработка закрытия окна
        def on_closing():
            if messagebox.askokcancel(RS(), l("fm_exit")):
                FM_GUI.destroy()

        FM_GUI.protocol("WM_DELETE_WINDOW", on_closing)
        FM_GUI.mainloop()

    except Exception as e:
        logger.exception(l("fm_critical_error"))
        messagebox.showerror(RS(), f'{l("fm_critical_error")}\n{e}')

if __name__ == "__main__":
    from config import THEME, DEFAULT_THEME
    FM(False, THEME[DEFAULT_THEME])
