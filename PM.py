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
from tkinter import ttk, messagebox, simpledialog
import tkinter as tk
#Логирование
from loguru import logger

from config import *
from OF import Psutil
from RS import random_string

process_manager_version = "1.5.3 Beta"

GUI_ELEMENTS = {
    "manager": None,
    "notebook": None,
    "tree": None,
    "tabs": {},
    "vsb": None,
    "current_tab": "Все Процессы",
    "treeview_data": [],
    "update_interval": time_to_update_process_list * 1000,
    "sort_column": "PID",
    "sort_direction": "asc", #Направление сортировки: "asc" (по возрастанию) или "desc" (по убыванию)
    "search_query": ""
}



def PM(run_in_recovery):
    if not run_in_recovery:
        import psutil
        from EC import EC, get_process_critical_status
    else:
        psutil = Psutil()
        def EC(i, c, d):
            pass
        def get_process_critical_status(i, r):
            return False



    try:
        #Обновляем таблицу
        def update_list():
            set_treeview_columns(GUI_ELEMENTS)
            load_current_tab_data(GUI_ELEMENTS)



        #Получаем имя процесса
        def get_process_name(process_id):
            process = psutil.Process(process_id)
            return process.name()



        #Получаем информацию о процессе
        def get_process_info(proc):
            try:
                status = "Заморожен" if proc.status() == psutil.STATUS_STOPPED else "Запущен"

                is_elevated = False
                #РЕАЛИЗОВАТЬ ПРОВЕРКУ НА ТО ЗАПУЩЕН ЛИ ПРОЦЕСС ОТ ИМЕНИ АДМИНИСТРАТОРА

                return {
                    "PID": proc.pid,
                    "Имя Процесса": proc.name(),
                    "Путь к файлу": proc.exe() if proc.exe() else "Н/Д",
                    "Пользователь": proc.username() if proc.username() else "Н/Д",
                    "Критичность": get_process_critical_status(proc.pid, run_in_recovery),
                    "Статус": status,
                    "Администратор": is_elevated,
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                return None
            except Exception as e:
                process_name = get_process_name(proc.pid)
                logger.error(f"PM - Ошибка при получении информации о процессе {process_name} (pid:{proc.pid}):\n{e}")
                return None



        #Получаем список процессов
        def get_process_list(list_type):
            all_processes = []
            for proc in psutil.process_iter(["pid", "name", "exe", "username", "status"]):
                info = get_process_info(proc)
                if info:
                    all_processes.append(info)

            if list_type == "all_list":
                return all_processes
            elif list_type == "critical_list":
                return [p for p in all_processes if p["Критичность"]]
            elif list_type == "suspend_list":
                return [p for p in all_processes if p["Статус"] == "Заморожен"]
            return []



        def filter_data_by_search(data, query):
            if not query:
                return data #Если строка поиска пустая, возвращаем все данные

            lower_query = query.lower()
            filtered_data = []

            #Перебираем каждый процесс
            for item in data:
                found = False
                #Перебираем все значения в процессе
                for value in item.values():
                    #Проверяем, есть ли совпадение в любом столбце
                    if lower_query in str(value).lower():
                        found = True
                        break
                if found:
                    filtered_data.append(item)

            return filtered_data



        #Диалог Поиска
        def open_search_dialog(gui_elements):
            manager = gui_elements["manager"]

            #Создаем дочернее окно (Toplevel)
            search_window = tk.Toplevel(manager)
            search_window.title("Поиск")
            search_window.geometry("300x100")
            search_window.resizable(False, False)
            #Делаем окно модальным (пока оно открыто, нельзя взаимодействовать с основным окном
            search_window.grab_set()

            #Устанавливаем положение окна по центру
            manager_x = manager.winfo_x()
            manager_y = manager.winfo_y()
            manager_width = manager.winfo_width()
            manager_height = manager.winfo_height()

            x = manager_x + (manager_width // 2) - 150
            y = manager_y + (manager_height // 2) - 50
            search_window.geometry(f"+{x}+{y}")

            tk.Label(search_window, text="Введите текст для поиска:").pack(pady=5, padx=10, anchor="w")

            #Текстовое поле с начальным значением
            search_text = tk.StringVar(value=gui_elements["search_query"])
            search_entry = ttk.Entry(search_window, textvariable=search_text, width=40)
            search_entry.pack(pady=5, padx=10)

            #Устанавливаем фокус на поле ввода
            search_entry.focus_set()

            def perform_search():
                #Сохраняем строку поиска в глобальном состоянии GUI_ELEMENTS
                gui_elements["search_query"] = search_text.get()
                #Закрываем окно поиска
                search_window.destroy()
                #Перезагружаем данные для применения фильтра
                load_current_tab_data(gui_elements)

            def cancel_search():
                search_window.destroy()

            button_frame = ttk.Frame(search_window)
            button_frame.pack(pady=10)

            ttk.Button(button_frame, text="Отмена", command=cancel_search).pack(side="left", padx=5)
            ttk.Button(button_frame, text="ОК", command=perform_search).pack(side="left", padx=5)

            #Привязка Enter к кнопке "ОК"
            search_window.bind("<Return>", lambda e: perform_search())
            #Привязка Esc к кнопке "Отмена"
            search_window.bind("<Escape>", lambda e: cancel_search())

            #Ожидаем закрытия окна
            manager.wait_window(search_window)



        #Останавливаем Поиск
        def stop_search(gui_elements):
            #Проверяем, активен ли поиск вообще
            if gui_elements["search_query"] == "":
                return #Ничего не делаем, если поиск и так пуст

            #Сбрасываем строку поиска
            gui_elements["search_query"] = ""
            #Перезагружаем данные для отображения полного списка
            load_current_tab_data(gui_elements)



        #Действие с процессами
        def action_process(gui_elements, action, process_id):
            try:
                proc = psutil.Process(process_id)

                if action == "kill":
                    proc.terminate()

                elif action == "suspend":
                    proc.suspend()

                elif action == "resume":
                    proc.resume()

                elif action == "edit_critical_to_false":
                    EC(process_id, False)

                elif action == "edit_critical_to_true":
                    EC(process_id, True)

                #Обновляем таблицу после действия
                gui_elements["manager"].after(100, lambda: load_current_tab_data(gui_elements))

            except psutil.NoSuchProcess:
                pass
            except psutil.AccessDenied:
                pass
            except Exception as e:
                process_name = get_process_name(process_id)
                logger.critical(f"PM - Неизвестная ошибка при выполнении {action} для {process_name} (pid: {process_id}):\n{e}")



        #О Программе
        def about_PM():
            messagebox.showinfo(random_string(), f"Менеджер Процессов - {process_manager_version}")



        #Сортируем данные
        def sort_data(data, col, direction):
            #Словарь для преобразования столбцов в ключи, по которым нужно сортировать
            key_map = {
                "PID": "PID",
                "Имя Процесса": "Имя Процесса",
                "Путь к файлу": "Путь к файлу",
                "Пользователь": "Пользователь",
                "Критичность": "Критичность",
                "Статус": "Статус",
            }

            #Получаем фактический ключ для сортировки
            sort_key = key_map.get(col)

            if not sort_key:
                return data

            #Определяем, является ли ключ числовым, чтобы сортировать правильно
            is_numeric = sort_key in ["PID"]

            def sort_func(item):
                value = item.get(sort_key, "")
                if is_numeric:
                    try:
                        return int(value)
                    except ValueError:
                        return 0 #Возвращаем 0, если не удается преобразовать в число
                return value

            #Сортируем данные. reverse=True, если направление 'desc' (по убыванию)
            data.sort(key=sort_func, reverse=(direction == "desc"))
            return data



        #Обработка смены вкладки
        def on_tab_change(event, gui_elements):
            selected_tab = gui_elements["notebook"].tab(gui_elements["notebook"].select(), "text")
            if selected_tab != gui_elements["current_tab"]:
                gui_elements["current_tab"] = selected_tab
                #сбрасываем состояние сортировки для новой вкладки
                gui_elements["sort_column"] = "PID"
                gui_elements["sort_direction"] = "asc"
                set_treeview_columns(gui_elements)
                #Отменяем текущее запланированное обновление и запускаем загрузку данных
                if "after_id" in gui_elements and gui_elements["after_id"] is not None:
                    gui_elements["manager"].after_cancel(gui_elements["after_id"])
                load_current_tab_data(gui_elements)



        #Установка столбиков, в зависимости от вкладки
        def set_treeview_columns(gui_elements):
            #Удаляем и пересоздаем таблицу и скроллбар для текущей вкладки
            if gui_elements["tree"] and gui_elements["tree"].winfo_exists():
                gui_elements["tree"].destroy()
            if gui_elements["vsb"] and gui_elements["vsb"].winfo_exists():
                gui_elements["vsb"].pack_forget()

            current_frame = gui_elements["tabs"][gui_elements["current_tab"]]

            gui_elements["tree"] = ttk.Treeview(current_frame, selectmode="browse")
            gui_elements["tree"].pack(side="left", fill="both", expand=True)

            gui_elements["vsb"] = ttk.Scrollbar(current_frame, orient="vertical", command=gui_elements["tree"].yview)
            gui_elements["vsb"].pack(side="right", fill="y")
            gui_elements["tree"].configure(yscrollcommand=gui_elements["vsb"].set)

            #Привязка ПКМ
            gui_elements["tree"].bind("<Button-3>", lambda e: handle_right_click(e, gui_elements))

            #Конфигурация стилей для подсветки
            style = ttk.Style()
            style.configure("Treeview", rowheight=25)
            style.map("Treeview", background=[("selected", "blue")])

            #Критичный
            gui_elements["tree"].tag_configure("critical", background="red", foreground="white")
            #Замороженный
            gui_elements["tree"].tag_configure("suspended", background="gray", foreground="white")
            #Админ
            gui_elements["tree"].tag_configure("admin", background="orange", foreground="black")

            columns = ("PID", "Имя Процесса", "Путь к файлу", "Пользователь", "Критичность", "Статус")
            headings = dict(zip(columns, columns))

            gui_elements["tree"]["columns"] = columns
            gui_elements["tree"]["show"] = "headings"

            #Добавляем функцию-обработчик клика по заголовку
            def sort_column_data(col):
                #Если кликнули на тот же столбец, меняем направление
                if gui_elements["sort_column"] == col:
                    gui_elements["sort_direction"] = "desc" if gui_elements["sort_direction"] == "asc" else "asc"
                else:
                    #Иначе, устанавливаем новый столбец и направление по умолчанию (asc)
                    gui_elements["sort_column"] = col
                    gui_elements["sort_direction"] = "asc"

                #Перезагружаем данные с учетом новой сортировки
                load_current_tab_data(gui_elements)

            #Установка ширины колонок и привязка сортировки
            col_widths = {"PID": 20, "Имя Процесса": 100, "Путь к файлу": 250, "Критичность": 50, "Статус": 35}
            for col in columns:
                heading_text = headings.get(col, col)
                #Добавляем символ направления сортировки к заголовку, если это текущий столбец
                if col == gui_elements["sort_column"]:
                    arrow = " ▼" if gui_elements["sort_direction"] == "desc" else " ▲"
                    heading_text += arrow

                gui_elements["tree"].heading(col, text=heading_text,
                                             command=lambda c=col: sort_column_data(c)) #Привязываем команду сортировки
                gui_elements["tree"].column(col, width=col_widths.get(col, 150), anchor=tk.W)



        #Загружаем данные для активной вкладки и заполняем таблицу
        def load_current_tab_data(gui_elements):
            tree = gui_elements["tree"]
            current_tab = gui_elements["current_tab"]

            #сохраняем текущий фокус, выделение и позицию скролла
            #Получаем PID процесса, который в данный момент в фокусе/выбран
            saved_pid = None
            saved_scroll_pos = None #переменная для сохранения позиции скролла
            try:
                #focus() возвращает iid (PID) элемента, который в фокусе
                focused_item_id = tree.focus()
                #selection() возвращает список выделенных iid
                selected_item_ids = tree.selection()

                #Сохраняем PID, который нужно восстановить
                if focused_item_id:
                    saved_pid = int(focused_item_id)
                elif selected_item_ids:
                    saved_pid = int(selected_item_ids[0])

                #Сохраняем позицию скроллбара
                saved_scroll_pos = tree.yview()[0]

            except Exception:
                pass

            #Загрузка исходных данных
            raw_data = []
            if current_tab == "Все Процессы":
                raw_data = get_process_list("all_list")
            elif current_tab == "Критичные Процессы":
                raw_data = get_process_list("critical_list")
            elif current_tab == "Замороженные Процессы":
                raw_data = get_process_list("suspend_list")

            if raw_data is None:
                raw_data = []

            gui_elements["treeview_data"] = filter_data_by_search(raw_data, gui_elements["search_query"])

            gui_elements["treeview_data"] = filter_data_by_search(raw_data, gui_elements["search_query"])
            #применяем сортировку перед заполнением таблицы
            gui_elements["treeview_data"] = sort_data(
                gui_elements["treeview_data"],
                gui_elements["sort_column"],
                gui_elements["sort_direction"]
            )
            #Перезагружаем колонки для обновления символа сортировки
            set_treeview_columns(gui_elements)

            tree = gui_elements["tree"]

            columns = gui_elements["tree"]["columns"]

            #Заполнение таблицы
            all_pids = []
            for PM_data in gui_elements["treeview_data"]:
                values = [str(PM_data.get(col, "")) for col in columns]
                unique_id = str(PM_data["PID"])
                all_pids.append(PM_data["PID"])

                tags = []
                if PM_data.get("Критичность"):
                    tags.append("critical")
                if PM_data.get("Статус") == "Заморожен":
                    tags.append("suspended")
                if PM_data.get("Администратор"):
                    tags.append("admin")

                #iid (идентификатор элемента) устанавливаем как PID
                tree.insert("", "end", values=values, tags=tuple(tags), iid=unique_id, open=True)

            focus_restored = False

            if saved_pid is not None:
                new_focus_id = str(saved_pid)

                #Если PID все еще в списке доступных процессов
                if new_focus_id in tree.get_children():
                    #Восстанавливаем фокус и выделение
                    tree.focus(new_focus_id)
                    tree.selection_set(new_focus_id)
                    tree.see(new_focus_id) #Прокручиваем до него
                    tree.focus_set()
                    focus_restored = False
                else:
                    #Элемент пропал. Ищем ближайший.
                    try:
                        insertion_index = next(i for i, pid in enumerate(all_pids) if pid > saved_pid)

                        if insertion_index > 0:
                            #Берем предыдущий элемент (ближайший меньший PID)
                            focus_pid = all_pids[insertion_index - 1]
                        else:
                            #Берем первый доступный
                            focus_pid = all_pids[0]

                        new_focus_id = str(focus_pid)

                        tree.focus(new_focus_id)
                        tree.selection_set(new_focus_id)
                        tree.see(new_focus_id)
                        tree.focus_set()
                        focus_restored = False

                    except (StopIteration, IndexError):
                        #Если список пуст или saved_pid был больше всех, восстанавливаем скролл, если есть
                        if all_pids:
                            #Берем последний
                            last_pid = all_pids[-1]
                            new_focus_id = str(last_pid)
                            tree.focus(new_focus_id)
                            tree.selection_set(new_focus_id)
                            tree.see(new_focus_id)
                            tree.focus_set()
                            focus_restored = False

            if not focus_restored and saved_scroll_pos is not None:
                tree.yview_moveto(saved_scroll_pos)

            #Если фокуса нет (например, первый запуск или сброс), устанавливаем на первый элемент
            if not tree.focus() and tree.get_children():
                first_item = tree.get_children()[0]
                tree.focus(first_item)
                tree.selection_set(first_item)
                tree.see(first_item) #Прокручиваем к первому элементу
                tree.focus_set()

            #Планируем следующие обновление таблицы
            #Это обновление автоматически повторно применит фильтр, если он установлен
            if "after_id" in gui_elements and gui_elements["after_id"] is not None:
                gui_elements["manager"].after_cancel(gui_elements["after_id"])

            gui_elements["after_id"] = gui_elements["manager"].after(
            gui_elements["update_interval"],
            lambda: load_current_tab_data(gui_elements)
            )



        #Контекстное Меню
        def show_context_menu(event, gui_elements, PM_data, item_id):
            manager = gui_elements["manager"]
            current_tab = gui_elements["current_tab"]

            menu = tk.Menu(manager, tearoff=0)

            if PM_data:
                process_path = PM_data["Путь к файлу"]
                process_name = PM_data["Имя Процесса"]
                critical_state = "Критичный" if PM_data["Критичность"] else "Не критичный"
                is_suspend = PM_data["Статус"] == "Заморожен"
                process_id = PM_data["PID"]

                if current_tab == "Все Процессы":
                    menu.add_command(label=f"Убить Процесс ({critical_state})",
                                     command=lambda: action_process(gui_elements, "kill", process_id))
                    if is_suspend:
                        menu.add_command(label="Разморозить",
                                         command=lambda: action_process(gui_elements, "resume", process_id))
                    else:
                        menu.add_command(label="Заморозить",
                                         command=lambda: action_process(gui_elements, "suspend", process_id))
                    if get_process_critical_status(process_id, run_in_recovery):
                        menu.add_command(label=f"Снять критичность",
                                         command=lambda: action_process(gui_elements, "edit_critical_to_false", process_id))
                    if not get_process_critical_status(process_id, run_in_recovery):
                        menu.add_command(label=f"Сделать критичным",
                                         command=lambda: action_process(gui_elements, "edit_critical_to_true", process_id))
                    menu.add_separator()
                    menu.add_command(label="Копировать путь", command=lambda: copy_to_clipboard(manager, process_path))
                    menu.add_command(label="Копировать имя процесса", command=lambda: copy_to_clipboard(manager, process_name))
                elif current_tab == "Критичные Процессы" or "Замороженные Процессы":
                    menu.add_command(label=f"Снять критичность",
                                     command=lambda: action_process(gui_elements, "edit_critical_to_false", process_id))
                    menu.add_command(label=f"Убить Процесс ({critical_state})",
                                     command=lambda: action_process(gui_elements, "kill", process_id))
                    menu.add_command(label="Разморозить",
                                     command=lambda: action_process(gui_elements, "resume", process_id))
                    menu.add_separator()
                    menu.add_command(label="Копировать путь", command=lambda: copy_to_clipboard(manager, process_path))
                    menu.add_command(label="Копировать имя процесса", command=lambda: copy_to_clipboard(manager, process_name))
                else:
                    menu.add_command(label=f"Убить Процесс ({critical_state})",
                                     command=lambda: action_process(gui_elements, "kill", process_id))
                    if is_suspend:
                        menu.add_command(label="Разморозить",
                                         command=lambda: action_process(gui_elements, "resume", process_id))
                    else:
                        menu.add_command(label="Заморозить",
                                         command=lambda: action_process(gui_elements, "suspend", process_id))
                    if get_process_critical_status(process_id, run_in_recovery):
                        menu.add_command(label=f"Снять критичность",
                                         command=lambda: action_process(gui_elements, "edit_critical_to_false", process_id))
                    if not get_process_critical_status(process_id, run_in_recovery):
                        menu.add_command(label=f"Сделать критичным",
                                         command=lambda: action_process(gui_elements, "edit_critical_to_true", process_id))
                    menu.add_separator()
                    menu.add_command(label="Копировать путь", command=lambda: copy_to_clipboard(manager, process_path))
                    menu.add_command(label="Копировать имя процесса", command=lambda: copy_to_clipboard(manager, process_name))

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()



        #Обработчик ПКМ
        def handle_right_click(event, gui_elements):
            #Получаем элемент, на котором был сделан клик
            item_id = gui_elements["tree"].identify_row(event.y)
            gui_elements["tree"].selection_set(item_id) #Выделяем элемент
            if item_id:
                process_id = int(item_id)
                #Находим исходные данные для выбранного элемента по PID
                PM_data = next((data for data in gui_elements["treeview_data"] if data.get("PID") == process_id), None)
            else:
                #Если клик был не на элементе
                PM_data = None

            show_context_menu(event, gui_elements, PM_data, item_id)



        #Копируем текст в буфер обмена
        def copy_to_clipboard(manager, text):
            manager.clipboard_clear()
            manager.clipboard_append(text)



        #Обработчик клавиш
        def handle_key_action(event, gui_elements):
            tree = gui_elements["tree"]

            #Получаем PID выделенного элемента
            selected_items = tree.selection()
            if not selected_items:
                return #Ничего не делаем, если ничего не выбрано

            #Так как selectmode="browse", мы ожидаем только один элемент
            selected_item_id = selected_items[0]
            try:
                process_id = int(selected_item_id)
            except ValueError:
                return #ID должен быть числом (PID)

            action = None
            key = event.keysym

            if key in ["Delete", "Delete_Last"]: #Клавиша Delete (Удалить)
                action = "kill"
            elif key == "s": #Клавиша S (Заморозить)
                action = "suspend"
            elif key == "u": #Клавиша U (Разморозить)
                action = "resume"
            elif key == "c": #Клавиша C (Критичность)
                #Для критичности нужно определить текущее состояние
                is_critical = get_process_critical_status(process_id)
                action = "edit_critical_to_false" if is_critical else "edit_critical_to_true"

            if action:
                #Выполняем соответствующее действие
                action_process(gui_elements, action, process_id)



        PM = tk.Tk()
        GUI_ELEMENTS["manager"] = PM
        PM.title(random_string())
        PM.geometry("800x450")

        #Меню
        menubar = tk.Menu(PM)
        #Создаем выпадающее меню "Действия"
        actions_menu = tk.Menu(menubar, tearoff=0)
        actions_menu.add_command(label="Поиск", accelerator="Ctrl+F", command=lambda: open_search_dialog(GUI_ELEMENTS))
        actions_menu.add_command(label="Прекратить поиск", accelerator="Esc", command=lambda: stop_search(GUI_ELEMENTS))
        menubar.add_cascade(label="Действия", menu=actions_menu)

        #Пункт "О Программе"
        menubar.add_command(label="О программе", command=about_PM)
        PM.config(menu=menubar)

        #Добавляем привязку клавиш Ctrl+F, Esc, Delete, S, U, C
        #Поиск
        PM.bind_all("<Control-f>", lambda e: open_search_dialog(GUI_ELEMENTS))
        PM.bind_all("<Control-F>", lambda e: open_search_dialog(GUI_ELEMENTS))

        #Прекратить поиск
        PM.bind_all("<Escape>", lambda e: stop_search(GUI_ELEMENTS))

        #Горячие клавиши действий
        PM.bind_all("<Delete>", lambda e: handle_key_action(e, GUI_ELEMENTS))
        PM.bind_all("<s>", lambda e: handle_key_action(e, GUI_ELEMENTS))
        PM.bind_all("<S>", lambda e: handle_key_action(e, GUI_ELEMENTS))
        PM.bind_all("<u>", lambda e: handle_key_action(e, GUI_ELEMENTS))
        PM.bind_all("<U>", lambda e: handle_key_action(e, GUI_ELEMENTS))
        PM.bind_all("<c>", lambda e: handle_key_action(e, GUI_ELEMENTS))
        PM.bind_all("<C>", lambda e: handle_key_action(e, GUI_ELEMENTS))

        #Панель вкладок
        GUI_ELEMENTS["notebook"] = ttk.Notebook(PM)
        GUI_ELEMENTS["notebook"].pack(pady=10, padx=10, fill="both", expand=True)
        GUI_ELEMENTS["notebook"].bind("<<NotebookTabChanged>>",
                                      lambda e: on_tab_change(e, GUI_ELEMENTS))

        #Создаём вкладки
        tab_names = ["Все Процессы", "Критичные Процессы", "Замороженные Процессы"]
        for tab_name in tab_names:
            frame = ttk.Frame(GUI_ELEMENTS["notebook"], padding="5 5 5 5")
            GUI_ELEMENTS["notebook"].add(frame, text=tab_name)
            GUI_ELEMENTS["tabs"][tab_name] = frame

        #Создание начальной Таблицы и Скроллбара
        initial_frame = GUI_ELEMENTS["tabs"]["Все Процессы"]
        GUI_ELEMENTS["tree"] = ttk.Treeview(initial_frame, selectmode="browse")
        GUI_ELEMENTS["vsb"] = ttk.Scrollbar(initial_frame, orient="vertical", command=GUI_ELEMENTS["tree"].yview)
        GUI_ELEMENTS["tree"].configure(yscrollcommand=GUI_ELEMENTS["vsb"].set)
        GUI_ELEMENTS["tree"].pack(side="left", fill="both", expand=True)
        GUI_ELEMENTS["vsb"].pack(side="right", fill="y")

        #Привязка ПКМ
        GUI_ELEMENTS["tree"].bind("<Button-3>", lambda e: handle_right_click(e, GUI_ELEMENTS))

        #Инициализация и загрузка первой вкладки
        update_list()

        PM.mainloop()
    except Exception as e:
        logger.critical(f"В Компоненте ProcessManager произошла неизвестная ошибка!\n{e}")
