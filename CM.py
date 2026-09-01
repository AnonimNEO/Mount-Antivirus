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
from tkinter import ttk, Menu
import tkinter as tk
# Логирование Ошибок
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger

# Импорт Компонентов
try:
    from ARM import ARM
except Exception as e:
    def ARM(a=None, b=None):
        pass

# try:
#     from B import B
# except Exception as e:
#     def B(a=None, b=None, c=None, d=None, e=None):
#         pass

try:
    from CC import CC
except Exception as e:
    def CC(a=None):
        pass
    
try:
    from FM import FM
except Exception as e:
    def FM(a=None, b=None):
        pass
    
try:
    from FE import FE
except Exception as e:
    def FE():
        pass
    
try:
    from FR import FR
except Exception as e:
    def FR(a=None, b=None):
        pass
    
try:
    from RLP import RLP
except Exception as e:
    def RLP():
        pass

try:
    from OF import pac, run_component, run_component_process, open_with, get_current_disc, apply_global_theme, protect_window_from_moving, create_menubar
except Exception as e:
    def pac():
        pass
    def run_component(a=None, *b):
        pass
    def open_with():
        pass
    def get_current_disc(a=None):
        pass
    def apply_global_theme(a=None, b=None):
        pass
    def protect_window_from_moving(a=None, b=None):
        pass
    def create_menubar(a=None, b=None, c=None, d=None, e=None):
        pass
    #def CMD():
    #    pass

try:
    from PM import PM
except Exception as e:
    def PM(a=None, b=None):
        pass
    
try:
    from R import R
except Exception as e:
    def R():
        pass
    
try:
    from RS import RS
except Exception as e:
    def RS(a=None):
        return "error"
    
try:
    from Run import Run
except Exception as e:
    def Run(a=None):
        pass
    
try:
    from SP import SP
except Exception as e:
    def SP(a=None, b=None, c=None):
        pass
    
try:
    from UA import UA
except Exception as e:
    def UA(a=None):
        pass
    
try:
    from UM import UM
except Exception as e:
    def UM(a=None):
        pass

from config import PROGRAM_AUTHENTICATION_CLYTH
from languages import l

CROWBAR_MENU_VERSION = "2.3.18 Beta"

