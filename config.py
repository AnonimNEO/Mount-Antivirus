# Общее количество строчек кода
all_line = '7068'

# Каталог настроек
settings_path = 'settings'

# Каталог логов
log_path = 'log'

# Каталог изображений
images_path = 'info_image\\'

# Файл настройки анимации
animation_txt = 'animation.txt'

# Файл базы плохих процессов
bad_process_txt = 'bad_process.txt'

# Файл максимальной нагрузки на CPU
ultimate_load_cpu_txt = 'ultimate_load_cpu.txt'

# Файл максимальной нагрузки на RAM
ultimate_load_ram_txt = 'ultimate_load_ram.txt'

# Файл базы исключений
exception_process_txt = 'exception_process.txt'

# Имя лог файла очитстки temp
clear_temp_log = 'Clear_Temp_log'

# Главный лог файл
T_log_txt = 'Mount_log.txt'

# Ключ Шифрования
clyth = 13

# icon - только иконка, only-windows - только окно, window - иконка и окно
start_interface = 'icon'

# Автозапуск Голосового Управления
start_obpc = True

# Автозапуск LoadProtection
start_lp = False

# анимация в онке True - да | False - нет
animation_default = 'False'

# Способ перезагрузки win32com, os, subprocess, bat
restart_windows = 'win32com'

# Через сколько секунд выполнить перезагрузку
time_to_restart = "1"

# Для win32com, перезапустить ли ОС? True - да | False - нет
reboot_os = True

# Для win32com, закрыть ПО принудительно? True - да | False - нет
force_software = True

# Для способа bat, имя файла .bat (обязательно .bat)
restart_windows_bat = 'restart_windows.bat'

# Имя пользователя по умолчанию
default_user_name = 'Admin'

# Количество секунд до обновления списка процессов
time_to_update_process_list = 5

# Количество секунд до обновления списка процессов в LoadProtection
time_to_close_window = 5

# Количество секунд до закрытия вопроса после заморозки
time_sleep_to_close_question = 30

# Количество секунд до закрытия окна вопроса о добавлении базе исключения
time_sleep_to_close_question2 = 60

# Количество секунд ожидания когда LoadProtection повторит сканирование
time_sleep_to_scan = 5

# Стандартное значения предельной нагрузки на CPU
ultimate_load_cpu = 25

# Стандартное значение предельной нагрузки на RAM
ultimate_load_ram = 20

# База запрещённых процессов по имени
bad_process = ['virus', 'malware', 'trojan', 'yandex', 'browser', 'max']

# База Исключений
exception_process = ['System Idle Process', 'System.exe', 'dwm.exe', 'mmc.exe', 'cmd.exe', 'conhost.exe', 'explorer.exe', 'smss.exe', 'Memory Compression', 'Interrupts', 'Interrupts', 'Registry', 'csrss.exe', 'wininit.exe', 'services.exe', 'RuntimeBroker.exe', 'InputPersonalization.exe', 'ApplicationFrameHost.exe', 'WindowsInternal.ComposableShell.Experiences.TextInput.InputApp.exe', 'taskhostw.exe', 'sihost.exe', 'spoolsv.exe', 'SearchIndexer.exe', 'SearchFilterHost.exe', 'SearchProtocolHost.exe', 'SearchProtocolHost.exe', 'dllhost.exe', 'lsass.exe', 'fontdrvhost.exe', 'csrss.exe', 'winlogon.exe', 'fontdrvhost.exe', 'TiWorker.exe', 'regedit.exe', 'MsMpEng.exe']

