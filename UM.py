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
from tkinter import ttk, messagebox
import tkinter as tk
#Работа с пользователями
import subprocess
import os
#Логирование
from loguru import logger

from RS import random_string

users_manager_version = "0.1.7 Pre-Alpha"


def run_net_command(args):
    try:
        subprocess.run(["net"] + args, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"UM - Команда net завершилась с ошибкой:\n{e.stderr}")
        return False
    except Exception as e:
        logger.exception(f"UM - Системная ошибка при выполнении команды.\n{e}")
        return False



class UserManager:
    def __init__(self, master):
        self.master = master
        master.title(random_string())
        master.geometry("275x285")

        self.users = [] 
        self.current_username = os.getlogin() 

        self.create_widgets()
        self.load_users()



    def create_widgets(self):
        self.tree = ttk.Treeview(self.master, columns=("username",), show="headings")
        self.tree.heading("username", text="Имя пользователя")
        self.tree.column("username", width=275)
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=5)

        self.create_button = tk.Button(button_frame, text="Создать пользователя", command=self.create_user)
        self.create_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(button_frame, text="Удалить выбранных", command=self.delete_users)
        self.delete_button.pack(side=tk.LEFT, padx=5)



    def load_users(self):
        try:
            cmd = (
                "powershell -Command \"Get-LocalUser | "
                "Where-Object { $_.SID -like 'S-1-5-21-*' -and $_.Enabled -eq $true } | "
                "Select-Object -ExpandProperty Name\""
            )

            #Выполняем команду
            result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.PIPE, encoding='cp866')
            lines = result.strip().splitlines()

            system_blacklist = [
                "Administrator", "Администратор", 
                "Guest", "Гость", 
                "DefaultAccount", "WDAGUtilityAccount", 
                "UtilityAccount", "SystemAdmin"
            ]

            self.users = []
            for line in lines:
                name = line.strip()
                if name and not any(black.lower() == name.lower() for black in system_blacklist):
                    self.users.append(name)

            self.update_tree()

        except Exception as e:
            logger.exception("UM - Ошибка при загрузке списка пользователей")
            messagebox.showerror(random_string(), f"Не удалось загрузить пользователей:\n{e}")



    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for username in self.users:
            self.tree.insert("", tk.END, values=(username,))



    def create_user(self):
        create_window = tk.Toplevel(self.master)
        create_window.title(random_string())
        create_window.geometry("150x150")

        tk.Label(create_window, text="Имя пользователя:").pack(pady=2)
        username_entry = tk.Entry(create_window)
        username_entry.pack(pady=2)

        tk.Label(create_window, text="Пароль:").pack(pady=2)
        password_entry = tk.Entry(create_window, show="*")
        password_entry.pack(pady=2)

        def confirm_creation():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                messagebox.showwarning(random_string(), "Заполните все поля.")
                return

            if run_net_command(["user", username, password, "/add"]):
                logger.info(f"UM - Пользователь {username} создан.")
                self.load_users()
                create_window.destroy()
            else:
                messagebox.showerror(random_string(), "Ошибка при создании. Проверьте права администратора.")

        create_button = tk.Button(create_window, text="Создать", command=confirm_creation)
        create_button.pack(pady=10)



    def delete_users(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(random_string(), "Выберите пользователя.")
            return

        for item in selected_items:
            username = self.tree.item(item, "values")[0]
            if username.lower() == self.current_username.lower():
                messagebox.showwarning(random_string(), f"Нельзя удалить себя ({username}).")
                continue

            if run_net_command(["user", username, "/delete"]):
                logger.info(f"UM - Пользователь {username} удален.")
            else:
                logger.error(f"UM - Ошибка при удалении пользователя {username}.")

        self.load_users()



def UM():
    try:
        root = tk.Tk()
        app = UserManager(root)
        root.mainloop()
    except Exception as e:
        logger.critical(f"В Компоненте UsersManager произошла неизвестная ошибка!\n{e}")