# Текущий язык (доступные языки: ru, en, ua)
CURRENT_LOCALIZATION = "ru"

# Общее количество строчек кода
ALL_LINE = "~13000"

# Каталог логов
LOG_PATH = "log"

# Шифрование логов
ENCRYPT_LOGS = False

# Каталог изображений
IMAGES_PATH = "."

# Имя лог файла очистки temp
CLEAR_TEMP_LOG = "Clear_Temp_log"

# Главный лог файл
T_LOG_TXT = "Crawbar_log.txt"

# Ключ Шифрования
CLYTH = "63263262"

# Ключ подтверждения подлинного окна
PROGRAM_AUTHENTICATION_CLYTH = "88005553535"

# icon - только иконка, only-windows - только окно, window - иконка и окно
START_INTERFACE = "icon"

# Контрастная тема
BLACK_THEME = {"bg": "black", "fg": "white", "bbg": "darkblue", "bfg": "white", "abg": "blue", "afg": "white", "lbg":  "black", "lfg": "white", "stb": "#090909", "tbg": "darkblue", "tfg": "white"}

# Тёмная тема
DARK_THEME = {"bg": "#1e1f22", "fg": "white", "bbg": "#243048", "bfg": "white", "abg": "#548af7", "afg": "white", "lbg":  "#1e1f22", "lfg": "white", "stb": "#1e1f22", "tbg": "#243048", "tfg": "white"}

# Светлая тема
WHITE_THEME = {"bg": "white", "fg": "black", "bbg": "white", "bfg": "black", "abg": "gray", "afg": "black", "lbg":  "white", "lfg": "black", "stb": "gray", "tbg": "white", "tfg": "black"}

# Красная тема
RED_THEME = {"bg": "black", "fg": "white", "bbg": "darkred", "bfg": "white", "abg": "red", "afg": "black", "lbg":  "black", "lfg": "white", "stb": "red", "tbg": "darkred", "tfg": "white"}

# Серая тема
GRAY_THEME =  {"bg": "gray", "fg": "white", "bbg": "gray", "bfg": "white", "abg": "white", "afg": "black", "lbg":  "gray", "lfg": "white", "stb": "gray", "tbg": "black", "tfg": "white"}

# Оранжевая тема
ORANGE_THEME =  {"bg": "gray", "fg": "white", "bbg": "darkorange", "bfg": "white", "abg": "orange", "afg": "black", "lbg":  "gray", "lfg": "darkorange", "stb": "gray", "tbg": "darkorange", "tfg": "black"}

# Зелёная тема
LIME_THEME =  {"bg": "green", "fg": "white", "bbg": "green", "bfg": "white", "abg": "lime", "afg": "black", "lbg":  "green", "lfg": "lime", "stb": "green", "tbg": "lime", "tfg": "black"}

# (НЕ РЕДАКТИРОВАТЬ) Кортеж тем
THEME = {"black": BLACK_THEME, "dark": DARK_THEME, "white": WHITE_THEME, "red": RED_THEME, "gray": GRAY_THEME, "orange": ORANGE_THEME, "lime": LIME_THEME}

# Тема по умолчанию
DEFAULT_THEME = "dark"

# Автозапуск LoadProtection
START_LP = False

# Старт движка скриптов
START_CASH = True

# Способ перезагрузки win32com, os, subprocess, bat
RESTART_WINDOWS = "win32com"

# Через сколько секунд выполнить перезагрузку
TIME_TO_RESTART = "1"

# Для win32com, перезапустить ли ОС? True - да | False - нет
REBOOT_OS = True

# Для win32com, закрыть ПО принудительно? True - да | False - нет
FORCE_SOFTWARE = True

# Для способа bat, имя файла .bat (обязательно .bat)
RESTART_WINDOWS_BAT = "restart_windows.bat"

# Имя пользователя по умолчанию
DEFAULT_USER_THEME = "Admin"

TIME_TO_UPDATE_PROCESS_LIST = 5

