# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

# Интерфейс
from tkinter import ttk, messagebox, Menu, simpledialog
import tkinter as tk
# Работа с пользователями
import subprocess
import os
import threading
# Логирование
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger

from languages import l
from OF import pac, apply_global_theme, create_menubar
from RS import RS

USER_MANAGER_VERSION = "0.3.12 Beta"

class UserManager:
    def run_net_command(self, args):
        try:
            result = subprocess.run(
                ["net"] + args, 
                capture_output=True, 
                text=True, 
                check=True, 
                creationflags=subprocess.CREATE_NO_WINDOW,
                encoding="cp1251"
            )
            return True
        except subprocess.CalledProcessError as e:
            # Парсим stderr в правильной кодировке
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f'UM - {l("net_error")}:\n{error_msg}')
            return False
        except Exception as e:
            logger.exception(f'UM - {l("system_command_error")}.')
            return False

    def __init__(self, UM_GUI):
        self.UM_GUI = UM_GUI
        UM_GUI.title(RS())
        UM_GUI.geometry("400x375")

        self.users = [] 
        self.current_username = os.getlogin() 

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        self.tree = ttk.Treeview(self.UM_GUI, columns=("username",), show="headings")
        self.tree.heading("username", text=l("user_name"))
        self.tree.column("username", width=275)
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self.UM_GUI)
        button_frame.pack(pady=5)

        self.create_button = tk.Button(button_frame, text=l("create_user"), command=self.create_user)
        self.create_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(button_frame, text=l("delete_users"), command=self.delete_users)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.reset_password_button = tk.Button(button_frame, text=l("change_password"), command=self.reset_password)
        self.reset_password_button.pack(side=tk.LEFT, padx=5)



    def load_users(self):
        try:
            cmd = (
                "powershell -Command \"Get-LocalUser | "
                "Where-Object { $_.SID -like 'S-1-5-21-*' -and $_.Enabled -eq $true } | "
                "Select-Object -ExpandProperty Name\""
            )

            # Выполняем команду PowerShell
            try:
                result = subprocess.check_output(
                    cmd, 
                    shell=True, 
                    stderr=subprocess.DEVNULL,  # Игнорируем stderr вместо захвата
                    encoding='utf-8'
                )
                lines = result.strip().splitlines()
            except:
                cmd = 'wmic useraccount where "Disabled=0 and LocalAccount=1" get Name /format:list'
                result = subprocess.check_output(
                    cmd, 
                    shell=True, 
                    stderr=subprocess.DEVNULL,
                    encoding="cp1251"
                )
                lines = result.strip().splitlines()

            system_blacklist = [
                "Administrator", l("admin"),
                "Guest", l("guest"),
                "DefaultAccount", "WDAGUtilityAccount", 
                "UtilityAccount", "SystemAdmin"
            ]

            self.users = []
            for line in lines:
                name = line.strip()
                
                # Если строка в формате "Name=username" (от wmic), извлеките только username
                if "=" in name:
                    name = name.split("=", 1)[1].strip()

                if name and not any(black.lower() == name.lower() for black in system_blacklist):
                    self.users.append(name)

            self.update_tree()

        except Exception as e:
            logger.exception(f'UM - {l("get_user_list_error")}')
            messagebox.showerror(RS(), f'{l("get_user_list_error")}:\n{e}')



    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for username in self.users:
            self.tree.insert("", tk.END, values=(username,))



    def create_user(self):
        create_window = tk.Toplevel(self.UM_GUI)
        create_window.title(RS())
        create_window.geometry("150x150")
        create_window.attributes("-topmost", True)

        tk.Label(create_window, text=l("user_name")).pack(pady=2)
        username_entry = tk.Entry(create_window)
        username_entry.pack(pady=2)

        tk.Label(create_window, text=l("password")).pack(pady=2)
        password_entry = tk.Entry(create_window, show="*")
        password_entry.pack(pady=2)

        def confirm_creation():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                messagebox.showwarning(RS(), l("enter_all_data"))
                return

            try:
                self.run_net_command(["user", username, password, "/add"])
                logger.success(f'UM - {l("user")} {username} {l("success_create")}.')
                self.load_users()
                create_window.destroy()
            except Exception as e:
                comment = f'UM - {l("create_user_error")} {username}'
                logger.exception(comment)
                messagebox.showerror(RS(), comment)

        create_button = tk.Button(create_window, text=l("create_user"), command=confirm_creation)
        create_button.pack(pady=10)



    def delete_users(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(RS(), l("select_user"))
            return

        for item in selected_items:
            username = self.tree.item(item, "values")[0]
            if username.lower() == self.current_username.lower():
                messagebox.showwarning(RS(), f'{l("cant_delete_self")} ({username})!\n{l("what_did_you")}!')
                continue

            if self.run_net_command(["user", username, "/delete"]):
                logger.info(f'UM - {l("user")} {username} {l("deleted")}.')
            else:
                comment = f'{l("delete_user_error")} {username}.'
                logger.error(f"UM - {comment}")
                messagebox.showerror(RS(), comment)

        self.load_users()



    def reset_password(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(RS(), l("select_user"))
            return

        # Диалог для ввода нового пароля
        password_dialog = tk.Toplevel(self.UM_GUI)
        password_dialog.title(RS())
        password_dialog.geometry("250x120")
        password_dialog.transient(self.UM_GUI)
        password_dialog.grab_set()

        tk.Label(password_dialog, text=l("enter_new_password")).pack(pady=10)
        password_entry = tk.Entry(password_dialog, show="*")
        password_entry.pack(pady=5, padx=10, fill=tk.X)

        def confirm_reset():
            new_password = password_entry.get().strip()
            
            if not new_password:
                messagebox.showwarning(RS(), f'{l("password")} {l("not_empty")}')
                return

            password_dialog.destroy()

            for item in selected_items:
                username = self.tree.item(item, "values")[0]

                thread = threading.Thread(target=self._do_reset_password, args=(username, new_password))
                thread.daemon = True
                thread.start()

        confirm_button = tk.Button(password_dialog, text=l("reset"), command=confirm_reset)
        confirm_button.pack(pady=10)

        password_entry.focus()
        password_entry.bind("<Return>", lambda e: confirm_reset())



    def _do_reset_password(self, username, new_password):
        try:
            comment = f'{l("change_password_error")} {username}.'
            if self.run_net_command(["user", username, new_password]):
                logger.info(f'UM - {l("password_for_user")} {username} {l("reset2")}.')
            else:
                logger.error(f"UM - {comment}")
                messagebox.showerror(RS(), comment)
        except Exception as e:
            comment = f'{l("change_password_error")} {username}'
            logger.exception(f"UM - {comment}")
            messagebox.showerror(RS(), comment)



def UM(current_theme=False, DEBUG_MODE=False):
    try:
        UM_GUI = tk.Tk()

        create_menubar(UM_GUI, False, DEBUG_MODE=DEBUG_MODE)

        apply_global_theme(UM_GUI, current_theme)

        UserManager(UM_GUI)
        UM_GUI.mainloop()
    except Exception as e:
        logger.exception(l("um_critical_error"))

if __name__ == "__main__":
    from config import THEME, DEFAULT_THEME
    current_theme = THEME[DEFAULT_THEME]
    UM(current_theme)
