# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

# Вставка картинок
from PIL import Image, ImageTk
# Графический Интерфейс
from tkinter import messagebox
import tkinter as tk
# Логирование Ошибок
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
# Обращение к веб-браузеру
import webbrowser
# Обращение к Системным Командам и Значениям
import os

# Импорт Компонентов
from config import IMAGES_PATH, PROGRAM_AUTHENTICATION_CLYTH
from languages import l
from RS import RS

ABOUT_PROGRAM_VERSION = "0.3.11 Beta"
image_references = {}
er = l("error")

def AP(AUTORUN_MASTER_VERSION=er,
       CROWBAR_ANTIVIRUS_SCRIPTS_HANDLER_VERSION=er,
       CLEAR_CACHE_VERSION=er,
       CROWBAR_MENU_VERSION=er,
       CROWBAR_CONSOLE_VERSION=er,
       EXIT_VERSION=er,
       EDIT_CRITICALITY_VERSION=er,
       FILE_EDITOR_VERSION=er,
       file_manager_version=er,
       FILE_REPLACER_VERSION=er,
       GET_FULL_ACCESS_VERSION=er,
       ON_BOARD_PC_VERSION=er,
       OTHER_FUNCTION_VERSION=er,
       PROCESS_MANAGER_VERSION=er,
       RESTART_VERSION=er,
       REAL_TIME_PROTECT_VERSION=er,
       REGISTRY_MONITOR_VERSION=er,
       RANDOM_STRING_VERSION=er,
       RUN_VERSION=er,
       SETTINGS_AND_UPDATE_VERSION=er,
       SOFTWARE_INSTALLATION_MANAGER=er,
       SCARECROW_PROTECTION_VERSION=er,
       TREY_VERSION=er,
       UNLOCK_ALL_VERSION=er,
       USERS_MANAGER_VERSION=er):
    """Показ данных об программе, принимает в качестве аргументов версии Компонентов"""
    try:
        # Загрузка изображений
        def load_images(master):
            image_labels_container = [] # Список для хранения ссылок на метки изображений
            image_files = [] # Список найденных файлов изображений

            # Проверяем существование каталога
            if not os.path.isdir(IMAGES_PATH):
                return image_labels_container

            # Получаем список файлов в каталоге
            try:
                image_files = [f for f in os.listdir(IMAGES_PATH) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
            except Exception as e:
                logger.exception(f'AP - {l("read_dir_error")} {IMAGES_PATH}')
                return image_labels_container

            # Проверяем наличие файлов
            if not image_files:
                return image_labels_container

            # Если каталог существует и файлы найдены, создаем фрейм для них
            image_frame = tk.Frame(master, bg="black")
            image_frame.pack(pady=20)

            # Загружаем изображения и создаем метки
            for image_file in image_files:
                img_path = os.path.join(IMAGES_PATH, image_file)
                try:
                    img = Image.open(img_path)
                    # Изменение размера изображения
                    img.thumbnail((100, 100))
                    img_tk = ImageTk.PhotoImage(img)

                    # Используем image_frame для создания Label
                    label = tk.Label(image_frame, image=img_tk, bg="black")
                    # Сохраняем ссылку на ImageTk.PhotoImage, чтобы избежать сборки мусора
                    image_references[img_path] = img_tk

                    label.pack(side=tk.LEFT, padx=5)
                    image_labels_container.append(label)

                except Exception as e:
                    logger.exception(f'AP - {l("read_image_error")} {image_file}')
                    continue # если одно изображение не загрузилось, продолжаем с другими

            return image_labels_container # Возвращаем список загруженных меток, чтобы знать, создался ли фрейм

        def show_component_versions(event):
            version_component_text = (
                f'{l("version_component")}:\n'
                f'{l("pac")}: {PROGRAM_AUTHENTICATION_CLYTH}\n'
                f'---{l("general_component")}---\n'
                f'{l("program_kernel")}: {TREY_VERSION}\n'
                f'{l("ARM")}: {AUTORUN_MASTER_VERSION}\n'
                f'{l("PM")}: {PROCESS_MANAGER_VERSION}\n'
                f'{l("FM")}: {file_manager_version}\n'
                f'{l("UA")}: {UNLOCK_ALL_VERSION}\n'
                f'{l("FE")}: {FILE_EDITOR_VERSION}\n'
                f'{l("RLP")}: {REAL_TIME_PROTECT_VERSION}\n'
                f'{l("SIM")}: {SOFTWARE_INSTALLATION_MANAGER}\n'
                f'{l("RM")}: {REGISTRY_MONITOR_VERSION}\n'
                f'---{l("mini_component")}---\n'
                f'{l("CM")}: {CROWBAR_MENU_VERSION}\n'
                f'{l("UM")}: {USERS_MANAGER_VERSION}\n'
                f'{l("FR")}: {FILE_REPLACER_VERSION}\n'
                f'{l("SP")}: {SCARECROW_PROTECTION_VERSION}\n'
                f'{l("CC")}: {CLEAR_CACHE_VERSION}\n'
                f'{l("R")}: {RESTART_VERSION}\n'
                f'{l("Run")}: {RUN_VERSION}\n'
                f'{l("OBPC")}: {ON_BOARD_PC_VERSION}\n'
                f'---{l("system_component")}---\n'
                f'{l("encryption")}: AES\n'
                f'{l("CASH")}: {CROWBAR_ANTIVIRUS_SCRIPTS_HANDLER_VERSION}\n'
                f'{l("EC")}: {EDIT_CRITICALITY_VERSION}\n'
                f'{l("GFA")}: {GET_FULL_ACCESS_VERSION}\n'
                f'{l("OF")}: {OTHER_FUNCTION_VERSION}\n'
                f'{l("Console")}: {CROWBAR_CONSOLE_VERSION}\n'
                f'{l("RS")}: {RANDOM_STRING_VERSION}\n'
                f'{l("AP")}: {ABOUT_PROGRAM_VERSION}\n'
                f'{l("SAU")}: {SETTINGS_AND_UPDATE_VERSION}\n'
                f'{l("E")}: {EXIT_VERSION}\n'
            )

            messagebox.showinfo(RS(), version_component_text)



        def open_gpl_licenses(event):
            webbrowser.open("https://www.gnu.org/licenses/gpl-3.0.html")



        def open_website(event):
            webbrowser.open("https://anonimneo.github.io/NEO-Organization/")



        def open_trade_on_steam(event):
                webbrowser.open_new("https://steamcommunity.com/tradeoffer/new/?partner=1842324943&token=xPAad4EP")



        about_window = tk.Tk()
        about_window.title(RS())
        about_window.configure(bg="black")

        # Текст
        label = tk.Label(about_window, text=l("about_program_text"), bg="black", fg="white", font=("ComicSans", 16))
        label.pack(pady=20)

        image_labels = load_images(about_window)

        version_link = tk.Label(about_window, text=l("version_component"), bg="black", fg="green", cursor="hand2", font=("ComicSans", 16))
        version_link.pack(pady=10)
        version_link.bind("<Button-1>", show_component_versions)

        donationalerts_link = tk.Label(about_window, text=l("donation_steam_text"), bg="black", fg="red", cursor="hand2", font=("ComicSans", 16))
        donationalerts_link.pack(pady=10)
        donationalerts_link.bind("<Button-1>", open_trade_on_steam)

        gpl_link = tk.Label(about_window, text=f'{l("license")} GPL v3.0', bg="red", fg="white", cursor="hand2", font=("ComicSans", 16))
        gpl_link.pack(pady=10)
        gpl_link.bind("<Button-1>", open_gpl_licenses)

        website_link = tk.Label(about_window, text=l("website_neo_organization"), bg="blue", fg="yellow", cursor="hand2", font=("ComicSans", 16))
        website_link.pack(pady=10)
        website_link.bind("<Button-1>", open_website)

        about_window.mainloop()
    except Exception as e:
        logger.exception(l("ap_exception_text"))

if __name__ == "__main__":
    AP()
