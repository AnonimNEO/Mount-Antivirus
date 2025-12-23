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
import tkinter as tk

#Логирование Ошибок
from loguru import logger
#Работа с временим
import time
#Работа с файлами и ОС
import ast
import os

from RS import random_string
from CC22 import CC22
from config import *

global load_protection_version, debug_mode, time_sleep_to_close_question, time_sleep_to_close_question2
load_protection_version = "2.2.12 Alpha"
debug_mode = True

def LP(run_in_recovery, debug_mode=False):
    if not run_in_recovery:
        import psutil
    else:
        psutil = Psutil()

    if not run_in_recovery:
        from EC import EC, get_process_critical_status
    else:
        def EC(i, c, d):
            pass
        def get_process_critical_status(i):
            return False

    def read_data_file(file, code):
        if not os.path.exists(file):
            if debug_mode:
                logger.info(f"LP - файла {file} не существует.")
            return exception_process
        try:
            with open(file, "r") as data:
                data_file = data.read()
            data_file_decrypt = CC22(str(data_file), code, True)
            data_list = ast.literal_eval(data_file_decrypt)
        except FileNotFoundError:
            data_list = []
            if debug_mode:
                logger.error(f"LP - файл {file}, внезапно исчез!")
        except Exception as e:
            data_list = []
            logger.error(f"LP - Неизвестная ошибка в функции read_data_file!\n{e}")

        return exception_process + data_list

    def save_data_file(file, code, process_name):
        if not os.path.exists(file):
            try:
                with open(file, "w") as data:
                    data.write('[""')
            except Exception as e:
                logger.error(f"LP - неизвестная ошибка при создании файла {file}, в функции cript_data_file\n{e}")
                return False
        try:
            with open(file, "r") as data:
                data_file = data.read()
            cript_process_name = CC22(process_name, code)
            if data_file:
                if data_file.endswith("]\n"):
                    data_file = data_file[:-2]
                elif data_file.endswith("]"):
                    data_file = data_file[:-1]
                else:
                    with open(file, "w") as data:
                        data.write('[""')
            with open(file, "w") as data:
                data.write(f'{data_file}, "{cript_process_name}"]')
            return True
        except FileNotFoundError:
            logger.error(f"LP - файл {file}, внезапно исчез!")
        except Exception as e:
            logger.error(f"LP - неизвестная ошибка при пополнении базы данных в файл {file}:\n{e}")

    #Вопрос следующего действия над процессом
    def question_process(process_name, process_id, cause, text, time_to_close_question):
        LP_PQ = tk.Tk()
        LP_PQ.withdraw()

        #Создание модального окна для вопроса
        dialog = tk.Toplevel(LP_PQ)
        dialog.title(random_string())

        tk.Label(dialog, text=text, wraplength=400, justify=tk.LEFT, padx=10, pady=10).pack()

        #Определение автоматического действия
        if cause == "name" or cause == "load":
            auto_action = "ignore"
            action_text = "проигнорирован"
        elif cause == "resume":
            auto_action = "ignore"
            action_text = "НЕ добавлен в базу исключений"

        #Переменная для хранения оставшегося времени
        remaining_time = tk.IntVar(value=time_to_close_question)

        #Label для отображения таймера
        timer_text_label = tk.Label(dialog,
                                    text=f"Процесс {process_name} будет {action_text} автоматически через {remaining_time.get()} сек.",
                                    fg="gray",
                                    wraplength=400,
                                    justify=tk.CENTER,
                                    pady=5)
        timer_text_label.pack()

        #Переменная для хранения выбора пользователя
        user_choice = tk.StringVar(value=auto_action) #Устанавливаем авто-действие как значение по умолчанию

        #Закрываем окно
        def close_dialog(action=auto_action):
            if dialog.winfo_exists(): #Проверка, что окно еще не закрыто
                user_choice.set(action)
                dialog.destroy()
                LP_PQ.quit()
            else:
                pass

        #Обновляем Таймер
        def update_timer():
            #Проверяем, существует ли еще виджет перед попыткой его обновить
            if not timer_text_label.winfo_exists():
                if debug_mode:
                    logger.info("LP - Виджет таймера уже закрыт. Останавливаем обновление.")
                return #Останавливаем рекурсивный вызов

            current_time = remaining_time.get()
            if current_time > 0:
                remaining_time.set(current_time - 1)
                #Обновляем текст на экране
                timer_text_label.config(
                    text=f"Процесс {process_name} будет {action_text}, автоматически через {remaining_time.get()} сек.")
                LP_PQ.after(1000, update_timer)
            else:
                #Время истекло, автоматически выполняем действие
                close_dialog(auto_action)

        #В зависимости от причины формируем кнопки
        if cause == "name" or cause == "load":
            #Кнопки для замороженного процесса
            tk.Button(dialog, text="Разморозить", command=lambda: close_dialog("resume")).pack(
                side=tk.LEFT, padx=5, pady=10)
            tk.Button(dialog, text=f"Закрыть (Критичность: {get_process_critical_status(process_id)})",
                      command=lambda: close_dialog("kill")).pack(side=tk.LEFT,
                                                                 padx=5, pady=10)
            tk.Button(dialog, text="Игнорировать", command=lambda: close_dialog("ignore")).pack(side=tk.LEFT,
                                                                                                padx=5, pady=10)
        elif cause == "resume":
            #Кнопки после разморозки
            tk.Button(dialog, text="Да, добавить в исключения", command=lambda: close_dialog("add_exception")).pack(
                side=tk.LEFT, padx=5, pady=10)
            tk.Button(dialog, text="Нет, не добавлять", command=lambda: close_dialog("ignore")).pack(side=tk.LEFT,
                                                                                                     padx=5,
                                                                                                     pady=10)

        #Центрирование окна
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        #Запускаем таймер сразу после открытия окна
        if time_to_close_question > 0:
            LP_PQ.after(1000, update_timer)

        LP_PQ.mainloop()

        return user_choice.get()

    def action_process(process_id, name_process, action, cause, text):
        if debug_mode:
            logger.info(f"LP - ID Процесса: {process_id}, Имя: {name_process}")
            logger.info(f"LP - Действие: {action}, Причина: {cause}")
            logger.info(f"LP - Сообщение: {text}")

        if action == "suspend":
            try:
                process = psutil.Process(process_id)
                process.suspend()
            except Exception as e:
                logger.critical(f"LP - Не удалось заморозить процесс {name_process} (PID: {process_id}):\n{e}")
                return False

            #Вызов окна и получение решения пользователя
            user_decision = question_process(name_process, process_id, cause, text, time_sleep_to_close_question)
            logger.info(f"LP - Для процесса {name_process} (PID: {process_id}), замороженный по причине {cause}, будет выполнено действие: {user_decision}")

            if user_decision == "kill":
                process = psutil.Process(process_id)
                process.terminate()
                logger.info(f"LP - Процесс {name_process} (PID: {process_id}) убит.")
                return True
            elif user_decision == "resume":
                action_process(process_id, name_process, "resume", "resume",
                               f"LP - Процесс {name_process} разморожен. Вы хотите добавить его в базу исключений?")
                return False  #Не удаляем из пула, так как он разморожен
            elif user_decision == "add_exception":
                save_data_file(exception_process_txt, clyth, name_process)
                read_data_file(exception_process_txt, clyth)
                return True
            elif user_decision == "ignore":
                #Процесс просто игнорируется, он не удаляется из пула
                #Иначе он исчезнет и не будет проверяться на нагрузку
                return False

            #Если не "kill", не "add_exception", и не "ignore" (например, "resume"),
            #и процесс был успешно разморожен (action_process(resume)), то мы возвращаем False,
            #чтобы он остался в пуле (действие "resume" не убивает процесс).
            #Если было выбрано "kill" или "add_exception", мы вернем True
            return True if user_decision == "kill" or user_decision == "add_exception" else False

        elif action == "resume":
            try:
                process = psutil.Process(process_id)
                process.resume()
            except Exception as e:
                logger.error(f"LP - Не удалось разморозить процесс {name_process} (PID: {process_id}):\n{e}")
                return False

            user_decision = question_process(name_process, process_id, cause, text, time_sleep_to_close_question2)

            if user_decision == "add_exception":
                save_data_file(exception_process_txt, clyth, name_process)
                read_data_file(exception_process_txt, clyth)
                return True
            return False
        return False



    #Получаем нагрузку процесса на RAN
    def get_ram_percentage(process_id, process_name):
        try:
            process = psutil.Process(process_id)
            process_mem_bytes = process.memory_info().rss
            mb_ram = process_mem_bytes / (1024 * 1024)

            return (process_mem_bytes / total_ram) * 100

            #Округляем процент до 2 знаков после запятой, МБ - до целого числа
            ram_percent_str = f"{ram_percent:.2f}"
            mb_ram_str = f"{mb_ram:.0f}"

            #Возвращаем строку в требуемом формате
            return f"{ram_percent_str} {mb_ram_str}"
        except psutil.NoSuchProcess:
            if debug_mode:
                logger.error(f"LP - Процесс {process_name} (PID: {process_id}) закрылся во время проверки")
        except PermissionError:
            logger.error(f"LP - Ошибка доступа при получении RAM для процесса {process_name} (PID: {process_id})")
        except Exception as e:
            logger.critical(f"LP - неизвестная ошибка при получении RAM  для процесса {process_name} (PID: {process_id})\n{e}")



    #Удаляем расширение файла в имени процесса
    def get_base_name(name):
        return name.rsplit(".", 1)[0]

    #Получаем список всех процессов
    def get_all_processes():
        if debug_mode:
            logger.info(f"LP - Получение списка всех процессов...")
        try:
            return list(psutil.process_iter(["pid", "name"]))
        except psutil.AccessDenied:
            logger.critical(f"LP - Не удалось получить доступ к списку процессов.")
            return False

    #Отсеиваем процессы из базы исключений
    def filter_exceptions(processes, exceptions):
        if debug_mode:
            logger.info(f"LP - Фильтрация исключений...")
        filtered_processes = [p for p in processes if p.info["name"] not in exceptions]
        return filtered_processes

    #Проверка имени процесса по базе
    def check_bad_names(processes, bad_names):
        if debug_mode:
            logger.info(f"LP - Проверка имени по базе...")
        rest_processes = []

        for p in processes:
            process_name = p.info["name"]
            process_name_lower = process_name.lower() #Используем полное имя процесса в нижнем регистре
            process_id = p.info["pid"]

            is_bad = False
            for bad_word in bad_names:
                #Проверяем, содержится ли "плохое" слово в полном имени процесса
                if bad_word.lower() in process_name_lower:
                    text = f'Процесс {process_name} заморожен из-за его подозрительного имени. Из-за слова "{bad_word}".'
                    #action_process возвращает True, если процесс убит или заморожен
                    if action_process(process_id, process_name, "suspend", "name", text):
                        logger.info(f"LP - Процесс {process_name} (PID: {process_id}) удален из дальнейшего пула.")
                        is_bad = True
                        break

            if not is_bad:
                rest_processes.append(p)

        return rest_processes



    #Проверка на нагрузку процессов на компоненты ПК
    def check_resource_load(processes):
        for p in processes:
            process_name = p.info["name"]
            process_id = p.info["pid"]
            is_high_load = False

            try:
                #Получение данных
                cpu_percent = p.cpu_percent(interval=0.1) #Интервал нужен для корректного расчета
                ram_mb = p.memory_info().rss / (1024 * 1024)
                ram_percent = get_ram_percentage(process_id, process_name)

                #Проверка допустимого порога CPU
                if cpu_percent > ultimate_load_cpu:
                    text = f"Процесс {process_name} избыточно нагружает Процессор на {cpu_percent:.2f}%."
                    if action_process(process_id, process_name, "suspend", "load", text):
                        is_high_load = True

                #Проверка порога RAM (если ещё не заморожен)
                if not is_high_load:
                    if ram_percent > ultimate_load_ram:
                        text = f"Процесс {process_name} избыточно нагружает Оперативную Память на {ram_percent:.2f}% ({ram_mb:.2f} MB)."
                        if action_process(process_id, process_name, "suspend", "load", text):
                            is_high_load = True

            except psutil.NoSuchProcess:
                #Процесс мог закрыться, пока происходила проверка
                if debug_mode:
                    logger.error(f"LP - Процесс {process_name} (PID: {process_id}) закрылся во время проверки.")
            except psutil.AccessDenied:
                pass
            except Exception as e:
                logger.critical(f"LP - Неизвестная ошибка при проверке процесса {process_name} (PID: {process_id}):\n{e}")
                pass
        return True


    try:
        if debug_mode:
            logger.info(f"LP - ВКЛЮЧЕН DEBUG МОД")
        global exception_process, bad_process, total_ram
        total_ram = psutil.virtual_memory().total
        exception_process = read_data_file(exception_process_txt, clyth)
        bad_process = read_data_file(bad_process_txt, clyth)
        while True:
            #Получение всех процессов
            all_processes = get_all_processes()

            #Фильтрация исключений
            filtered_processes = filter_exceptions(all_processes, exception_process)

            #Проверка на плохие имена
            processes_after_name_check = check_bad_names(filtered_processes, bad_process)

            #Проверка на избыточную нагрузку
            check_resource_load(processes_after_name_check)
            time.sleep(time_sleep_to_scan)
    except Exception as e:
        logger.critical("LP - В Компоненте LoadProtection произошла неизвестная ошибка!")