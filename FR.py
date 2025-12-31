#Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
#Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
#ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
#В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
#ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
#Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
#Или в файле COPYING.txt в архиве с установщиком
#Copyleft 🄯 NEO Organization, Departament K 2024 - 2025
#Coded by @AnonimNEO (Telegram)

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from loguru import logger

from RS import random_string

file_replacer = "0.2.2 Beta"

def FR():
    def browse_source(source_var):
        path = filedialog.askopenfilename(title=random_string())
        if path:
            source_var.set(path)

    def browse_target(target_var):
        path = filedialog.askopenfilename(title=random_string())
        if path:
            target_var.set(path)

    def on_preset_select(event, combo, target_var, presets_dict):
        selected = combo.get()
        path = presets_dict.get(selected, "")
        if path:
            target_var.set(path)

    def replace_file(source_var, target_var):
        final_src = source_var.get()
        final_tgt = target_var.get()

        if not final_src or not os.path.exists(final_src):
            messagebox.showerror(random_string(), "Файл-источник не выбран или не найден!")
            return
        if not final_tgt:
            messagebox.showerror(random_string(), "Путь к цели не указан!")
            return

        backup_path = final_tgt + ".bak"

        try:
            #Создаем бэкап
            if os.path.exists(final_tgt):
                shutil.copy2(final_tgt, backup_path)
                logger.info(f"FR - Создан бэкап: {backup_path}")

            #Копируем новый файл на место старого
            shutil.copy2(final_src, final_tgt)
            logger.success(f"Заменено: {final_tgt}")
            messagebox.showinfo(random_string(), f"Файл заменен.\nБэкап создан в том же каталоге")
        except PermissionError:
            messagebox.showerror(random_string(), "Запустите программу от имени администратора.")
        except Exception as e:
            logger.error(f"FR - Ошибка при замене файла:\n{e}")
            messagebox.showerror(random_string(), e)

    def restore_file(target_var):
        final_tgt = target_var.get()
        if not final_tgt:
            messagebox.showwarning(random_string(), "Сначала выберите или укажите путь к файлу!")
            return
        
        backup_path = final_tgt + ".bak"
        if not os.path.exists(backup_path):
            messagebox.showwarning(random_string(), f"Бэкап не найден по пути:\n{backup_path}")
            return

        if messagebox.askyesno(random_string(), f"Восстановить {os.path.basename(final_tgt)} из бэкапа?"):
            try:
                #Возвращаем бэкап на место основного файла
                shutil.move(backup_path, final_tgt)
                logger.success(f"FR - Восстановлено из бэкапа: {final_tgt}")
                messagebox.showinfo(random_string(), "Файл успешно восстановлен.")
            except Exception as e:
                logger.error(f"FR - Ошибка при восстановлении файла:\n{e}")
                messagebox.showerror(random_string(), str(e))

    FR = tk.Tk()
    FR.title(random_string())
    FR.geometry("400x250")

    source_path = tk.StringVar()
    target_path = tk.StringVar()

    presets = {
        "Свой путь": "",
        "Sethc (Залипание клавиш)": "C:\\Windows\\System32\\sethc.exe",
        "Utilman (Спец. возможности)": "C:\\Windows\\System32\\utilman.exe",
        "Taskmgr (Диспетчер задач)": "C:\\Windows\\System32\\taskmgr.exe",
        "Explorer (Проводник)": "C:\\Windows\\explorer.exe"
    }

    #GUI элементы
    tk.Label(FR, text="1)На, что заменить:", font=('Segoe UI', 9, 'bold')).pack(anchor="w", padx=10, pady=(10, 0))
    src_frame = tk.Frame(FR)
    src_frame.pack(fill="x", padx=10)
    tk.Entry(src_frame, textvariable=source_path).pack(side="left", expand=True, fill="x")
    tk.Button(src_frame, text="Обзор", command=lambda: browse_source(source_path)).pack(side="right", padx=5)

    tk.Label(FR, text="2)Что заменяем:").pack(anchor="w", padx=10, pady=(10, 0))
    combo_presets = ttk.Combobox(FR, values=list(presets.keys()), state="readonly")
    combo_presets.pack(fill="x", padx=10)
    combo_presets.set("Выберите пресет...")
    combo_presets.bind("<<ComboboxSelected>>", lambda e: on_preset_select(e, combo_presets, target_path, presets))

    tgt_frame = tk.Frame(FR)
    tgt_frame.pack(fill="x", padx=10, pady=5)
    tk.Entry(tgt_frame, textvariable=target_path).pack(side="left", expand=True, fill="x")
    tk.Button(tgt_frame, text="Обзор", command=lambda: browse_target(target_path)).pack(side="right", padx=5)

    #Кнопки действий
    btn_frame = tk.Frame(FR)
    btn_frame.pack(pady=15)

    tk.Button(btn_frame, text="Заменить",
              command=lambda: replace_file(source_path, target_path), 
              bg="#ffcccc", width=15, font=('Segoe UI', 9, 'bold')).pack(side="left", padx=10)

    tk.Button(btn_frame, text="Восстановить",
              command=lambda: restore_file(target_path), 
              bg="#ccffcc", width=15).pack(side="left", padx=10)

    FR.mainloop()
