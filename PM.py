# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

from languages import l
# Логирование
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
# Интерфейс
from tkinter import ttk, messagebox
import tkinter as tk
import os
try:
    import psutil
    from EC import EC, get_process_critical_status
except:
    def EC(a=None, b=None):
        pass
    def get_process_critical_status(a=None, b=None):
        pass
    from OF import Psutil
    psutil = Psutil()

PROCESS_MANAGER_VERSION = "1.9.8 Beta"

# Действие с процессами
def action_process(PM_GUI_ELEMENTS=False, action="suspend", process_ids=None, RUN_IN_RECOVERY=False, DEBUG_MODE=False):
    """
    Функция для действия с процессами
    PM_GUI_ELEMENTS - окна tkinter - передавать только если функция вызывается из интерфейса PM
    action (str) - действие с процессом
        kill - убить процесс (важно: перед убийством процесса его критичность будет установлена на False)
        suspend - заморозить процесс
        resume - разморозить процесс
        edit_critical_to_false - изменить критичсноть процесса на False
        edit_critical_to_true - изменить критичсноть процесса на True
    process_ids (list) - список id процессов для операции
    RUN_IN_RECOVERY - Код работает в среде восстановления? Тогда True
    DEBUG_MODE - включить режим отладки (если True будет больше логов)
    return - функция ничего не возвращает!
    """
    if not RUN_IN_RECOVERY:
        import psutil
        from EC import EC
    else:
        psutil = Psutil()
        def EC(a=None, b=None):
            pass

    if not isinstance(process_ids, (list, tuple)):
        process_ids = [process_ids]

    for pid in process_ids:
        try:
            proc = psutil.Process(int(pid))

            if action == "kill":
                EC(int(pid), False, DEBUG_MODE)
                proc.terminate()
            elif action == "suspend":
                proc.suspend()
            elif action == "resume":
                proc.resume()
            elif action == "edit_critical_to_false":
                EC(int(pid), False, DEBUG_MODE)
            elif action == "edit_critical_to_true":
                EC(int(pid), True, DEBUG_MODE)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except:
            logger.exception(f'PM - {l("at")} {action} PID {pid}')

    # Обновляем таблицу один раз после обработки всех процессов
    if PM_GUI_ELEMENTS:
        PM_GUI_ELEMENTS["manager"].after(200, lambda: load_current_tab_data(PM_GUI_ELEMENTS, DEBUG_MODE))



def action_process_by_name(name, action="suspend", DEBUG_MODE=False):
    """
    Функция для действия с процессами по их названию
    name - имя процессов для операции
    action (str) - действие с процессом
        kill - убить процесс (важно: перед убийством процесса его критичность будет установлена на False)
        suspend - заморозить процесс
        resume - разморозить процесс
        edit_critical_to_false - изменить критичсноть процесса на False
        edit_critical_to_true - изменить критичсноть процесса на True
    DEBUG_MODE - включить режим отладки (если True будет больше логов)
    return - функция ничего не возвращает!
    """
    try:
        import psutil
        from EC import EC
    except:
        pass
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"] == name:
                # Изменяем критичность
                EC(proc.pid, False)
                # Выполняем действие
                action_process(False, action, proc.pid, RUN_IN_RECOVERY, DEBUG_MODE)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except:
            logger.exception(f'ARM/PM - {l("action_error")} {action}')



# Копируем текст в буфер обмена
def copy_to_clipboard(manager, text):
    manager.clipboard_clear()
    manager.clipboard_append(text)

def delete_file(file_path):
    os.remove(file_path)

def kill_delete_process(PID, PM_GUI_ELEMENTS=False):
    proces = psutil.Process(PID)
    process_file = proces.exe()
    process_name = proces.name()
    action_process(PM_GUI_ELEMENTS, "kill", proces.pid, DEBUG_MODE)
    try:
        proces.wait(timeout=3) # Ждёт максимум 3 секунды
    except psutil.TimeoutExpired:
        comment = f'PM - {l("process")} {process_name} ({PID[0]}) {l("process_dont_close")}'
        logger.error(comment)
        messagebox.showerror(RS(), comment)
    delete_file(process_file)

