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
from tkinter import ttk, Menu
import tkinter as tk
#Логирование Ошибок
from loguru import logger

#Импорт Компонентов
from R import R
from UA import UA
from CC import CC
from SP import SP
from FM import FM
from PM import PM
from LP import LP
from Run import Run
from ARM import ARM
from OF import open_with
from RS import random_string


global settings_path, animation_txt, animation_default, unlocker_version
unlocker_version = "1.7.19 Beta"

@logger.catch
def MU(run_in_recovery):
    try:
        mount_unlocker = tk.Tk()
        mount_unlocker.focus_force()
        style = ttk.Style()
        style.theme_use("clam")
        mount_unlocker.geometry("370x320")

        mount_unlocker.title(random_string())
        header_text = "Монтировка Анлокер"
        header_label = tk.Label(mount_unlocker, font=("Arial", 32, "bold"))
        header_label.pack()

        #Каждая буква будет иметь свой цвет из радуги
        rainbow_colors = ["red", "orange", "yellow2", "green", "lightgreen", "blue", "skyblue", "violet"]

        def update_text_color(text, index, label):
            label.config(text=text[:index], fg=rainbow_colors[index % len(rainbow_colors)])
            mount_unlocker.after(150, update_text_color, text, index+1, label)

        update_text_color(header_text, 0, header_label)

        process_manager_button = tk.Button(mount_unlocker, text="Менеджер Процессов", command=lambda:PM(run_in_recovery), font=("Arial", 24))
        process_manager_button.pack()

        file_manager_button = tk.Button(mount_unlocker, text="Файловый Менеджер", command=lambda:FM(run_in_recovery), font=("Arial", 24))
        file_manager_button.pack()

        autoload_button = tk.Button(mount_unlocker, text="Мастер Автозагрузки", command=lambda:ARM(run_in_recovery), font=("Arial", 24))
        autoload_button.pack()

        unlock_button = tk.Button(mount_unlocker, text="Разблокировка всего", command=lambda:UA(run_in_recovery), font=("Arial", 24))
        unlock_button.pack()

        copyright_label = tk.Label(mount_unlocker, text=f"Mount Unlocker {unlocker_version}", anchor="w")
        copyright_label.pack(side="bottom", anchor="w", padx=10, pady=10)

        about_menu = tk.Menu(mount_unlocker)
        mount_unlocker.config(menu=about_menu)

        #Создание Меню
        main_menu = Menu(mount_unlocker)
        mount_unlocker.config(menu=main_menu)

        #Пункт "Утилиты"
        utilities_menu = Menu(main_menu, tearoff=0)
        main_menu.add_cascade(label="Утилиты", menu=utilities_menu)
        utilities_menu.add_command(label="Scarecrow Protection", command=lambda:SP(run_in_recovery))
        utilities_menu.add_command(label="Открыть С Помощью", command=open_with)
        utilities_menu.add_command(label="Запустить очистку Temp", command=lambda:CC(run_in_recovery))
        utilities_menu.add_command(label="Запустить LoadProtection", command=lambda:LP(run_in_recovery))
        utilities_menu.add_command(label="Запустить от имени Админа", command=Run)
        utilities_menu.add_command(label="Перезапустить ПК", command=R)

        mount_unlocker.mainloop()

    except Exception as e:
        logger.critical(f"В Компоненте MountUnlocker произошла неизвестная ошибка!\n{e}")