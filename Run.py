#Данное Свободное Программное Обеспечение распространяется по лицензии GPL-2.0-only или GPL-2.0-or-later
#Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату (в случае её распространения), но вы обязаны выкладывать исходный код своей версии программы!
#ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ - ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v2.0 или более поздней версии.
#В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ - ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ.
#ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ - ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО ПРЕДОСТАВЛЯЕТ ЛИЦЕНЗИЯ GPL.
#Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
#Или в файле COPYING в архиве с установщиком программы
#Copyleft 🄯 NEO Organization Departament K 2024 - 2025
#Coded by @AnonimNEO (Telegram)

#Логирование Ошибок
from loguru import logger
#Интерфейс
import tkinter as tk
#Работа с процессами
import subprocess
#Работа с файлами
import os

from RS import random_string

global user_name
run_version = "0.9.9 Beta"

@logger.catch
def Run():
    try:
        @logger.catch
        def start_file_with_admin(path):
            software = 1
            if path == "C:\\Windows\\System32\\gpedit.msc":
                os.startfile(path)
                software = 0
            if path == "C:\\Windows\\regedit.exe":
                os.startfile(path)
                software = 0
            if software == 1:
                try:
                    #Получаем имя текущего пользователя
                    username = os.getlogin()
                    logger.info(f"Run - Имя текущего пользователя: {username}")
                except Exception as e:
                    username = user_name
                    logger.error(f"Run - Не Удалось узнать имя пользователя!\n{e}")

                #Проверяем Существует ли файл
                if os.path.exists(path):
                    try:
                        #Запускаем Файл от имени администратора
                        subprocess.run(["runas", f"/user:{username}", path])
                    except Exception as e:
                        logger.error(f"Run - Ошибка при запуске файла {path}\n{e}")
                else:
                    logger.error(f"Run - не найден файл -{path}")

        def set_path(path):
            entry.delete(0, tk.END)
            entry.insert(0, path)

        def on_ok():
            path = entry.get()
            start_file_with_admin(path)

        run = tk.Tk()
        run.focus_force()
        run.title(random_string())
        run.geometry("350x150")
        run.configure(bg="#2E2E2E")

        entry = tk.Entry(run, width=50)
        entry.pack(pady=10)

        ok_button = tk.Button(run, text="ОК", command=on_ok, bg="#444444", fg="white")
        ok_button.pack(pady=10)

        buttons_frame = tk.Frame(run, bg="#2E2E2E")
        buttons_frame.pack(pady=10)

        buttons = {
            "CMD": "C:\\Windows\\System32\\cmd.exe",
            "REGEDIT": "C:\\Windows\\regedit.exe",
            "GPEDIT": "C:\\Windows\\System32\\gpedit.msc",
            "POWERSHELL": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
            "EXPLORER": "C:\\Windows\\explorer.exe"
        }

        for text, path in buttons.items():
            button = tk.Button(buttons_frame, text=text, command=lambda p=path: set_path(p), bg="#444444", fg="white")
            button.pack(side=tk.LEFT, padx=5)

        run.bind("<Return>", lambda event: on_ok())
        run.mainloop()

    except Exception as e:
        logger.critical(f"В Компоненте Run произошла неизвестная ошибка!\n{e}")