# Контекстное Меню
def show_context_menu(event, PM_GUI_ELEMENTS, selected_pids):
    manager = PM_GUI_ELEMENTS["manager"]
    tree = PM_GUI_ELEMENTS["tree"]
    menu = tk.Menu(manager, tearoff=0)

    count = len(selected_pids)
    suffix = f' ({count} {l("things")}.)' if count > 1 else ""

    if selected_pids:
        # Стандартные действия
        menu.add_command(label=f'{l("kill_processes")} {suffix}',
                         command=lambda: action_process(PM_GUI_ELEMENTS, "kill", selected_pids, DEBUG_MODE))
        menu.add_command(label=f'{l("suspend")} {suffix}',
                         command=lambda: action_process(PM_GUI_ELEMENTS, "suspend", selected_pids, DEBUG_MODE))
        menu.add_command(label=f'{l("resume")} {suffix}',
                         command=lambda: action_process(PM_GUI_ELEMENTS, "resume", selected_pids, DEBUG_MODE))
        menu.add_separator()
        menu.add_command(label=f'{l("make_it_critical")} {suffix}',
                         command=lambda: action_process(PM_GUI_ELEMENTS, "edit_critical_to_true", selected_pids, DEBUG_MODE))
        menu.add_command(label=f'{l("remove_criticality")} {suffix}',
                         command=lambda: action_process(PM_GUI_ELEMENTS, "edit_critical_to_false", selected_pids, DEBUG_MODE))

        # если выбран ровно один процесс
        if count == 1:
            menu.add_separator()
            item_values = tree.item(selected_pids[0], "values")
            file_path = item_values[2] if len(item_values) > 2 else ""
            file_name = proc.name(selected_pids[0])

            menu.add_command(label=l("kill_delete_file_process"), command=lambda: kill_delete_process(int(selected_pids[0]), PM_GUI_ELEMENTS))
            menu.add_separator()

            if file_path and file_path != l("no_data"):
                menu.add_command(
                    label=f'{l("copy_path")} {l("to_file")}',
                    command=lambda: copy_to_clipboard(manager, file_path))
                menu.add_command(
                    label=l("copy_name"),
                    command=lambda: copy_to_clipboard(manager, file_path)
                )

    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()

# Обработчик ПКМ
def handle_right_click(event, PM_GUI_ELEMENTS):
    tree = PM_GUI_ELEMENTS["tree"]
    item_under_cursor = tree.identify_row(event.y)

    selected_items = list(tree.selection())

    # Если мы нажали ПКМ на элемент, который не выделен — выделяем только его
    if item_under_cursor and item_under_cursor not in selected_items:
        tree.selection_set(item_under_cursor)
        selected_items = [item_under_cursor]

    if selected_items:
        show_context_menu(event, PM_GUI_ELEMENTS, selected_items)