# @logger.catch
def CM(RUN_IN_RECOVERY=False, current_theme="dark", DEBUG_MODE=False):
    """Главное окно программы"""
    try:
        # Обновляем размер шрифта и кнопок при изменении размера окна
        def on_window_resize(event):
            # Проверяем, что событие вызвано именно окном CM_GUI
            if event.widget != CM_GUI:
                return

            width = event.width
            height = event.height

            # Базовые размеры
            base_width = 750
            base_height = 300

            # Вычисляем коэффициенты
            scale_w = width / base_width
            scale_h = height / base_height

            # Снижаем интенсивность вертикального масштабирования.
            # Берём ширину как основной фактор и высоту как вспомогательный.
            # Это предотвратит раздувание шрифта на квадратных мониторах.
            scale = (scale_w * 0.8) + (scale_h * 0.2)

            # Замедляем общий рост, чтобы на 4К или полном экране шрифт не становился огромным.
            # Я честно не знаю, работает ли это у меня FullHD
            if scale > 1.2:
                scale = 1.2 + (scale - 1.2) * 0.5

            # Рассчитываем новые размеры шрифтов
            header_font_size = int(32 * scale)
            button_font_size = int(18 * scale)
            small_button_font_size = int(10 * scale)

            # Применяем шрифты с лимитом сверху
            update_fonts(
                min(48, max(14, header_font_size)), 
                min(24, max(10, button_font_size)), 
                min(14, max(8, small_button_font_size)), 
                scale
            )

        # Обновляем шрифты всех элементов интерфейса
        def update_fonts(header_size, button_size, small_size, scale):
            try:
                # Шрифт для заголовков
                header_f = ("Default", header_size, "bold")
                for label in header_labels:
                    label.configure(font=header_f)

                # Шрифт для кнопок
                button_f = ("Default", button_size)
                for btn in regular_buttons:
                    btn.configure(style="TButton")
                    style.configure("TButton", font=button_f) 
                    btn.configure(font=button_f)

                # Маленькие кнопки
                small_f = ("Default", small_size)
                for btn in small_buttons:
                    btn.configure(font=small_f)

                # Версия внизу
                copyleft_label.configure(font=("Default", max(8, int(10 * scale))))
            except:
                pass

        CM_GUI = tk.Tk()
        CM_GUI.geometry("750x350")
        CM_GUI.minsize(750, 300)
        CM_GUI.title(RS())

        CM_GUI.lift()
        CM_GUI.focus_set()

        apply_global_theme(CM_GUI, current_theme)

        style = ttk.Style()

        tab_control = ttk.Notebook(CM_GUI)

        tab_components = ttk.Frame(tab_control)
        tab_control.add(tab_components, text=l("components"))
        tab_utilities = ttk.Frame(tab_control)
        tab_control.add(tab_utilities, text=l("utilities"))
        tab_protect = ttk.Frame(tab_control)
        tab_control.add(tab_protect, text=l("protect"))
        tab_manage = ttk.Frame(tab_control)
        tab_control.add(tab_manage, text=l("control"))

        tab_components.configure(style="TFrame")
        tab_utilities.configure(style="TFrame")
        tab_protect.configure(style="TFrame")
        tab_manage.configure(style="TFrame")

        # Списки для отслеживания элементов при изменении размера
        header_labels = []
        regular_buttons = []
        small_buttons = []

        # Вкладка "Компоненты"
        label_comp = ttk.Label(tab_components, text=l("components"), font="Default 24")
        label_comp.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        header_labels.append(label_comp)

        arm_btn = ttk.Button(tab_components, text=l("ARM"),
                     command=lambda:run_component_process(ARM, RUN_IN_RECOVERY, current_theme, DEBUG_MODE))
        arm_btn.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(arm_btn)

        pm_btn = ttk.Button(tab_components, text=l("PM"),
                     command=lambda:run_component_process(PM, RUN_IN_RECOVERY, current_theme, DEBUG_MODE))
        pm_btn.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(pm_btn)

        fm_btn = ttk.Button(tab_components, text=l("FM"),
                     command=lambda:run_component_process(FM, RUN_IN_RECOVERY, current_theme, DEBUG_MODE))
        fm_btn.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(fm_btn)

        ua_btn = ttk.Button(tab_components, text=l("UA"),
                     command=lambda:UA(RUN_IN_RECOVERY, DEBUG_MODE))
        ua_btn.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(ua_btn)



        # Вкладка "Утилиты"
        label_util = ttk.Label(tab_utilities, text=l("utilities"))
        label_util.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        header_labels.append(label_util)

        fr_btn = ttk.Button(tab_utilities, text=l("FR"),
                     command=lambda:run_component(FR, RUN_IN_RECOVERY, current_theme, DEBUG_MODE))
        fr_btn.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(fr_btn)

        cc_btn = ttk.Button(tab_utilities, text=l("CC"),
                     command=lambda:CC(RUN_IN_RECOVERY))
        cc_btn.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(cc_btn)

        run_btn = ttk.Button(tab_utilities, text=l("Run"),
                     command=lambda:run_component_process(Run, current_theme, DEBUG_MODE))
        run_btn.grid(row=2, column=0, columnspan=1, sticky="nsew", padx=5, pady=5)
        small_buttons.append(run_btn)

        #cmd_btn = ttk.Button(tab_utilities, text="CMD",
        #             command=lambda:run_component(CMD))
        #cmd_btn.grid(row=2, column=1, columnspan=1, sticky="nsew", padx=5, pady=5)
        #small_buttons.append(cmd_btn)

        r_btn = ttk.Button(tab_utilities, text=l("R"),
                     command=R)
        r_btn.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(r_btn)

        ow_btn = ttk.Button(tab_utilities, text=l("open_with"),
                     command=lambda:open_with())
        ow_btn.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(ow_btn)



        # Вкладка "Защита"
        label_prot = ttk.Label(tab_protect, text=l("protect"))
        label_prot.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        header_labels.append(label_prot)

        if DEBUG_MODE:
            try:
                from RLP import RLP
            except:
                logger.exception(f"CM - {import_error} RLP")
            rlp_btn = ttk.Button(tab_protect, text="Защита Нагрузки",
                          command=lambda:run_component(RLP, RUN_IN_RECOVERY))
            rlp_btn.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
            regular_buttons.append(rlp_btn)

            try:
                from SIM import SIM
            except:
                logger.exception(f"CM - {import_error} SIM")
            sim_btn = ttk.Button(tab_protect, text="Менеджер Установки",
                                 command=lambda: run_component(SIM, RUN_IN_RECOVERY, current_theme, DEBUG_MODE))
            sim_btn.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
            regular_buttons.append(sim_btn)

        sp_btn = ttk.Button(tab_protect, text=l("SP"),
                      command=lambda:run_component(SP, RUN_IN_RECOVERY, current_disc_r, current_theme, DEBUG_MODE))
        sp_btn.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(sp_btn)



        # Вкладка "Управление"
        label_manage = ttk.Label(tab_manage, text=l("control"))
        label_manage.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        header_labels.append(label_manage)

        um_btn = ttk.Button(tab_manage, text=l("UM"),
                      command=lambda:run_component(UM, current_theme, DEBUG_MODE))
        um_btn.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(um_btn)

        fe_btn = ttk.Button(tab_manage, text=l("FE"),
                            command=lambda: run_component(FE, None, current_theme))
        fe_btn.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        regular_buttons.append(fe_btn)

        # b_btn = ttk.Button(tab_manage, text=l("B"),
        #                     command=lambda: run_component(B, RUN_IN_RECOVERY))
        # b_btn.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        # regular_buttons.append(b_btn)

        # Настройка сетки для адаптивности
        for tab in [tab_components, tab_utilities, tab_protect, tab_manage]:
            tab.columnconfigure(0, weight=1)
            tab.columnconfigure(1, weight=1)
            tab.rowconfigure(1, weight=1)
            tab.rowconfigure(2, weight=1)
            tab.rowconfigure(3, weight=1)
            tab.rowconfigure(4, weight=1)

        if RUN_IN_RECOVERY:
            current_disc_r, found_disc = get_current_disc(RUN_IN_RECOVERY)
        else:
            current_disc_r = "C:\\"

        tab_control.pack(fill="both", expand=True)

        copyleft_label = ttk.Label(CM_GUI, text=f'{l("CM")} {CROWBAR_MENU_VERSION}', anchor="w")
        copyleft_label.pack(side="bottom", anchor="w", padx=10, pady=10)

        # Создаём меню
        create_menubar(CM_GUI, RUN_IN_RECOVERY, DEBUG_MODE=DEBUG_MODE)

        # if RUN_IN_RECOVERY:
        #     def change_user():
        #        user = simpledialog.askstring(title=RS(), prompt=f"Введите имя пользователя: ")
        #        load_bush(current_disc, user)

        #     menubar.add_command(label=f"Пользователь: {user_name}", command=lambda:change_user)

        # Привязываем событие изменения размера окна
        CM_GUI.bind("<Configure>", on_window_resize)

        CM_GUI.mainloop()
    except:
        logger.exception(l("cm_critical_error"))

if __name__ == "__main__":
    from config import THEME, DEFAULT_THEME
    current_theme = THEME[DEFAULT_THEME]
    CM(False, current_theme)
