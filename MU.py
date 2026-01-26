#Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
#Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
#ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
#В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
#ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
#Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
#Или в файле COPYING.txt в архиве с установщиком
#Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
#Coded by @AnonimNEO (Telegram)

#Интерфейс
from tkinter import ttk, Label, Button, messagebox
import tkinter as tk
#Логирование Ошибок
from loguru import logger

#Импорт Компонентов
from ARM import ARM
from CC import CC
from FM import FM
from FR import FR
from OF import check_first_run, run_lp, run_obpc, open_with, get_current_disc
from PM import PM
from R import R
from RS import random_string
from Run import Run
from SP import SP
from UA import UA
from UM import UM

global settings_path, animation_txt, animation_default, unlocker_version
unlocker_version = "2.0.2 Beta"

@logger.catch
def MU(run_in_recovery, first_run):
    if first_run:
        messagebox.showinfo(random_string(), "Данное окно будет автоматически появляться в среде восстановления или при ошибке создания иконки в трейе.")

    try:
        mount_unlocker = tk.Tk()
        mount_unlocker.focus_force()
        style = ttk.Style()
        style.theme_use("clam")
        mount_unlocker.geometry("750x300")
        mount_unlocker.resizable(False, False)
        mount_unlocker.title(random_string())

        tab_control = ttk.Notebook(mount_unlocker)

        tab_components = ttk.Frame(tab_control)
        tab_control.add(tab_components, text="Компоненты")
        tab_utilities = ttk.Frame(tab_control)
        tab_control.add(tab_utilities, text="Утилиты")
        tab_protect = ttk.Frame(tab_control)
        tab_control.add(tab_protect, text="Защита")
        tab_other = ttk.Frame(tab_control)
        tab_control.add(tab_other, text="Прочее")

        Label(tab_components, text="Компоненты", font="Default 24").grid(row=0, column=0)

        Button(tab_components, text="Мастер Автозагрузки", font="Default 24", command=lambda:ARM(run_in_recovery, first_run)).grid(row=1, column=0)
        Button(tab_components, text="Менеджер Процессов", font="Default 24", command=lambda:PM(run_in_recovery, first_run)).grid(row=1, column=1)
        Button(tab_components, text="Файловый Менеджер", font="Default 24", command=lambda:FM(run_in_recovery, first_run)).grid(row=2, column=0)
        Button(tab_components, text="Разблокировка Всего", font="Default 24", command=lambda:UA(run_in_recovery, first_run)).grid(row=2, column=1)

        Label(tab_utilities, text="Утилиты", font="Default 24").grid(row=0, column=0)

        Button(tab_utilities, text="Замена Setch и Utilman", font="Default 24", command=FR).grid(row=1, column=0)
        Button(tab_utilities, text="     Очистка Temp       ", font="Default 24", command=lambda:CC(run_in_recovery, first_run)).grid(row=1, column=1)
        Button(tab_utilities, text="     Запуск от имени администратора    ", font="Default 15", command=lambda:Run(first_run)).grid(row=2, column=0)
        Button(tab_utilities, text="   Перезапустить ПК   ", font="Default 24", command=R).grid(row=2, column=1)
        Button(tab_utilities, text="Голосовое Управление", font="Default 24", command=lambda: run_obpc(run_in_recovery, first_run)).grid(row=3, column=0)
        Button(tab_utilities, text=" Открыть с помощью ", font="Default 24", command=lambda:open_with).grid(row=3, column=1)

        Label(tab_protect, text="Защита", font="Default 24").grid(row=0, column=0)

        if run_in_recovery:
            current_disc_r, found_disc = get_current_disc(run_in_recovery)
        else:
            current_disc_r = "C:\\"

        Button(tab_protect, text=" Защита Нагрузки " , font="Default 24", command=lambda:run_lp(run_in_recovery, first_run)).grid(row=1, column=0)
        Button(tab_protect, text="Пугало от вирусов" , font="Default 24", command=lambda:SP(run_in_recovery, first_run, current_disc_r)).grid(row=2, column=0)

        Label(tab_other, text="Прочее", font="Default 24").grid(row=0, column=0)

        Button(tab_other, text="Менеджер Пользователей", font="Default 24", command=UM).grid(row=1, column=0)
        Button(tab_other, text="Включить режим обучения", font="Default 24", command=lambda:check_first_run(delete=True)).grid(row=2, column=0)

        tab_control.pack(fill="both", expand=0)

        copyleft_label = tk.Label(mount_unlocker, text=f"Mount Unlocker {unlocker_version}", anchor="w")
        copyleft_label.pack(side="bottom", anchor="w", padx=10, pady=10)

        mount_unlocker.mainloop()
    except Exception as e:
        logger.critical(f"В Компоненте MountUnlocker произошла неизвестная ошибка!\n{e}")