# Установка столбиков, в зависимости от вкладки
def set_treeview_columns(PM_GUI_ELEMENTS, DEBUG_MODE=False):
    if PM_GUI_ELEMENTS["tree"] and PM_GUI_ELEMENTS["tree"].winfo_exists():
        for col in PM_GUI_ELEMENTS["tree"]["columns"]:
            # Запоминаем ширину каждой колонки
            PM_GUI_ELEMENTS["column_widths"][col] = PM_GUI_ELEMENTS["tree"].column(col, width=None)

    if PM_GUI_ELEMENTS["tree"] and PM_GUI_ELEMENTS["tree"].winfo_exists():
        PM_GUI_ELEMENTS["tree"].destroy()
    if PM_GUI_ELEMENTS["vsb"] and PM_GUI_ELEMENTS["vsb"].winfo_exists():
        PM_GUI_ELEMENTS["vsb"].pack_forget()

    current_frame = PM_GUI_ELEMENTS["tabs"][PM_GUI_ELEMENTS["current_tab"]]

    PM_GUI_ELEMENTS["tree"] = ttk.Treeview(current_frame, selectmode="extended")
    PM_GUI_ELEMENTS["tree"].pack(side="left", fill="both", expand=True)

    PM_GUI_ELEMENTS["vsb"] = ttk.Scrollbar(current_frame, orient="vertical", command=PM_GUI_ELEMENTS["tree"].yview)
    PM_GUI_ELEMENTS["vsb"].pack(side="right", fill="y")
    PM_GUI_ELEMENTS["tree"].configure(yscrollcommand=PM_GUI_ELEMENTS["vsb"].set)

    PM_GUI_ELEMENTS["tree"].bind("<Button-3>", lambda e: handle_right_click(e, PM_GUI_ELEMENTS))

    style = ttk.Style()
    style.configure("Treeview", rowheight=25)
    PM_GUI_ELEMENTS["tree"].tag_configure("critical", background="red", foreground="white")
    PM_GUI_ELEMENTS["tree"].tag_configure("suspended", background="gray", foreground="white")
    PM_GUI_ELEMENTS["tree"].tag_configure("admin", background="orange", foreground="black")

    columns = ("PID", l("process2"), f'{l("path")} {l("to_file")}', l("user2"), l("critical"), l("status"))
    PM_GUI_ELEMENTS["tree"]["columns"] = columns
    PM_GUI_ELEMENTS["tree"]["show"] = "headings"

    def sort_column_data(col, DEBUG_MODE):
        if PM_GUI_ELEMENTS["sort_column"] == col:
            PM_GUI_ELEMENTS["sort_direction"] = "desc" if PM_GUI_ELEMENTS["sort_direction"] == "asc" else "asc"
        else:
            PM_GUI_ELEMENTS["sort_column"] = col
            PM_GUI_ELEMENTS["sort_direction"] = "asc"
        load_current_tab_data(PM_GUI_ELEMENTS, DEBUG_MODE)

    for col in columns:
        heading_text = col
        if col == PM_GUI_ELEMENTS["sort_column"]:
            heading_text += " ▼" if PM_GUI_ELEMENTS["sort_direction"] == "desc" else " ▲"

        PM_GUI_ELEMENTS["tree"].heading(col, text=heading_text, command=lambda c=col: sort_column_data(c, DEBUG_MODE))

        w = PM_GUI_ELEMENTS["column_widths"].get(col, 150)
        PM_GUI_ELEMENTS["tree"].column(col, width=w, anchor=tk.W)

# Сортируем данные
def sort_data(data, col, direction):
    # Словарь для преобразования столбцов в ключи, по которым нужно сортировать
    key_map = {
        "PID": "PID",
        l("process2"): l("process2"),
        f'{l("path")} {l("to_file")}': f'{l("path")} {l("to_file")}',
        l("user2"): l("user2"),
        l("critical"): l("critical"),
        l("status"): l("status"),
    }

    # Получаем фактический ключ для сортировки
    sort_key = key_map.get(col)

    if not sort_key:
        return data

    # Определяем, является ли ключ числовым, чтобы сортировать правильно
    is_numeric = sort_key in ["PID"]

    def sort_func(item):
        value = item.get(sort_key, "")
        if is_numeric:
            try:
                return int(value)
            except ValueError:
                return 0 # Возвращаем 0, если не удается преобразовать в число
        return value

    # Сортируем данные, reverse=True, если направление "desc" (по убыванию)
    data.sort(key=sort_func, reverse=(direction == "desc"))
    return data

# Получаем имя процесса
def get_process_name(process_id):
    process = psutil.Process(process_id)
    return process.name()

