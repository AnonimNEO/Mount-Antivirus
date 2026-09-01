# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
import time
import datetime
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
import winreg
import queue

from RS import RS
from OF import apply_global_theme
from languages import l
from PM import action_process
from RM import RegistryMonitor

SOFTWARE_INSTALLATION_MANAGER = "0.1.14 Pre-Alpha"

class SoftwareInstallManager:
    def __init__(self, SIM_GUI):
        self.SIM_GUI = SIM_GUI
        self.SIM_GUI.title(RS())
        self.SIM_GUI.geometry("1000x700")

        # Создаем вкладки
        self.notebook = ttk.Notebook(SIM_GUI)
        self.notebook.pack(fill="both", expand=True)

        # Вкладка для мониторинга
        self.monitoring_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.monitoring_tab, text="Мониторинг")

        # Создаем содержимое вкладки
        self.create_monitoring_tab()

        # Инициализация переменных
        self.exe_path = None

        # Очередь для событий реестра
        self.registry_event_queue = queue.Queue()
        self.monitoring_active = False # Добавим флаг для контроля активности мониторинга
        self.active_registry_monitors = [] # Список для хранения активных мониторов реестра
        self.registry_check_after_id = None # Инициализируем переменную для after_cancel

    # Запускает мониторинг реестра и цикл проверки очереди
    def _start_registry_monitoring(self):
        if self.monitoring_active and self.active_registry_monitors: #  Проверяем, не запущен ли уже мониторинг
            logger.info("SIM - Мониторинг реестра уже активен.")
            return

        logger.info("SIM - Запуск мониторинга реестра...")
        # Запускаем поток для RM с передачей очереди
        def reg_monitor_thread_starter():
            # Создаем и запускаем мониторы в отдельном потоке
            monitors = [
                RegistryMonitor(
                    winreg.HKEY_CURRENT_USER,
                    "",
                    watch_subtree=True,
                    event_queue=self.registry_event_queue
                ),
                RegistryMonitor(
                    winreg.HKEY_LOCAL_MACHINE,
                    "",
                    watch_subtree=True,
                    event_queue=self.registry_event_queue
                ),
                RegistryMonitor(
                    winreg.HKEY_CLASSES_ROOT,
                    "",
                    watch_subtree=True,
                    event_queue=self.registry_event_queue
                ),
                RegistryMonitor(
                    winreg.HKEY_USERS,
                    "",
                    watch_subtree=True,
                    event_queue=self.registry_event_queue
                ),
                RegistryMonitor(
                    winreg.HKEY_CURRENT_CONFIG,
                    "",
                    watch_subtree=True,
                    event_queue=self.registry_event_queue
                ),
            ]
            for monitor in monitors:
                monitor.start()
            self.active_registry_monitors = monitors # Сохраняем ссылки на мониторы
            logger.info("SIM - Все мониторы реестра запущены.")

        self.reg_monitor_starter_thread = threading.Thread(target=reg_monitor_thread_starter, daemon=True)
        self.reg_monitor_starter_thread.start()

        # Запускаем цикл проверки очереди, если он еще не запущен
        if not hasattr(self, "registry_check_after_id") or self.registry_check_after_id is None:
            self.registry_check_after_id = self.SIM_GUI.after(100, self.check_registry_events)

    # Останавливает все активные мониторы реестра
    def _stop_registry_monitoring(self):
        if not self.active_registry_monitors:
            logger.info("SIM - Нет активных мониторов реестра для остановки.")
            return

        logger.info("SIM - Остановка мониторинга реестра...")
        for monitor in self.active_registry_monitors:
            monitor.stop()
        self.active_registry_monitors.clear() # Очищаем список
        logger.info("SIM - Все мониторы реестра остановлены.")

        # Отменяем запланированную проверку очереди, если она активна
        if hasattr(self, "registry_check_after_id") and self.registry_check_after_id:
            self.SIM_GUI.after_cancel(self.registry_check_after_id)
            self.registry_check_after_id = None # Обнуляем идентификатор

    # Проверяет очередь на новые события и обновляет вкладку реестра
    def check_registry_events(self):
        if not self.monitoring_active: # Прекращаем проверку, если мониторинг остановлен
            return

        try:
            while not self.registry_event_queue.empty():
                message = self.registry_event_queue.get_nowait()
                self._add_registry_log(message)
        except queue.Empty:
            pass
        # Обновляем self.registry_check_after_id с новым идентификатором
        self.registry_check_after_id = self.SIM_GUI.after(100, self.check_registry_events)

    # Добавляет сообщение о событии реестра во вкладку "Реестр"
    def _add_registry_log(self, message):
        # Получите нужный фрейм/виджет
        frame = self.log_frames.get("registry")
        if frame:
            # message уже содержит всю необходимую информацию
            label = ttk.Label(frame.log_frame, text=message, style="TInstall.TLabel", anchor="w", font=("Default", 9))
            label.pack(fill="x", padx=5, pady=2)
            frame.log_frame.update_idletasks()
            frame.canvas.yview_moveto(1.0)
            frame.log_lines.append(label)
            # Также можно логировать в файл или память
            if self.log_file_path: # Если логируем в файл
                with open(self.log_file_path, "a", encoding="utf-8") as f:
                    f.write(f"{message}\n")
            else: # Если логируем в память
                self.in_memory_logs.append(message)

    def create_monitoring_tab(self):
        try:
            # Основной фрейм
            main_frame = ttk.Frame(self.monitoring_tab, style="TInstall.TFrame")
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Верхняя панель управления
            control_frame = ttk.Frame(main_frame, style="TInstall.TFrame")
            control_frame.pack(fill="x", pady=(0, 10))

            # Вставляем выпадающий список и надпись слева
            save_options = ["Сохранять в ОЗУ", "Сохранять в файл"]
            self.save_var = tk.StringVar(value=save_options[0])

            save_frame = ttk.Frame(control_frame)
            save_frame.pack(side="left", padx=5)

            ttk.Label(save_frame, text="Куда сохранять лог:", style="TInstall.TLabel").pack(side="left")
            self.save_option_menu = ttk.OptionMenu(save_frame, self.save_var, save_options[0], *save_options)
            self.save_option_menu.pack(side="left", padx=5)

            # Информация о выбранной программе
            self.exe_info_label = ttk.Label(control_frame, text="Программа не выбрана", style="TInstall.TLabel", font=("Default", 9, "bold"))
            self.exe_info_label.pack(side="left", padx=5)

            # Кнопки управления
            btn_frame = ttk.Frame(control_frame, style="TInstall.TFrame")
            btn_frame.pack(side="right")

            ttk.Button(btn_frame, text="Выбрать программу", style="TInstall.TButton", command=self._choose_install_exe).pack(side="left", padx=5)

            self.monitor_btn = ttk.Button(btn_frame, text="▶ Начать мониторинг", style="TInstall.TButton", command=self._start_install_monitoring, state="disabled")
            self.monitor_btn.pack(side="left", padx=5)

            # Кнопка сохранения логов
            self.save_btn = ttk.Button(btn_frame, text="💾 Сохранить логи", style="TInstall.TButton", command=self._save_installation_logs, state="disabled")
            self.save_btn.pack(side="left", padx=5)

            # Notebook для разных типов мониторинга
            self.monitor_notebook = ttk.Notebook(main_frame, style="TInstall.TNotebook")
            self.monitor_notebook.pack(fill="both", expand=True)

            # внутри create_monitoring_tab
            self.log_frames = {}
            # Создаем вкладки
            tabs = {
                "filesystem": ("Файловая система", self._create_scrollable_log),
                "registry": ("Реестр", self._create_scrollable_log),
                "process": ("Процессы", self._create_scrollable_log),
                "network": ("Сеть", self._create_scrollable_log),
                "resources": ("Ресурсы", self._create_scrollable_log),
                # "summary": ("Сводка", self._create_summary_tab)
            }
            for key, (title, creator) in tabs.items():
                frame = ttk.Frame(self.monitor_notebook, style="TInstall.TFrame")
                if creator == self._create_scrollable_log:
                    self._create_scrollable_log(frame)
                    self.log_frames[key] = frame
                # elif creator == self._create_summary_tab:
                #     creator(frame)
                #     self.log_frames[key] = frame
                self.monitor_notebook.add(frame, text=title)

            # Статус бар
            self.status_bar = ttk.Label(
                main_frame,
                text="Готов к работе",
                style="TInstall.TLabel",
                relief="sunken",
                anchor="w"
            )
            self.status_bar.pack(fill="x", pady=(5, 0))

            # Инициализация переменных
            self.monitored_process = None
            self.observer = None
            self.monitoring_active = False
            self.installation_logs = {key: [] for key in tabs.keys()}
            self.log_file_path = None
            self.in_memory_logs = [] #  Для хранения логов в памяти

        except Exception as e:
            logger.exception(f'SIM - {l("error")}')
            messagebox.showerror(RS(), f"Не удалось создать вкладку мониторинга:\n{e}")

    def create_filesystem_tab(self, parent_frame):
        self._create_scrollable_log(parent_frame)
        filter_frame = ttk.Frame(parent_frame, style="TInstall.TFrame")
        filter_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(filter_frame, text="Поиск:", style="TInstall.TLabel").pack(side="left")
        self.fs_filter = ttk.Entry(filter_frame)
        self.fs_filter.pack(side="left", fill="x", expand=True, padx=5)
        self.fs_filter.bind("<Return>", lambda e: self._filter_logs("filesystem"))

    # def _create_summary_tab(self, parent_frame):
    #     self._create_scrollable_log(parent_frame)
    #     btn_frame = ttk.Frame(parent_frame, style="TInstall.TFrame")
    #     btn_frame.pack(fill="x", pady=(5, 0))
    #     ttk.Button(btn_frame, text="📊 Сгенерировать отчет", style="TInstall.TButton", command=self._generate_install_report).pack()

    def _create_scrollable_log(self, parent_frame):
        canvas = tk.Canvas(parent_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        log_frame = ttk.Frame(canvas, style="TInstall.TFrame")
        canvas.create_window((0, 0), window=log_frame, anchor="nw")
        log_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        parent_frame.canvas = canvas
        parent_frame.log_frame = log_frame
        parent_frame.log_lines = []

    def _choose_install_exe(self):
        file_path = filedialog.askopenfilename(title=RS(), filetypes=[("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")])
        if file_path:
            self.exe_path = file_path
            self.exe_info_label.config(text=f"Выбрано: {os.path.basename(file_path)}")
            self.monitor_btn.config(state="normal")
            self._update_status("Программа выбрана. Готов к мониторингу")

    def _start_install_monitoring(self):
        if not hasattr(self, "exe_path") or not self.exe_path:
            messagebox.showwarning(RS(), "Выберите программу")
            return

        if self.monitoring_active:
            self._stop_install_monitoring()
            return

        # Проверяем выбранный вариант сохранения
        save_option = self.save_var.get()
        if save_option == "Сохранять в файл":
            log_dir = filedialog.asksaveasfilename(title=RS(),defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt")])
            if not log_dir: # Если пользователь отменил выбор файла
                return
            os.makedirs(os.path.dirname(log_dir), exist_ok=True) # Создаем директорию, если она не существует
            self.log_file_path = log_dir
            # Записываем шапку в файл
            with open(self.log_file_path, "w", encoding="utf-8") as f:
                f.write(f"=== Лог установки {os.path.basename(self.exe_path)} ===\n")
                f.write(f"Время начала: {datetime.datetime.now()}\n")
                f.write(f"Путь к файлу: {self.exe_path}\n")
        else:
            # В память
            self.log_file_path = None
            self.in_memory_logs.clear()
            self.installation_logs = {key: [] for key in self.installation_logs}

        # Очистка логов
        for frame in self.log_frames.values():
            for widget in frame.log_frame.winfo_children():
                widget.destroy()
            frame.log_lines.clear()

        self.monitoring_active = True
        self.monitor_btn.config(text="■ Остановить мониторинг")
        self.save_btn.config(state="normal")
        self._update_status(">>>Мониторинг запущен")

        # Запускаем мониторинг реестра, если он еще не запущен
        self._start_registry_monitoring()

        threading.Thread(target=self._run_install_monitoring, daemon=True).start()

    def _run_install_monitoring(self):
        try:
            self._add_log_entry(">>>Запуск программы...", "header", "process")
            # Используем shell=True для корректной работы с путями, содержащими пробелы, но с CREATE_NO_WINDOW
            self.monitored_process = subprocess.Popen([self.exe_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
            pid = self.monitored_process.pid
            proc = psutil.Process(pid)
            self._add_log_entry(f'>>>PID процесса: {pid}", "info", "process')
            self._setup_filesystem_monitoring()
            # _setup_registry_monitoring вызывается в _start_install_monitoring

            while self.monitoring_active and proc.is_running():
                self._monitor_child_processes(proc)
                self._monitor_open_files(proc)
                self._monitor_network_activity(proc)
                self._monitor_resources(proc)
                self._read_process_output()
                time.sleep(1)
            if self.monitoring_active:
                self._add_log_entry(">>>Программа завершила работу", "success", "process")
                self._generate_install_summary()
                self._update_status(">>>Мониторинг завершен")
        except FileNotFoundError:
            self._add_log_entry(f'[!] Ошибка: Файл "{self.exe_path}" не найден.', "error", "process")
            self._update_status(f'[!] Ошибка: Файл "{self.exe_path}" не найден.')
            self.monitoring_active = False # Останавливаем мониторинг, если файл не найден
        except Exception as e:
            logger.exception(f"SIM - Ошибка мониторинга")
            self._add_log_entry(f'>>> [!] Ошибка мониторинга:\n{e}", "error", "process')
            self._update_status(f"[!] Ошибка: {e}")
        finally:
            self.monitoring_active = False
            if self.observer:
                self.observer.stop()
                self.observer.join()
            if hasattr(self, "monitored_process") and self.monitored_process and self.monitored_process.poll() is None: #  Проверяем, жив ли процесс перед terminate
                self.monitored_process.terminate()
            self._stop_registry_monitoring() # Останавливаем мониторинг реестра при завершении основного мониторинга
            self.monitor_btn.config(text="▶ Начать мониторинг")
            self.save_btn.config(state="disabled")

    def _stop_install_monitoring(self):
        self.monitoring_active = False
        self.monitor_btn.config(text="▶ Начать мониторинг")
        # Прерываем процессы
        all_pids = [proc.pid for proc in psutil.process_iter()]
        action_process(False, all_pids, "kill", False)
        self._stop_registry_monitoring() # Останавливаем мониторинг реестра
        self._update_status(">>>Мониторинг остановлен")

    def _setup_filesystem_monitoring(self):
        self._add_log_entry(">>>Начало мониторинга файловой системы", "header", "filesystem")
        class InstallHandler(FileSystemEventHandler):
            def __init__(self, parent):
                self.parent = parent
            def on_created(self, event):
                if self.parent.monitoring_active:
                    self.parent._add_log_entry(f'📂 Создан: {event.src_path}", "file_event", "filesystem')
            def on_deleted(self, event):
                if self.parent.monitoring_active:
                    self.parent._add_log_entry(f'🗑 Удален: {event.src_path}", "file_event", "filesystem')
            def on_modified(self, event):
                if self.parent.monitoring_active and not event.is_directory:
                    self.parent._add_log_entry(f'✏ Изменён: {event.src_path}", "file_event", "filesystem')
        self.observer = Observer()

        watch_dirs = []
        # Проверяем все диски, доступные в системе
        for d in "ABCDEFGHIJKLMNOPQRSTUVWXXYZ":
            drive_path = f"{d}:\\"
            if os.path.exists(drive_path):
                watch_dirs.append(drive_path)

        # Перед добавлением директории в наблюдение
        for directory in watch_dirs:
            try:
                self.observer.schedule(InstallHandler(self), path=directory, recursive=True)
            except:
                logger.exception(f"SIM - Не удалось добавить директорию для мониторинга {directory}")

        self.observer.start()

    def _monitor_child_processes(self, parent_proc):
        try:
            for child in parent_proc.children(recursive=True):
                self._add_log_entry(f'>>>Подпроцесс: {child.name()} (PID: {child.pid})", "process_info", "process')
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _monitor_open_files(self, proc):
        try:
            #  Используем net_connections() вместо connections()
            open_files = proc.open_files()
            for f in open_files:
                self._add_log_entry(f'📄 Открыт файл: {f.path}", "file_access", "filesystem')
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _monitor_network_activity(self, proc):
        try:
            # Используем net_connections() вместо connections()
            connections = proc.net_connections()
            for conn in connections:
                if conn.status == psutil.CONN_ESTABLISHED:
                    self._add_log_entry(f'🌐 Соединение: {conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port}", "network_activity", "network')
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _monitor_resources(self, proc):
        try:
            cpu_percent = proc.cpu_percent()
            memory_info = proc.memory_info()
            self._add_log_entry(f'CPU: {cpu_percent}%, RAM: {memory_info.rss / 1024 / 1024:.2f} MB", "resource_usage", "resources')
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _read_process_output(self):
        if not self.monitored_process:
            return
        stdout = self.monitored_process.stdout
        if stdout:
            try:
                output = stdout.readline()
                if output:
                    self._add_log_entry(f'ℹ️ Вывод: {output.decode(errors="replace").strip()}", "process_output", "process')
            except ValueError: # Обработка случая, когда процесс уже завершился
                pass
        stderr = self.monitored_process.stderr
        if stderr:
            try:
                error = stderr.readline()
                if error:
                    self._add_log_entry(f'[!] Ошибка: {error.decode(errors="replace").strip()}", "process_error", "process')
            except ValueError: # Обработка случая, когда процесс уже завершился
                pass

    def _add_log_entry(self, message, log_type, log_category):
        if not self.monitoring_active and log_category != "summary": # Не добавляем логи, если мониторинг остановлен, кроме сводки
            return
        frame = self.log_frames.get(log_category)
        if not frame:
            return
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        label = ttk.Label(frame.log_frame, text=full_message, style="TInstall.TLabel", anchor="w", font=("Default", 9))
        label.pack(fill="x", padx=5, pady=2)
        frame.log_frame.update_idletasks()
        frame.canvas.yview_moveto(1.0)
        frame.log_lines.append(label)
        # Добавляем в соответствующую структуру логов
        if self.log_file_path:
            # Лог в файл
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(f"{full_message}\n")
        else:
            # Лог в память
            self.in_memory_logs.append(full_message)

    def _update_status(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"[{timestamp}] {message}")

    def _save_installation_logs(self):
        if not self.in_memory_logs and not self.log_file_path:
            messagebox.showwarning(RS(), "Нет данных для сохранения")
            return

        save_path = filedialog.asksaveasfilename(title=RS(),defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt")])
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write("=== Отчёт Об Установке ===\n\n")
                    f.write(f"Программа: {os.path.basename(self.exe_path)}\n")
                    f.write(f"Время мониторинга: {datetime.datetime.now()}\n\n")
                    # Добавляем содержимое из in_memory_logs, если оно есть
                    if self.in_memory_logs:
                        for line in self.in_memory_logs:
                            f.write(line + "\n")
                    # Если логировалось в файл, то файл уже содержит данные
                    elif self.log_file_path and os.path.exists(self.log_file_path):
                        with open(self.log_file_path, "r", encoding="utf-8") as infile:
                            f.write(infile.read())

                messagebox.showinfo(RS(), f"Отчет сохранен: {save_path}")
                os.startfile(os.path.dirname(save_path))
            except Exception as e:
                logger.exception(f"SIM - Ошибка при сохранении отчёта")
                messagebox.showerror(RS(), f"Не удалось сохранить файл:\n{e}")
        else:
            # Отмена
            pass

    def _generate_install_summary(self):
        installed_files = []
        modified_files = []
        for entry in self.in_memory_logs:
            if "Создан:" in entry:
                installed_files.append(entry.split("Создан:")[1].strip())
            elif "Изменен:" in entry:
                modified_files.append(entry.split("Изменен:")[1].strip())
        summary = [
            "=== Сводка Установки ===",
            f"Программа: {os.path.basename(self.exe_path)}",
            f"Всего создано файлов: {len(installed_files)}",
            f"Всего изменено файлов: {len(modified_files)}",
            "\n\n=== Основные Директории ==="
        ]
        dir_stats = {}
        for file in installed_files:
            dir_name = os.path.dirname(file)
            dir_stats[dir_name] = dir_stats.get(dir_name, 0) + 1
        for dir_path, count in sorted(dir_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary.append(f"{dir_path} - {count} файлов")
        for line in summary:
            self._add_log_entry(line, "info", "summary")

    # def _generate_install_report(self):
    #     self._save_installation_logs()

    def _filter_logs(self, category):
        filter_text = self.fs_filter.get().lower()
        frame = self.log_frames.get(category)
        if not frame:
            return
        for label in frame.log_lines:
            text = label.cget("text").lower()
            if filter_text in text:
                label.pack(fill="x", padx=5, pady=2)
            else:
                label.pack_forget()

def SIM(RUN_IN_RECOVERY=False, current_theme=False, DEBUG_MODE=False):
    if RUN_IN_RECOVERY:
        if not messagebox.askyesno(RS(), "Тесты данного Компонента в среде восстановления не проводились\nЗапустить его?"):
            return
    SIM_GUI = tk.Tk()
    apply_global_theme(SIM_GUI, current_theme)
    app = SoftwareInstallManager(SIM_GUI)
    SIM_GUI.mainloop()