# (НЕ РЕДАКТИРОВАТЬ) Документация
DOCUMENTATION_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Справка Антивирус Монтировка</title>
	<style>
		* {
			box-sizing: border-box;
		}

		body {
			font-family: Arial, sans-serif;
			line-height: 1.5;
			background: # 1a1a1a;
			margin: 0;
			padding: 0;
			display: flex;
			flex-direction: column;
			min-height: 100vh;
			color: white;
		}

		header {
			background: linear-gradient(135deg, darkred 0%, # 770000 100%);
			color: white;
			padding: 15px;
			text-align: center;
			box-shadow: 0 4px 6px rgba(255, 0, 0, 0.3);
		}

		.container {
			display: flex;
			flex: 1;
			min-height: 0;
		}

		.sidebar-container {
			display: flex;
			flex-direction: column;
			width: 290px;
			transition: width 0.3s ease;
			flex-shrink: 0;
			height: 100vh;
  			overflow-y: auto;
		}

		.sidebar-container.collapsed {
			width: 40px;
		}

		.sidebar-toggle {
			background-color: darkred;
			color: white;
			border: none;
			padding: 10px;
			cursor: pointer;
			width: 40px;
			height: 40px;
			border-radius: 0 0 4px 0;
			display: flex;
			align-items: center;
			justify-content: center;
			margin-bottom: 5px;
		}

		.sidebar-toggle:hover {
			background-color: # cc0000;
		}

		.sidebar-toggle span {
			display: block;
			width: 20px;
			height: 2px;
			background-color: white;
			margin: 2px 0;
		}

		.sidebar {
			width: 250px;
			background-color: # 2a2a2a;
			padding: 20px;
			transition: all 0.3s ease;
			overflow-y: auto;
			border-right: 2px solid red;
			flex: 1;
		}

		.sidebar.collapsed {
			width: 0;
			padding: 0;
			border-right: none;
			overflow: hidden;
		}

		.sidebar ul {
			list-style-type: none;
			padding: 0;
			margin: 0;
		}

		.sidebar li {
			margin-bottom: 10px;
		}

		.sidebar a {
			display: block;
			padding: 8px 12px;
			text-decoration: none;
			color: orange;
			border-radius: 4px;
			cursor: pointer;
			transition: all 0.3s ease;
		}

		.sidebar a:hover {
			background-color: darkred;
			color: orange;
		}

		.sidebar li ul {
			margin-left: 20px;
			margin-top: 5px;
		}

		.content {
			flex: 1;
			padding: 20px;
			overflow-y: auto;
			min-width: 0;
			height: 100vh;
  			overflow-y: auto;
			background-color: # 1a1a1a;
		}

		img {
			display: block;
			max-width: 100%;
			height: auto;
			margin-bottom: 20px;
		}

		section {
			display: none;
			padding: 15px;
			border: 1px solid red;
			border-radius: 4px;
			background-color: darkred;
			<!-- background-color: # E27C1A; -->
		}

		section.active {
			display: block;
		}

		.component-section {
			display: none;
		}

		.component-section.active {
			display: block;
		}

		h2 {
			margin-top: 0;
			color: white;
		}

		h2 {
			margin-top: 5px;
			color: orange;
		}

		h3 {
			margin-top: 5px;
			color: orange;
		}

		.faq-item {
			margin-bottom: 20px;
			padding-bottom: 20px;
			border-bottom: 1px solid black;
			color: white;
		}

		.component-item {
			margin-bottom: 20px;
			padding: 15px;
			background-color: # 2a2a2a;
			border-left: 4px solid orange;
			border-radius: 4px;
			color: white;
		}

		.component-item h3 {
			margin-top: 0;
			color: orange;
		}

		.requirements-list {
			background-color: darkred;
			padding: 15px;
			border-radius: 4px;
			margin-top: 10px;
			border: 1px solid black;
			color: white;
		}

		.requirements-list li {
			margin-bottom: 8px;
		}

		.programmer {
			display: inline-block;
			background-color: black;
			color: red;
			padding: 5px 10px;
			border-radius: 4px;
			font-weight: bold;
			margin-top: 10px;
		}
	</style>

</head>
<body>
	<header>
		<h1>Документация Антивируса Монтировка</h1>
		<p><b>Свободный</b> антивирус на Python</p>
	</header>
	<div class="container">
		<div class="sidebar-container" id="sidebarContainer">
			<button class="sidebar-toggle" id="toggleSidebar" title="Панель">
				<span></span>
				<span></span>
				<span></span>
			</button>
			<nav class="sidebar" id="sidebar">
				<ul>
					<li><a onclick="showSection('about')">О программе</a></li>
					<li><a onclick="showSection('requirements')">Минимальные требования</a></li>
					<li><a onclick="showSection('install')">Установка</a></li>
					<li><a onclick="showSection('components')">Компоненты</a>
						<ul>
							<li><a onclick="showComponent('autorunmaster')">Мастер Автозагрузки</a></li>
							<li><a onclick="showComponent('processmanager')">Менеджер Процессов</a></li>
							<li><a onclick="showComponent('filemanager')">Файловый Менеджер</a></li>
							<li><a onclick="showComponent('unlockall')">Разблокировка всего</a></li>
							<li><a onclick="showComponent('usermanager')">Менеджер Пользователей</a></li>
							<li><a onclick="showComponent('fileeditor')">Редактор Файлов</a></li>
							<li><a onclick="showComponent('crowbarscipts')">Обработчик Скриптов</a></li>
							<li><a onclick="showComponent('restart')">Перезапуск ОС</a></li>
							<li><a onclick="showComponent('realtimeprotection')">(Pre-Alpha) Защита в Реальном Времени</a></li>
							<li><a onclick="showComponent('clearcache')">Очистка Кэша</a></li>
							<li><a onclick="showComponent('browser')">Браузер</a></li>
							<li><a onclick="showComponent('replacer')">Замена системных файлов</a></li>
							<li><a onclick="showComponent('run')">Запуск от администратора</a></li>
							<li><a onclick="showComponent('scarecrowprotection')">Пугало от вирусов</a></li>
							<li><a onclick="showComponent('installmanager')">(Pre-Alpha) Менеджер Установки</a></li>
						</ul>
					</li>
					<li><a onclick="showSection('why')">Почему мы?</a></li>
					<li><a onclick="showSection('commercial')">Коммерческое использование</a></li>
					<li><a onclick="showSection('update')">Обновления</a></li>
					<li><a onclick="showSection('faq')">Частые вопросы</a></li>
					<li><a onclick="showSection('privacy')">Конфиденциальность</a></li>
					<li><a onclick="showSection('contacts')">Контакты</a></li>
				</ul>
			</nav>
		</div>

		<main class="content">
			<section id="about" class="active">
				<div class="component-item">
					<h3>О программе</h3>
					<p><b>"Антивирус Монтировка"</b> - это набор утилит предназначенных не только для удаления самих вирусов, но и их последствий. При этом не только в ручную, но и полу автоматически.</p>
				</div>
				<div class="component-item">
					<h3>Ключевые отличия</h3>
					<p><b>"Антивирус Монтировка"</b> - это не обычный антивирус в привычном понимании. Большинство антивирусов о которых вы знаете - являются антивирусными "сканерами". Но Антивирус "Монтировка" не является антивирусным сканером, вместо этого используются более универсальные методы.</p>
					<p>Проект является свободным программным обеспечением на <b>Python</b> и распространяется по лицензии <b>GPL v3</b>. А значит каждый может узнать как работает программа и помочь в разработке</p>
				</div>
				<div class="component-item">
					<h3>Статус проекта</h3>
					<p><b>Учтите, что проект находится в стадии активной разработки, а именно в beta! А также на данный момент средства полуавтоматического обнаружения не доделаны до конца!</b> Однако программой уже вполне можно пользоваться, большая часть функционала уже реализована, а стабильность программы по сравнению с Pre-Alpha намного выше.</p>
				</div>
				<div class="component-item">
					<h3>Технические характеристики</h3>
					<ul>
						<li><b>Размер:</b> ~20 МБ</li>
						<li><b>Потребление ОЗУ:</b> ~30-130 МБ</li>
						<li><b>Тип файла:</b> .EXE</li>
						<li><b>Производительность:</b> Высокая</li>
						<li><b>Интерфейс:</b> Лёгкий, на базе tkinter, без иконок</li>
					</ul>
				</div>
			</section>


			<section id="install">
				<h2>Установка Антивируса Монтировка</h2>
				<div class="component-item">
					<h3>Для установки выполните следующие шаги:</h3>
					<ol>
						<li>Перейдите на <b><a href="https://anonimneo.github.io/NEO-Organization/Programs/Crowbar/crowbar.html" target="_blank">официальный сайт</a></b></li>
						<li>Нажмите на кнопку "Скачать исходный код"</li>
						<li>После того как вы попали на гитхаб, нажмите на пункт "релизы"</li>
						<li>Затем вы можете выбрать версию. Если вы хотите протестировать программу без полноценной установки - то ваш выбор "Готовый Антивирус Монтировка". Если же вы хотите установить и полноценно настроить программу под себя - то тогда ваш выбор "Установщик Антивируса Монтировка"</li>
						<li>После выбора скачайте из ресурсов .exe файл или .zip архив. Если вы скачиваете установщик, также скачайте архив с исходным кодом (sourcecode.zip)</li>
						<li>Если скачали готовый файл просто запустите его. Если установщик - то распакуйте архив (crowbar_antivirus_setup.zip) ЖЕЛАТЕЛЬНО не на рабочий стол! (так как в этом каталоге будет создано много файлов). Запустите установщик и следуйте его инструкциям.</li>
					</ol>
				</div>
				<div class="component-item">
					<h3>Системные требования для установки</h3>
					<ul>
						<li>Операционная система: Windows 10 и выше</li>
						<li>Для Компиляции (установки) программы ~1GB свободного места на диске.  Итоговый вес программы будет ~20MB.</li>
					</ul>
				</div>
			</section>

			<section id="requirements">
				<h2>Минимальные требования</h2>
				<p>Для корректной работы Антивируса Монтировка необходимо:</p>

				<div class="component-item">
					<h3>Аппаратные требования:</h3>
					<ul>
						<li><b>Процессор:</b> windows 10 - запустилась с первого раза? Тогда хватит</li>
						<li><b>Оперативная память:</b> windows 10 - запустилась с первого раза? Тогда хватит</li>
						<li><b>Место на диске:</b> для Компиляции (установки) программы ~1GB свободного места на диске.  Итоговый вес программы будет ~20MB.</li>
						<li><b>Видеокарта:</b> windows 10 - запустилась с первого раза? Тогда хватит</li>
					</ul>
				</div>

				<div class="component-item">
					<h3>Программные требования:</h3>
					<ul>
						<li><b>ОС:</b> Windows XP, Windows Vista, Windows 7, Windows 8, Windows 10, Windows 11</li>
						<li><b>Python:</b> (Для установки) версия 3.12 и выше</li>
						<li><b>Права доступа:</b> требуются права администратора</li>
					</ul>
				</div>

				<div class="component-item">
					<h3>Сетевые требования:</h3>
					<ul>
						<li><b>Интернет:</b> Не требуется</li>
						<li><b>Обновления:</b> Скачивайте новый архив с исходным кодом в программе откройте настройки и выберите этот архив</li>
					</ul>
				</div>
			</section>

			<section id="components">
				<h2>Компоненты Антивируса Монтировка</h2>
				<p>Программа состоит из так называемых "Компонентов", это полноценные утилиты которые взаимодействуют между собой, что даёт Антивирусу Монтировка мощный функционал. Нажмите на название компонента в меню слева для подробной информации.</p>

				<div id="components-content">
					<div id="autorunmaster" class="component-section active">
						<div class="component-item">
							<h3>Мастер Автозагрузки</h3>
							<p><b>Функционал:</b> Управление всей автозагрузкой ОС виндовс. Доступно не только удаление, но и изменение (если доступно для типа автозагрузки). Есть система оценивания угрозы значения автозагрузки в %. Также доступно удаление исполняемого файла и заморозка/убийство процесса данного файла.</p>
							<p><b>Принцип работы:</b> Компонент читает системные параметры автозагрузок (пользовательская, реестр и планировщик) анализирует значение и выводит результат по вкладкам в таблицу.</p>
							<p><b>Применение:</b> Помимо удаления вирусов из автозагрузки, данный функционал можно использовать на обычном ПО для оптимизации ОС.
						</div>
					</div>

					<div id="processmanager" class="component-section">
						<div class="component-item">
							<h3>Менеджер Процессов</h3>
							<p><b>Функционал:</b> Полное управление всеми запущенными процессами в системе (заморозка, разморозка, изменение критичности и убийство процесса).</p>
							<p><b>Принцип работы:</b> Загружает список всех запущенных процессов и их данные в таблицу (PID, имя, исполняемый файл, статус работы, критичность и пользователь). Также позволяет принудительно завершать процессы, включая те, которые не поддаются стандартному диспетчеру задач виндовс.</p>
							<p><b>Применение:</b> Безопасная заморозка или закрытие процессов вредоносного ПО.</p>
						</div>
					</div>

					<div id="filemanager" class="component-section">
						<div class="component-item">
							<h3>Файловый Менеджер</h3>
							<p><b>Функционал:</b> Навигация и все базовые операциями с файлами, поиск, получение прав на каталог или файл, а также интеграция с Редактором файлов для их редактирования.</p>
							<p><b>Принцип работы:</b> Загрузка всех каталогов и файлов с указанного каталога без исключений. Поиск происходит в отдельном потоке и загружает результаты постепенно (однако для оптимизации итоговая сортировка и возможность сортировать таблицу произойдёт после окончания поиска. Получение полных прав на каталог или файл происходит через команду icals</p>
							<p><b>Применение:</b> Удаление вредоносных файлов из защищённых каталогов, а также базовые операции с файлами.</p>
						</div>
					</div>

					<div id="unlockall" class="component-section">
						<div class="component-item">
							<h3>Разблокировка всего</h3>
							<p><b>Функционал:</b> Разблокировка ограничений групповых политик и дебагеров, а также блокировки доменов в hosts.</p>
							<p><b>Принцип работы:</b> Изменение значений в реестре, однако вместо тупого прописывания каждого ограничения и его нужного значения, данный компонент циклом перебирает все параметры меняя их значения, но система исключений позволяет гибко настраивать сброс ограничений даже на ПК в офисах или корпорациях, чтобы не повреждать конфигурацию ОС. Также данный Компонент автоматически проверяет и при необходимости восстанавливает значения параметров шрифтов в реестре.</p>
							<p><b>Применение:</b> Подготовительная или итоговая очистка последствий.</p>
						</div>
					</div>

					<div id="usermanager" class="component-section">
						<div class="component-item">
							<h3>Менеджер Пользователей</h3>
							<p><b>Функционал:</b> Управление локальными пользователями (создание, удаление и изменение пароля).</p>
							<p><b>Принцип работы:</b> Использование API виндовс, и возможность менять пароль пользователя на указанный.</p>
							<p><b>Применение:</b> Удаление вредоносных локальных учётных записей, восстановление контроля над системой.</p>
						</div>
					</div>

					<div id="fileeditor" class="component-section">
						<div class="component-item">
							<h3>Редактор файлов</h3>
							<p><b>Функционал:</b> Редактирование текстовых файлов (.txt, .bat, .ini и т.д), а также написание скриптов для Антивируса Монтировка. Также доступен поиск по тексту.</p>
							<p><b>Принцип работы:</b> С обычными файлами и поиском всё тривиально, а редактирование скриптов происходит как с обычным текстом, но при сохранении скрипт шифруется - это сделано для безопасности. (при открытии скрипт автоматически расшифруется).</p>
							<p><b>Применение:</b> Редактирование скриптов и чтение логов.</p>
						</div>
					</div>

					<div id="crowbarscipts" class="component-section">
						<div class="component-item">
							<h3>Обработчик Скриптов</h3>
							<p><b>Функционал:</b> Позволяет программе исполнять пользовательские скрипты.</p>
							<p><b>Принцип работы:</b> При передаче аргументов, открывает текстовые файлы в редакторе файлов, а если это был скрипт расшифрует его и выполнит.</p>
							<p><b>Применение:</b> Для упрощения диагностики или удаление вирусов.</p>
						</div>
					</div>

					<div id="restart" class="component-section">
						<div class="component-item">
							<h3>Перезапуск ОС</h3>
							<p><b>Функционал:</b> Выполняет перезапуск через встроенные команды виндовс.</p>
							<p><b>Принцип работы:</b> Выполнение перезапуска разными методами (запуск .bat файла, выполнение команды, выполнение команды через api виндовс).</p>
							<p><b>Применение:</b> Принудительный перезапуск в случае блокировки перезапуска через пуск или сочетания клавиш.</p>
						</div>
					</div>

					<div id="realtimeprotection" class="component-section">
						<div class="component-item">
							<h3>(Pre-Alpha) Защита в Реальном Времени</h3>
							<p><b>Функционал:</b> Полуавтоматическая защита в реальном времени.</p>
							<p><b>Принцип работы:</b> Анализ всех процессов на подозрительные факторы (название совпадает с названием системного файла, избыточная нагрузка на компоненты ПК и т.п).</p>
							<p><b>Применение:</b> Полуавтоматическая диагностика.</p>
						</div>
					</div>

					<div id="clearcache" class="component-section">
						<div class="component-item">
							<h3>Очистка Кэша</h3>
							<p><b>Функционал:</b> Очистка кэша (каталог %Temp%).</p>
							<p><b>Принцип работы:</b> Удаление всего содержимого %Temp% с логированием.</p>
							<p><b>Применение:</b> Очистка кэша вредоносного ПО или определения запущенных файлов в %Temp%.</p>
						</div>
					</div>

					<div id="browser" class="component-section">
						<div class="component-item">
							<h3>Браузер</h3>
							<p><b>Функционал:</b> Браузер система вкладок, возможность посещения онлайн, офлайн страниц, а также открытия html кода напрямую из переменной.</p>
							<p><b>Принцип работы:</b> Просто браузер на базе PyQt6 без лишнего и со стандартными защитами окна.</p>
							<p><b>Применение:</b> Просмотр документации (справки) и посещение онлайн страниц и скачивание файлов, не привлекая внимания вредоносного ПО.</p>
						</div>
					</div>

					<div id="replacer" class="component-section">
						<div class="component-item">
							<h3>Замена системных файлов</h3>
							<p><b>Функционал:</b> Позволяет заменить редко используемые системные файлы на другую программу, чтобы обойти защиту вредоносного ПО. Восстановить системные файлы можно одной кнопкой.</p>
							<p><b>Принцип работы:</b> В среде восстановления системные файлы не защищены - поэтому замена достаточно легка.</p>
							<p><b>Применение:</b> Обход защиты вируса.</p>
						</div>
					</div>

					<div id="run" class="component-section">
						<div class="component-item">
							<h3>Запуск от администратора</h3>
							<p><b>Функционал:</b> Запуск любых операций с повышенными правами.</p>
							<p><b>Принцип работы:</b> Если программа запущена от имени администратора то и другие программы запущенные от неё будут иметь права администратора.</p>
							<p><b>Применение:</b> Выполнение действий, требующих права администратора (например системные команды такие как sfc /scannow).</p>
						</div>
					</div>

					<div id="scarecrowprotection" class="component-section">
						<div class="component-item">
							<h3>Пугало от вирусов</h3>
							<p><b>Функционал:</b> Создание программ "обманок" полная структура файлов и значения в реестре реальных антивирусных программ или имитация работы в виртуальной машине - заставляют вирусов стилеров обходить вашу ОС стороной дабы не попасть в базу антивирусных сканеров.</p>
							<p><b>Принцип работы:</b> Компонент содержит списки файлов, параметров и других данных реальных программ которые он просто создаёт.</p>
							<p><b>Применение:</b> Пасивная защита от стилеров.</p>
						</div>
					</div>

					<div id="installmanager" class="component-section">
						<div class="component-item">
							<h3>(Pre-Alpha) Менеджер Установки</h3>
							<p><b>Функционал:</b> Отслеживание активности программы и мониторинг изменений.</p>
							<p><b>Принцип работы:</b> Мониторинг файловой системы, реестра, сетевой активности и активности процессов.</p>
							<p><b>Применение:</b> Установка программ через этот компонент позволит не только определить является ли ПО вредоносным нг и откатить изменения даже если это ПО не вредоносное.</p>
						</div>
					</div>
				</div>
			</section>

			<section id="why">
				<h2>Почему мы?</h2>
				<p>Антивирус Монтировка предлагает уникальный подход к защите и очистке системы, сочетая гибкость ручного управления с эффективностью полуавтоматических инструментов. В отличие от обычных антивирусов, мы фокусируемся не только на обнаружении угроз, но и на полном устранении их последствий. Также в отличие от других антивирусов в которых скудный выбор настройки, Антивирус Монтировка даёт полную свободу действий как минимум потому, что Антивирус Монтировка является open-source Программным Обеспечением.</p>
			</section>

			<section id="commercial">
				<h2>Коммерческое использование</h2>
				<p>Использование Антивируса Монтировка в коммерческих целях на данный момент строго запрещается! Это и касается произвольных "форков", без нашего согласия вы не имеете права продавать или использовать Антивирус Монтировка в коммерческих целях.</p>
			</section>

			<section id="update">
				<h2>Обновления</h2>
				<p>Для обновления вам необходимо скачать новую версию исходного кода (sourcecode.zip), открыть настройки программы и выбрать данный архив с новой версией, указать необходимые значения и выполнить компиляцию (это требует установленного python3.12+ и всех библиотек).</p>
			</section>

			<section id="faq">
				<h2>Вопросы и ответы</h2>
				<div class="component-item">
					<h3>Что такое Антивирус Монтировка?</h3>
					<p>Это набор утилит для удаления вирусов, их последствий с открытым исходным кодом.</p>
				</div>
				<div class="component-item">
					<h3>Нужны ли права администратора?</h3>
					<p>Да, для большинства функций требуются права администратора.</p>
				</div>
			</section>

			<section id="privacy">
				<h2>Конфиденциальность</h2>
				<div class="component-item">
					<b>Антивирус Монтировка не собирает никакие ваши личные данные!</b>
				</div>
				<div class="component-item">
					<p>Однако мы будем рады если вы отправите логи программы нам на почту (operawifi.mini.net.win.2000@gmail.com), в логах не содержится чувствительная или конфиденциальная информация (функция анонимных отчётов в разработке). Но это поможет в разработке программы.</p>
				</div>
			</section>

			<section id="contacts">
				<h2>Контакты</h2>
				<div class="component-item">
					<h2>Создано благодаря:</h2>
					<img width="256" height="256" src="img/NEO_Organization.png">
					<h2>NEO Organization</h2>
				</div>
				<div class="component-item">
					<h2>При поддержке:</h2>
					<img width="256" height="256" src="img/Departamnet_K.png">
					<h2>Departament K</h2>
				</div>
				<div class="component-item">
					<h2>Программисты:</h2>
					<h2 class="programmer">AnonimNEO</h2>
				</div>
				<div class="component-item">
					<h2>Язык программирования:</h2>
					<img width="256" height="256" src="img/Python.png">
					<h2>Python</h2>
				</div>
				<div class="component-item">
					<h2>Лицензия:</h2>
					<img width="256" height="256" src="img/GPLv3.png">
					<h2>GPLv3</h2>
				</div>
				<div class="component-item">
					<h2>Электронная почта:</h2>
					<a href="mailto:operawifi.mini.net.win.2000@gmail.com"><h2><img width="256" height="256" src="img/Gmail.png"></h2></a>
					<a href="mailto:operawifi.mini.net.win.2000@gmail.com"><h2>operawifi.mini.net.win.2000@gmail.com</h2></a>
				</div>
				<div class="component-item">
					<h2>YouTube:</h2>
					<a href="https://www.youtube.com/channel/UCZvOEU_IDRsfK5j-JoNAVWg" target="_blank"><img width="512" height="256" src="img/YouTube_K.png"></a>
					<a href="https://www.youtube.com/channel/UCZvOEU_IDRsfK5j-JoNAVWg" target="_blank"><h3>YouTube Отдела К</h3></a>
				</div>
			</section>
		</main>
	</div>

	<script>
		const sidebar = document.getElementById("sidebar");
		const sidebarContainer = document.getElementById("sidebarContainer");
		const toggleSidebar = document.getElementById("toggleSidebar");

		function hideAllSections() {
			document.querySelectorAll("main.content > section").forEach(sec => sec.classList.remove("active"));
			document.querySelectorAll(".component-section").forEach(sec => sec.classList.remove("active"));
		}

		function showSection(id) {
			hideAllSections();
			const section = document.getElementById(id);
			if (section) section.classList.add("active");
		}

		function showComponent(id) {
			hideAllSections();
			const componentsSection = document.getElementById("components");
			const component = document.getElementById(id);
			if (componentsSection) componentsSection.classList.add("active");
			if (component) component.classList.add("active");
		}

		toggleSidebar.addEventListener("click", () => {
			sidebar.classList.toggle("collapsed");
			sidebarContainer.classList.toggle("collapsed");
		});

		("about");
	</script>
</body>
</html>
"""