# Получаем информацию о процессе
def get_process_info(proc, DEBUG_MODE=False):
    try:
        status = l("frozen") if proc.status() == psutil.STATUS_STOPPED else l("started")

        # РЕАЛИЗОВАТЬ ПРОВЕРКУ НА АДМИНИСТРАТОРА
        is_elevated = False

        return {
            "PID": proc.pid,
            l("process2"): proc.name(),
            f'{l("path")} {l("to_file")}': proc.exe() if proc.exe() else l("no_data"),
            l("user2"): proc.username() if proc.username() else l("no_data"),
            l("critical") : get_process_critical_status(proc.pid, DEBUG_MODE),
            l("status"): status,
            l("admin"): is_elevated,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None
    except:
        process_name = get_process_name(proc.pid)
        logger.exception(f'PM - {l("info_process_error")} {process_name} (pid:{proc.pid})')
        return None

def filter_data_by_search(data, query):
    if not query:
        return data # Если строка поиска пустая, возвращаем все данные

    lower_query = query.lower()
    filtered_data = []

    # Перебираем каждый процесс
    for item in data:
        found = False
        # Перебираем все значения в процессе
        for value in item.values():
            # Проверяем, есть ли совпадение в любом столбце
            if lower_query in str(value).lower():
                found = True
                break
        if found:
            filtered_data.append(item)

    return filtered_data

# Получаем список процессов
def get_process_list(list_type, DEBUG_MODE=False):
    all_processes = []
    for proc in psutil.process_iter(["pid", "name", "exe", "username", "status"]):
        info = get_process_info(proc, DEBUG_MODE)
        if info:
            all_processes.append(info)

    if list_type == "all_list":
        return all_processes
    elif list_type == "critical_list":
        return [p for p in all_processes if p[l("critical")]]
    elif list_type == "suspend_list":
        return [p for p in all_processes if p[l("status")] == l("frozen")]
    return []

# Загружаем данные для активной вкладки и заполняем таблицу
def load_current_tab_data(PM_GUI_ELEMENTS, DEBUG_MODE=False):
    tree = PM_GUI_ELEMENTS["tree"]
    current_tab = PM_GUI_ELEMENTS["current_tab"]

    # Получаем PID процесса, который в данный момент в фокусе/выбран
    saved_pid = None
    saved_scroll_pos = None # переменная для сохранения позиции скролла
    try:
        # focus() возвращает PID элемента, который в фокусе
        focused_item_id = tree.focus()
        # selection() возвращает список выделенных iid
        selected_item_ids = tree.selection()

        # Сохраняем PID, который нужно восстановить
        if focused_item_id:
            saved_pid = int(focused_item_id)
        elif selected_item_ids:
            saved_pid = int(selected_item_ids[0])

        # Сохраняем позицию скроллбара
        saved_scroll_pos = tree.yview()[0]

    except Exception:
        pass

    # Загрузка исходных данных
    raw_data = []
    if current_tab == l("all_process"):
        raw_data = get_process_list("all_list", DEBUG_MODE)
    elif current_tab == l("critical_process"):
        raw_data = get_process_list("critical_list", DEBUG_MODE)
    elif current_tab == l("suspend_process"):
        raw_data = get_process_list("suspend_list", DEBUG_MODE)

    if raw_data is None:
        raw_data = []

    PM_GUI_ELEMENTS["treeview_data"] = filter_data_by_search(raw_data, PM_GUI_ELEMENTS["search_query"])

    # применяем сортировку перед заполнением таблицы
    PM_GUI_ELEMENTS["treeview_data"] = sort_data(
        PM_GUI_ELEMENTS["treeview_data"],
        PM_GUI_ELEMENTS["sort_column"],
        PM_GUI_ELEMENTS["sort_direction"]
    )
    # Перезагружаем колонки для обновления символа сортировки
    set_treeview_columns(PM_GUI_ELEMENTS, DEBUG_MODE)

    tree = PM_GUI_ELEMENTS["tree"]

    columns = PM_GUI_ELEMENTS["tree"]["columns"]

    # Заполнение таблицы
    all_pids = []
    for PM_data in PM_GUI_ELEMENTS["treeview_data"]:
        values = [str(PM_data.get(col, "")) for col in columns]
        unique_id = str(PM_data["PID"])
        all_pids.append(PM_data["PID"])

        tags = []
        if PM_data.get(l("critical")):
            tags.append("critical")
        if PM_data.get(l("status")) == l("frozen"):
            tags.append("suspended")
        if PM_data.get(l("admin")):
            tags.append("admin")

        # iid (идентификатор элемента) устанавливаем как PID
        tree.insert("", "end", values=values, tags=tuple(tags), iid=unique_id, open=True)

    focus_restored = False

    if saved_pid is not None:
        new_focus_id = str(saved_pid)

        # Если PID все еще в списке доступных процессов
        if new_focus_id in tree.get_children():
            # Восстанавливаем фокус и выделение
            tree.focus(new_focus_id)
            tree.selection_set(new_focus_id)
            tree.see(new_focus_id) # Прокручиваем до него
            tree.focus_set()
            focus_restored = False
        else:
            # Элемент пропал. Ищем ближайший.
            try:
                insertion_index = next(i for i, pid in enumerate(all_pids) if pid > saved_pid)

                if insertion_index > 0:
                    # Берем предыдущий элемент (ближайший меньший PID)
                    focus_pid = all_pids[insertion_index - 1]
                else:
                    # Берем первый доступный
                    focus_pid = all_pids[0]

                new_focus_id = str(focus_pid)

                tree.focus(new_focus_id)
                tree.selection_set(new_focus_id)
                tree.see(new_focus_id)
                tree.focus_set()
                focus_restored = False

            except (StopIteration, IndexError):
                # Если список пуст или saved_pid был больше всех, восстанавливаем скролл, если есть
                if all_pids:
                    # Берем последний
                    last_pid = all_pids[-1]
                    new_focus_id = str(last_pid)
                    tree.focus(new_focus_id)
                    tree.selection_set(new_focus_id)
                    tree.see(new_focus_id)
                    tree.focus_set()
                    focus_restored = False

    if not focus_restored and saved_scroll_pos is not None:
        tree.yview_moveto(saved_scroll_pos)

    # Если фокуса нет (например, первый запуск или сброс), устанавливаем на первый элемент
    if not tree.focus() and tree.get_children():
        first_item = tree.get_children()[0]
        tree.focus(first_item)
        tree.selection_set(first_item)
        tree.see(first_item) # Прокручиваем к первому элементу
        tree.focus_set()

    # Планируем следующие обновление таблицы
    # Это обновление автоматически повторно применит фильтр, если он установлен
    if "after_id" in PM_GUI_ELEMENTS and PM_GUI_ELEMENTS["after_id"] is not None:
        PM_GUI_ELEMENTS["manager"].after_cancel(PM_GUI_ELEMENTS["after_id"])

    PM_GUI_ELEMENTS["after_id"] = PM_GUI_ELEMENTS["manager"].after(
    PM_GUI_ELEMENTS["update_interval"],
    lambda: load_current_tab_data(PM_GUI_ELEMENTS, DEBUG_MODE))



def PM(RUN_IN_RECOVERY=False, current_theme="dark", DEBUG_MODE=False):
    from OF import pac, Psutil, apply_global_theme, extract_filename_from_path, create_menubar
    from RS import RS
    from config import TIME_TO_UPDATE_PROCESS_LIST
    search_dialog_open = False

    PM_GUI_ELEMENTS = {
        "manager": None,
        "notebook": None,
        "tree": None,
        "tabs": {},
        "vsb": None,
        "current_tab": l("all_process"),
        "treeview_data": [],
        "update_interval": TIME_TO_UPDATE_PROCESS_LIST * 1000,
        "sort_column": "PID",
        "sort_direction": "asc",
        "search_query": "",
        # Начальные значения ширины колонок
        "column_widths": {"PID": 50, l("process2"): 150, f'{l("path")} {l("to_file")}': 250, l("critical"): 80, l("status"): 80, l("user2"): 150}
    }

    if not RUN_IN_RECOVERY:
        import psutil
        from EC import EC, get_process_critical_status
    else:
        psutil = Psutil()
        def EC(a=None, b=None):
            pass
        def get_process_critical_status(a=None, b=None):
            pass


    try:
        # Обновляем таблицу
        def update_list(DEBUG_MODE):
            set_treeview_columns(PM_GUI_ELEMENTS, DEBUG_MODE)
            load_current_tab_data(PM_GUI_ELEMENTS, DEBUG_MODE)



        # Диалог Поиска
        def open_search_dialog(PM_GUI_ELEMENTS, DEBUG_MODE=False):
            nonlocal search_dialog_open
            search_dialog_open = True
            manager = PM_GUI_ELEMENTS["manager"]
            # Создаем окно поиска
            search_window = tk.Toplevel(manager)
            search_window.title(RS())
            search_window.geometry("250x125")
            search_window.attributes("-topmost", True)
            search_window.grab_set()

            ttk.Label(search_window, text=l("enter_text_for_search")).pack(pady=5, padx=10, anchor="w")
            search_text = tk.StringVar(value=PM_GUI_ELEMENTS["search_query"])
            search_entry = ttk.Entry(search_window, textvariable=search_text, width=40)
            search_entry.pack(pady=5, padx=10)
            search_entry.focus_set()

            def perform_search(DEBUG_MODE):
                PM_GUI_ELEMENTS["search_query"] = search_text.get()
                search_window.destroy()
                load_current_tab_data(PM_GUI_ELEMENTS, DEBUG_MODE)
                nonlocal search_dialog_open
                search_dialog_open = False

            def cancel_search():
                search_window.destroy()
                nonlocal search_dialog_open
                search_dialog_open = False

            button_frame = ttk.Frame(search_window)
            button_frame.pack(pady=10)
            ttk.Button(button_frame, text=l("cancel2"), command=cancel_search).pack(side="left", padx=5)
            ttk.Button(button_frame, text=l("ok"), command=lambda: perform_search(DEBUG_MODE)).pack(side="left", padx=5)

            search_window.bind("<Return>", lambda e: perform_search(DEBUG_MODE))
            search_window.bind("<Escape>", lambda e: cancel_search())

            manager.wait_window(search_window)



        # Останавливаем Поиск
        def stop_search(PM_GUI_ELEMENTS, DEBUG_MODE):
            # Проверяем, активен ли поиск вообще
            if PM_GUI_ELEMENTS["search_query"] == "":
                return # Ничего не делаем, если поиск и так пуст

            # Сбрасываем строку поиска
            PM_GUI_ELEMENTS["search_query"] = ""
            # Перезагружаем данные для отображения полного списка
            load_current_tab_data(PM_GUI_ELEMENTS, DEBUG_MODE)



        # Обработка смены вкладки
        def on_tab_change(event, PM_GUI_ELEMENTS, DEBUG_MODE=False):
            selected_tab = PM_GUI_ELEMENTS["notebook"].tab(PM_GUI_ELEMENTS["notebook"].select(), "text")
            if selected_tab != PM_GUI_ELEMENTS["current_tab"]:
                PM_GUI_ELEMENTS["current_tab"] = selected_tab
                # Сбрасываем состояние сортировки для новой вкладки
                # PM_GUI_ELEMENTS["sort_column"] = "PID"
                # PM_GUI_ELEMENTS["sort_direction"] = "asc"
                set_treeview_columns(PM_GUI_ELEMENTS, DEBUG_MODE)

                # Отменяем текущее запланированное обновление и запускаем загрузку данных
                if "after_id" in PM_GUI_ELEMENTS and PM_GUI_ELEMENTS["after_id"] is not None:
                    PM_GUI_ELEMENTS["manager"].after_cancel(PM_GUI_ELEMENTS["after_id"])
                load_current_tab_data(PM_GUI_ELEMENTS, DEBUG_MODE)



        # Обработчик клавиш
        def handle_key_action(event, PM_GUI_ELEMENTS):
            # Проверяем, открыт ли диалог поиска
            if search_dialog_open:
                return

            tree = PM_GUI_ELEMENTS["tree"]
            selected_items = tree.selection()

            if not selected_items:
                return

            action = None
            key = event.keysym

            if key in ["Delete", "Delete_Last"]:
                action = "kill"
            elif key in ["s", "S"]:
                action = "suspend"
            elif key in ["u", "U"]:
                action = "resume"
            elif key in ["c", "C"]:
                first_pid = int(selected_items[0])
                is_critical = get_process_critical_status(first_pid, DEBUG_MODE)
                action = "edit_critical_to_false" if is_critical else "edit_critical_to_true"

            if action:
                action_process(PM_GUI_ELEMENTS, action, list(selected_items), RUN_IN_RECOVERY, DEBUG_MODE)

        PM_GUI = tk.Tk()
        PM_GUI_ELEMENTS["manager"] = PM_GUI
        PM_GUI.title(RS())
        PM_GUI.geometry("810x450")

        PM_GUI.after(0, lambda: apply_global_theme(PM_GUI, current_theme))

        create_menubar(PM_GUI, RUN_IN_RECOVERY, "PM", open_search_dialog, stop_search, PM_GUI_ELEMENTS, DEBUG_MODE=DEBUG_MODE)

        # Добавляем привязку клавиш Ctrl+F, Esc, Delete, S, U, C
        # Поиск
        PM_GUI.bind_all("<Control-f>", lambda e: open_search_dialog(PM_GUI_ELEMENTS, DEBUG_MODE))
        PM_GUI.bind_all("<Control-F>", lambda e: open_search_dialog(PM_GUI_ELEMENTS, DEBUG_MODE))

        # Прекратить поиск
        PM_GUI.bind_all("<Escape>", lambda e: stop_search(PM_GUI_ELEMENTS, DEBUG_MODE))

        # Горячие клавиши действий
        PM_GUI.bind_all("<Delete>", lambda e: handle_key_action(e, PM_GUI_ELEMENTS))
        PM_GUI.bind_all("<s>", lambda e: handle_key_action(e, PM_GUI_ELEMENTS))
        PM_GUI.bind_all("<S>", lambda e: handle_key_action(e, PM_GUI_ELEMENTS))
        PM_GUI.bind_all("<u>", lambda e: handle_key_action(e, PM_GUI_ELEMENTS))
        PM_GUI.bind_all("<U>", lambda e: handle_key_action(e, PM_GUI_ELEMENTS))
        PM_GUI.bind_all("<c>", lambda e: handle_key_action(e, PM_GUI_ELEMENTS))
        PM_GUI.bind_all("<C>", lambda e: handle_key_action(e, PM_GUI_ELEMENTS))

        # Панель вкладок
        PM_GUI_ELEMENTS["notebook"] = ttk.Notebook(PM_GUI)
        PM_GUI_ELEMENTS["notebook"].pack(pady=10, padx=10, fill="both", expand=True)
        PM_GUI_ELEMENTS["notebook"].bind("<<NotebookTabChanged>>", lambda e: on_tab_change(e, PM_GUI_ELEMENTS, DEBUG_MODE))

        # Создаём вкладки
        tab_names = [l("all_process"), l("critical_process"), l("suspend_process")]
        for tab_name in tab_names:
            frame = ttk.Frame(PM_GUI_ELEMENTS["notebook"], padding="5 5 5 5")
            PM_GUI_ELEMENTS["notebook"].add(frame, text=tab_name)
            PM_GUI_ELEMENTS["tabs"][tab_name] = frame

        # Создание начальной Таблицы и Скроллбара
        initial_frame = PM_GUI_ELEMENTS["tabs"][l("all_process")]
        PM_GUI_ELEMENTS["tree"] = ttk.Treeview(initial_frame, selectmode="browse")
        PM_GUI_ELEMENTS["vsb"] = ttk.Scrollbar(initial_frame, orient="vertical", command=PM_GUI_ELEMENTS["tree"].yview)
        PM_GUI_ELEMENTS["tree"].configure(yscrollcommand=PM_GUI_ELEMENTS["vsb"].set)
        PM_GUI_ELEMENTS["tree"].pack(side="left", fill="both", expand=True)
        PM_GUI_ELEMENTS["vsb"].pack(side="right", fill="y")

        # Привязка ПКМ
        PM_GUI_ELEMENTS["tree"].bind("<Button-3>", lambda e: handle_right_click(e, PM_GUI_ELEMENTS))

        # Инициализация и загрузка первой вкладки
        update_list(DEBUG_MODE)

        PM_GUI.mainloop()
    except:
        logger.exception(l("pm_critical_error"))

if __name__ == "__main__":
    from config import THEME, DEFAULT_THEME
    current_theme = THEME[DEFAULT_THEME]
    PM(False, current_theme)
