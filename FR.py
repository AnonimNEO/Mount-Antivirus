# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

FILE_REPLACER_VERSION = "0.4.10 Beta"

def FR(RUN_IN_RECOVERY=False, current_theme=False, DEBUG_MODE=False):
    # Интерфейс
    from tkinter import filedialog, messagebox, ttk, Menu
    import tkinter as tk
    # Логирование
    try:
        from OF import Logger
        logger = Logger()
    except:
        from loguru import logger
    # Работа с файлами
    import subprocess
    import shutil
    import os

    from GFA import GFA
    from RS import RS
    from OF import pac, apply_global_theme, get_current_disc, create_menubar
    from languages import l

    def browse_source(source_var):
        path = filedialog.askopenfilename(title=RS())
        if path:
            source_var.set(path)

    def browse_target(target_var):
        path = filedialog.askopenfilename(title=RS())
        if path:
            target_var.set(path)

    def on_preset_select(event, combo, target_var, presets_dict):
        selected = combo.get()
        path = presets_dict.get(selected, "")
        if path:
            target_var.set(path)

    def replace_file(source_var, target_var):
        try:
            GFA(source_var, RUN_IN_RECOVERY)
            GFA(target_var, RUN_IN_RECOVERY)
        except:
            pass
        final_src = source_var.get()
        raw_target = target_var.get()

        current_disc, found_disc = get_current_disc(RUN_IN_RECOVERY)

        if not found_disc:
            current_disc = "C:\\"

        if raw_target.startswith("C:"):
            final_tgt = raw_target.replace("C:", current_disc)
        else:
            final_tgt = raw_target

        if not final_src or not os.path.exists(final_src):
            messagebox.showerror(RS(), f'{l("file")} {l("not_found")}')
            return

        try:
            # Получаем права собственности (для WinRE)
            # /F - путь к файлу, /A - передать права группе администраторов
            subprocess.run(f'takeown /f "{final_tgt}" /a', shell=True, check=False)
            
            # Даем полные права администраторам
            # /grant - предоставить права, :F - Full access (полный доступ)
            subprocess.run(f'icacls "{final_tgt}" /grant administrators:F', shell=True, check=False)

            # Создаем бэкап
            backup_path = final_tgt + ".backup"
            if os.path.exists(final_tgt):
                shutil.copy2(final_tgt, backup_path)
                logger.info(f'FR - {l("create_backup")}: {backup_path}')

            # Копируем новый файл
            shutil.copy2(final_src, final_tgt)
            logger.success(f'FR - {l("success")} {l("replaced")}: {final_tgt}')
            messagebox.showinfo(RS(), f'{l("file")} {l("replaced")} {l("on_disc")} {current_disc}')

        except Exception as e:
            logger.exception(f'FR - {l("error")}')
            messagebox.showerror(RS(), f'{l("replace_file_not_found")}:\n{e}')

    def restore_file(target_var):
        final_tgt = target_var.get()
        current_disc, found_disc = get_current_disc(RUN_IN_RECOVERY)
        if not found_disc:
            current_disc = "C:\\"
        final_tgt = final_tgt.replace("C:", f"{current_disc}")
        if not final_tgt:
            messagebox.showwarning(RS(), l("select_file"))
            return

        backup_path = final_tgt + ".backup"
        if not os.path.exists(backup_path):
            messagebox.showwarning(RS(), f'{l("backup")} {l("not_found")} {l("on_dir")}:\n{backup_path}')
            return

        if messagebox.askyesno(RS(), f'{l("restore")} {os.path.basename(final_tgt)} {l("from_backup")}?'):
            try:
                # Возвращаем бэкап на место основного файла
                shutil.move(backup_path, final_tgt)
                logger.success(f'FR - {l("restore_from_backup")}: {final_tgt}')
                messagebox.showinfo(RS(), f'{l("file")} {l("success")} {l("restored")}.')
            except Exception as e:
                logger.exception(f'FR - {l("error")} {l("when_restoring_a_file")}')
                messagebox.showerror(RS(), str(e))

    FR_GUI = tk.Tk()
    FR_GUI.title(RS())
    FR_GUI.geometry("400x235")

    apply_global_theme(FR_GUI, current_theme)

    source_path = tk.StringVar()
    target_path = tk.StringVar()

    presets = {
        l("your_way"): "",
        f'Sethc ({l("sticky_keys")})': r"C:\Windows\System32\sethc.exe",
        f'Utilman ({l("specialist_possibilities")})': r"C:\Windows\System32\utilman.exe",
        f'Taskmgr ({l("task_manager")})': r"C:\Windows\System32\taskmgr.exe",
        f'Explorer ({l("explorer")})': r"C:\Windows\explorer.exe"
    }

    # GUI элементы
    tk.Label(FR_GUI, text=f'1){l("what_to_replace")}:').pack(anchor="w", padx=10, pady=(10, 0))
    src_frame = tk.Frame(FR_GUI)
    src_frame.pack(fill="x", padx=10)
    tk.Entry(src_frame, textvariable=source_path).pack(side="left", expand=True, fill="x")
    tk.Button(src_frame, text=l("review"), command=lambda: browse_source(source_path)).pack(side="right", padx=5)

    tk.Label(FR_GUI, text=f'2){l("what_are_replace")}:').pack(anchor="w", padx=10, pady=(10, 0))
    combo_presets = ttk.Combobox(FR_GUI, values=list(presets.keys()), state="readonly")
    combo_presets.pack(fill="x", padx=10)
    combo_presets.set(l("select_preset"))
    combo_presets.bind("<<ComboboxSelected>>", lambda e: on_preset_select(e, combo_presets, target_path, presets))

    tgt_frame = tk.Frame(FR_GUI)
    tgt_frame.pack(fill="x", padx=10, pady=5)
    tk.Entry(tgt_frame, textvariable=target_path).pack(side="left", expand=True, fill="x")
    tk.Button(tgt_frame, text=l("review"), command=lambda: browse_target(target_path)).pack(side="right", padx=5)

    # Кнопки действий
    btn_frame = tk.Frame(FR_GUI)
    btn_frame.pack(pady=15)

    tk.Button(btn_frame, text=l("replace"),
              command=lambda: replace_file(source_path, target_path),
              width=15).pack(side="left", padx=10)

    tk.Button(btn_frame, text=l("restore"),
              command=lambda: restore_file(target_path), 
              width=15).pack(side="left", padx=10)

    create_menubar(FR_GUI, RUN_IN_RECOVERY, DEBUG_MODE=DEBUG_MODE)

    FR_GUI.mainloop()

if __name__ == "__main__":
    from config import THEME, DEFAULT_THEME
    current_theme = THEME[DEFAULT_THEME]
    FR(False, current_theme)
