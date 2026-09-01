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
from tkinter import filedialog, messagebox
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
import os

from languages import l
from config import CLYTH
from RS import RS
from AES import AES
from OF import pac, extract_filename_from_path, apply_global_theme, create_menubar

FILE_EDITOR_VERSION = "0.3.12 Beta"

class FileEditor:
    def __init__(self, FE_GUI):
        self.FE_GUI = FE_GUI
        self.FE_GUI.title(RS())
        self.FE_GUI.geometry("650x400")

        self.current_file = None
        self.is_modified = False

        # Переменные для стилей
        self.font_family = "Default"
        self.font_size = 12
        self.line_numbers_enabled = False

        # Список для хранения позиций совпадений
        self.matches_positions = []
        self.current_match_index = -1

        # Создаём меню
        create_menubar(self.FE_GUI, False, "FE", self.open_file, self.save_file, None, True, self.save_as_file, self.on_closing, self.change_font, self.change_font_size)

        # Создаём панель поиска
        self.create_search_panel()

        # Создаём главный фрейм
        self.main_frame = tk.Frame(self.FE_GUI)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Создаём текстовое поле
        self.create_text_widget()

        # Создаём строку состояния
        self.create_status_bar()

        # Создаём контекстное меню
        self.create_context_menu()

        # Привязываем сочетания клавиш
        self.bind_shortcuts()

        # Обработчик закрытия окна
        self.FE_GUI.protocol("WM_DELETE_WINDOW", self.on_closing)



    def create_context_menu(self):
        self.context_menu = tk.Menu(self.FE_GUI, tearoff=0)
        self.context_menu.add_command(label=l("cancel"), command=lambda: self.text_widget.edit_undo())
        self.context_menu.add_command(label=l("repeat"), command=lambda: self.text_widget.edit_redo())
        self.context_menu.add_separator()
        self.context_menu.add_command(label=l("cut"), command=self.cut_text)
        self.context_menu.add_command(label=l("copy"), command=self.copy_text)
        self.context_menu.add_command(label=l("paste"), command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=l("select_all"), command=self.select_all)

        # Привязываем показ контекстного меню на ПКМ
        self.text_widget.bind("<Button-3>", self.show_context_menu)



    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_FE_GUI, event.y_FE_GUI)
        finally:
            self.context_menu.grab_release()



    def bind_shortcuts(self):
        self.FE_GUI.bind("<Control-O>", lambda e: self.open_file())
        self.FE_GUI.bind("<Control-S>", lambda e: self.save_file())
        self.FE_GUI.bind("<Control-Shift-S>", lambda e: self.save_as_file())
        self.FE_GUI.bind("<Control-Z>", lambda e: self.text_widget.edit_undo())
        self.FE_GUI.bind("<Control-Y>", lambda e: self.text_widget.edit_redo())
        self.FE_GUI.bind("<Control-X>", lambda e: self.cut_text())
        self.FE_GUI.bind("<Control-C>", lambda e: self.copy_text())
        self.FE_GUI.bind("<Control-V>", lambda e: self.paste_text())
        self.FE_GUI.bind("<Control-A>", lambda e: self.select_all())
        self.FE_GUI.bind("<Control-F>", lambda e: self.toggle_search_panel())



    def change_font(self, font_name):
        self.font_family = font_name
        self.text_widget.config(font=(self.font_family, self.font_size))



    def change_font_size(self, size):
        self.font_size = size
        self.text_widget.config(font=(self.font_family, self.font_size))



    def create_text_widget(self):
        frame = tk.Frame(self.main_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Прокрутка
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Текстовое поле
        self.text_widget = tk.Text(
            frame,
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
            font=(self.font_family, self.font_size),
            undo=True,
            maxundo=-1
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)

        # Отслеживание изменений
        self.text_widget.bind("<KeyRelease>", self.on_text_change)



    def create_status_bar(self):
        self.status_bar = tk.Label(
            self.FE_GUI,
            text=l("new_file"),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)



    def update_status_bar(self):
        if self.current_file:
            filename = os.path.basename(self.current_file)
            modified_indicator = " *" if self.is_modified else ""
            self.status_bar.config(text=f"{filename}{modified_indicator}")
        else:
            modified_indicator = " *" if self.is_modified else ""
            self.status_bar.config(text=f'{l("new_file")}{modified_indicator}')



    def on_text_change(self, event=None):
        if not self.is_modified:
            self.is_modified = True
            self.update_status_bar()
        # Обновляем поиск
        if self.search_active:
            self.perform_search()



    def open_file(self):
        file_path = filedialog.askopenfilename(
            title=RS(),
            filetypes=[(l("text_file"), "*.txt"), ("MarkDown", "*.md"), ("JSON", "*.json"), (l("crowbar_scripts"), "*.cas"), (l("all_files"), "*.*")]
        )
        if file_path:
            self.load_file(file_path)



    def load_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                messagebox.showerror(RS(), f'{l("file")} {l("not_found")}: {file_path}')
                return

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            file_name = extract_filename_from_path(file_path)
            if file_name[-4:] == ".cas":
                content = AES(content, CLYTH, True)

            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, content)

            self.current_file = file_path
            self.is_modified = False
            self.update_status_bar()
        except Exception as e:
            logger.exception(f'FE - {l("error")} {l("load_file")}')
            messagebox.showerror(RS(), str(e))



    def save_file(self):
        if not self.current_file:
            self.save_as_file()
            return
        try:
            content = self.text_widget.get(1.0, tk.END)
            file_name = extract_filename_from_path(self.current_file)
            if file_name[-4:] == ".cas":
                content = AES(content, CLYTH)
            with open(self.current_file, "w", encoding="utf-8") as file:
                file.write(content)
            self.is_modified = False
            self.update_status_bar()
            messagebox.showinfo(RS(), f'{l("file")} {l("success_saved")}!')
        except Exception as e:
            logger.exception(f'FE - {l("error")} {l("save_file")}: {self.current_file}')
            messagebox.showerror(RS(), str(e))



    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            title=RS(),
            defaultextension=".txt",
            filetypes=[(l("text_file"), "*.txt"), ("MarkDown", "*.md"), ("JSON", "*.json"), (l("crowbar_scripts"), "*.cas"), (l("all_files"), "*.*")]
        )
        if file_path:
            try:
                content = self.text_widget.get(1.0, tk.END)
                content = AES(content, CLYTH)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self.current_file = file_path
                self.is_modified = False
                self.update_status_bar()
                messagebox.showinfo(RS(), f'{l("file")} {l("success_saved")}!')
            except Exception as e:
                logger.exception(f'FE - {l("error")} {l("save_file")}: {file_path}')
                messagebox.showerror(RS(), str(e))



    def cut_text(self):
        try:
            self.text_widget.event_generate("<<Cut>>")
        except:
            pass



    def copy_text(self):
        try:
            self.text_widget.event_generate("<<Copy>>")
        except:
            pass



    def paste_text(self):
        try:
            self.text_widget.event_generate("<<Paste>>")
        except:
            pass



    def select_all(self):
        self.text_widget.tag_add(tk.SEL, "1.0", tk.END)
        self.text_widget.mark_set(tk.INSERT, "1.0")
        self.text_widget.see(tk.INSERT)
        return "break"



    def on_closing(self):
        if self.is_modified:
            response = messagebox.askyesnocancel(RS(), l("save_changes?"))
            if response is None: # Отмена
                return
            elif response: # Да
                self.save_file()
        self.FE_GUI.destroy()



    # Создаём панель поиска
    def create_search_panel(self):
        self.search_active = True
        self.search_panel = tk.Frame(self.FE_GUI, bd=1, relief=tk.RAISED)
        self.search_panel.pack(side=tk.TOP, fill=tk.X)
        # Текстовое поле поиска
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_panel, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.perform_search())

        # Чекбоксы
        self.case_var = tk.BooleanVar(value=True)
        self.word_var = tk.BooleanVar(value=False)

        self.case_check = tk.Checkbutton(self.search_panel, text=l("match_case"), variable=self.case_var, command=self.perform_search)
        self.word_check = tk.Checkbutton(self.search_panel, text=l("whole_words"), variable=self.word_var, command=self.perform_search)

        self.case_check.pack(side=tk.LEFT, padx=5)
        self.word_check.pack(side=tk.LEFT, padx=5)

        # Кнопки навигации
        self.prev_button = tk.Button(self.search_panel, text=l("back"), command=self.search_prev)
        self.next_button = tk.Button(self.search_panel, text=l("next"), command=self.search_next)
        self.prev_button.pack(side=tk.LEFT, padx=2)
        self.next_button.pack(side=tk.LEFT, padx=2)

        # Кнопка закрытия поиска
        self.close_search_button = tk.Button(self.search_panel, text="×", command=self.toggle_search_panel)
        self.close_search_button.pack(side=tk.RIGHT, padx=2)



    # Показываем или скрывает панель поиска
    def toggle_search_panel(self):
        if self.search_active:
            self.search_panel.pack_forget()
            self.search_active = False
            self.clear_search_highlight()
        else:
            self.search_panel.pack(side=tk.TOP, fill=tk.X, before=self.main_frame)
            self.search_active = True
            self.search_var.set("")
            self.matches_positions = []
            self.current_match_index = -1
            self.clear_search_highlight()



    # Выполняем поиск и выделяем совпадения
    def perform_search(self):
        self.clear_search_highlight()
        pattern = self.search_var.get()
        if not pattern:
            return
        content = self.text_widget.get("1.0", tk.END)
        flags = 0
        if not self.case_var.get():
            pattern = pattern.lower()
            content_cmp = content.lower()
        else:
            content_cmp = content

        self.matches_positions = []

        import re
        if self.word_var.get():
            regex = r"\b{}\b".format(re.escape(pattern))
        else:
            regex = re.escape(pattern)

        for match in re.finditer(regex, content_cmp):
            start_idx = match.start()
            end_idx = match.end()
            start = self.text_widget.index(f"1.0+{start_idx}c")
            end = self.text_widget.index(f"1.0+{end_idx}c")
            self.matches_positions.append((start, end))

        # Выделяем все совпадения одним цветом
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        for start, end in self.matches_positions:
            self.text_widget.tag_add("search_highlight", start, end)
        self.text_widget.tag_config("search_highlight", foreground="blue", background="yellow")

        # Выделяем текущее совпадение другим цветом
        self.text_widget.tag_remove("current_match", "1.0", tk.END)
        if self.matches_positions:
            self.current_match_index = 0
            start, end = self.matches_positions[self.current_match_index]
            self.text_widget.tag_add("current_match", start, end)
            self.text_widget.tag_config("current_match", foreground="white", background="red")

            self.focus_match(self.current_match_index)



    # Перемещаем курсор к совпадению по индексу и выделяем его цветом
    def focus_match(self, index):
        if not self.matches_positions:
            return
        if index < 0 or index >= len(self.matches_positions):
            return
        start, end = self.matches_positions[index]
        # Убираем выделение текущего совпадения
        self.text_widget.tag_remove("current_match", "1.0", tk.END)
        self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
        self.text_widget.tag_add("current_match", start, end)
        self.text_widget.see(start)
        self.text_widget.mark_set(tk.INSERT, start)
        # Выделяем текущее совпадение
        self.text_widget.tag_add(tk.SEL, start, end)



    # Переходим к следующему совпадению
    def search_next(self):
        if not self.matches_positions:
            return
        self.current_match_index = (self.current_match_index + 1) % len(self.matches_positions)
        self.focus_match(self.current_match_index)



    # Переходим к предыдущему совпадению
    def search_prev(self):
        if not self.matches_positions:
            return
        self.current_match_index = (self.current_match_index - 1) % len(self.matches_positions)
        self.focus_match(self.current_match_index)



    # Удаляем выделение от поиска
    def clear_search_highlight(self):
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)



def FE(file_path=None, current_theme=False):
    try:
        if not current_theme:
            from config import THEME, DEFAULT_THEME
            current_theme = THEME[DEFAULT_THEME]
        FE_GUI = tk.Tk()
        apply_global_theme(FE_GUI, current_theme)
        editor = FileEditor(FE_GUI)
        if file_path:
            editor.load_file(file_path)
        FE_GUI.mainloop()
    except:
        logger.exception(l("fe_critical_error"))

if __name__ == "__main__":
    FE()
