# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

import sys
import os
from pathlib import Path
from urllib.parse import urlparse

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QTabWidget, QMessageBox, QFileDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QUrl, Qt, QThread, pyqtSignal

try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
from RS import RS
from config import *
from languages import l

browser_version = "0.2.8 Beta"

# страница для контроля открытия ссылок и скачиваний
class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, browser_window, parent=None):
        super().__init__(parent)
        self.browser_window = browser_window

        # Подключаем сигнал скачивания
        self.profile().downloadRequested.connect(self.on_download_requested)



    def createWindow(self, window_type):
        # Создаём новую вкладку вместо нового окна
        self.browser_window.add_new_tab()
        return self.browser_window.get_current_browser().page()



    def on_download_requested(self, download):
        # Получаем имя файла и URL
        file_name = download.suggestedFileName()
        download_url = download.url().toString()

        # Открываем диалог сохранения
        file_path, _ = QFileDialog.getSaveFileName(
            self.browser_window,
            RS(),
            file_name,
            "All Files (*.*)"
        )

        if file_path:
            # Если пользователь выбрал путь, устанавливаем его
            download.setDownloadFileName(file_path)

            # Принимаем скачивание
            download.accept()

            if self.browser_window.log:
                logger.info(f"B - {l("download_start")}: {file_name} -> {file_path}")

            # Подключаемся к сигналам завершения/ошибки
            download.isFinishedChanged.connect(
                lambda: self.on_download_finished(file_path, file_name) if download.isFinished() else None
            )
        else:
            # Если пользователь отменил диалог, отклоняем скачивание
            download.cancel()
            if self.browser_window.log:
                logger.info(f"B - {l("download_cancel")}: {file_name}")



    def on_download_finished(self, file_path, file_name):
        if self.browser_window.log:
            logger.info(f"B - {l("download_completed")}: {file_name}")

        QMessageBox.information(
            self.browser_window,
            RS(),
            f"{l("file_download_on")} \n{file_path}"
        )



    def on_download_failed(self, file_name):
        if self.browser_window.log:
            logger.error(f"B - {l("download_fail")}: {file_name}")

        QMessageBox.critical(
            self.browser_window,
            RS(),
            f"{l("download_fail")}: {file_name}"
        )



class BrowserWindow(QMainWindow):
    def __init__(self, DEBUG_MODE=False, url="https://duckduckgo.com", file=False, html=False):
        super().__init__()

        self.DEBUG_MODE = DEBUG_MODE
        self.current_theme = default_theme
        self.tabs = []

        self.setWindowTitle(RS())
        self.setGeometry(100, 100, 1400, 900)

        # Главный виджет
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # панель
        control_panel = QHBoxLayout()
        control_panel.setContentsMargins(5, 5, 5, 5)
        control_panel.setSpacing(5)

        # Кнопки навигации
        self.btn_back = QPushButton("←")
        self.btn_back.setMaximumWidth(40)
        self.btn_back.setMaximumHeight(35)
        self.btn_back.clicked.connect(self.go_back)
        control_panel.addWidget(self.btn_back)

        self.btn_forward = QPushButton("→")
        self.btn_forward.setMaximumWidth(40)
        self.btn_forward.setMaximumHeight(35)
        self.btn_forward.clicked.connect(self.go_forward)
        control_panel.addWidget(self.btn_forward)

        self.btn_refresh = QPushButton("↻")
        self.btn_refresh.setMaximumWidth(40)
        self.btn_refresh.setMaximumHeight(35)
        self.btn_refresh.clicked.connect(self.refresh_page)
        control_panel.addWidget(self.btn_refresh)

        # Адресная строка
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText(l("enter_url_or_file_path"))
        self.address_bar.setMaximumHeight(35)
        self.address_bar.returnPressed.connect(self.load_from_address_bar)
        control_panel.addWidget(self.address_bar)

        # Выбор темы
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(theme.keys())
        self.theme_selector.currentTextChanged.connect(lambda: self.apply_theme(theme_name))
        self.theme_selector.setMaximumWidth(120)
        self.theme_selector.setMaximumHeight(35)
        control_panel.addWidget(self.theme_selector)

        # Добавляем панель управления в главный layout
        control_panel_widget = QWidget()
        control_panel_widget.setMaximumHeight(50)
        control_panel_widget.setLayout(control_panel)
        main_layout.addWidget(control_panel_widget)

        # вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"QTabBar::tab {{ height: 30px; }}")
        self.tab_widget.setMovable(True) # Возможность перетаскивать вкладки
        self.tab_widget.setTabsClosable(True) # Кнопка закрытия на вкладке
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Кнопка "+" для добавления новой вкладки
        self.btn_new_tab = QPushButton("+")
        self.btn_new_tab.setMaximumWidth(40)
        self.btn_new_tab.setMaximumHeight(30)
        self.btn_new_tab.clicked.connect(self.add_new_tab)
        self.tab_widget.setCornerWidget(self.btn_new_tab, Qt.Corner.TopRightCorner)

        main_layout.addWidget(self.tab_widget)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Создаём первую вкладку
        self.create_tab(l("new_tab"))

        # Загружаем содержимое в первую вкладку
        current_browser = self.get_current_browser()
        if html:
            self.load_html(html)
            if DEBUG_MODE:
                logger.debug(f"B - {l("html_loaded")}")
        elif file:
            self.load_file(url)
            if DEBUG_MODE:
                logger.debug(f"B - {l("file_loaded")}: {url}")
        else:
            self.load_url(url)
            if DEBUG_MODE:
                logger.debug(f"B - {l("page_loaded")}: {url}")

        current_browser.urlChanged.connect(self.on_url_changed)

        # Применяем тему
        self.apply_theme(self.current_theme)



    def create_tab(self, title=l("new_tab")):
        browser = QWebEngineView()

        # Устанавливаем кастомную страницу для контроля ссылок и скачиваний
        custom_page = CustomWebEnginePage(self, browser)
        browser.setPage(custom_page)

        self.tabs.append(browser)
        self.tab_widget.addTab(browser, title)
        self.tab_widget.setCurrentWidget(browser)

        # Подключаем сигнал изменения URL
        browser.urlChanged.connect(self.on_url_changed)



    # Открываем нвовую вкладку
    def add_new_tab(self):
        self.create_tab(l("new_tab"))
        current_browser = self.get_current_browser()
        current_browser.setUrl(QUrl("https://duckduckgo.com"))



    # Закрываем вкладку
    def close_tab(self, index):
        if len(self.tabs) > 1:
            self.tab_widget.removeTab(index)
            self.tabs.pop(index)
        else:
            self.close()



    # Смена вкладки
    def get_current_browser(self):
        current_widget = self.tab_widget.currentWidget()
        return current_widget if isinstance(current_widget, QWebEngineView) else None



    # Кнопка <-
    def go_back(self):
        browser = self.get_current_browser()
        if browser:
            browser.back()



    # Кнопка ->
    def go_forward(self):
        browser = self.get_current_browser()
        if browser:
            browser.forward()



    # Кнопка |-> (обновить)
    def refresh_page(self):
        browser = self.get_current_browser()
        if browser:
            browser.reload()



    # Загружаем ссылку
    def load_url(self, url):
        browser = self.get_current_browser()
        if browser:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            browser.setUrl(QUrl(url))



    # Загружаем файл
    def load_file(self, file_path):
        path = Path(file_path)
        if path.exists():
            file_url = QUrl.fromLocalFile(str(path.absolute()))
            browser = self.get_current_browser()
            if browser:
                browser.setUrl(file_url)
            if DEBUG_MODE:
                logger.debug(f"B - {l("file_loaded")}: {file_path}")
        else:
            if DEBUG_MODE:
                logger.error(f"B - {l("file_not_found")}: {file_path}")
            QMessageBox.critical(self, RS(), f"{l("file_not_found")}:\n{file_path}")



    # Загружаем HTML код из переменной
    def load_html(self, html_content):
        browser = self.get_current_browser()
        if browser:
            browser.setHtml(str(html_content))



    # Загружаем ссылку из адресной строки
    def load_from_address_bar(self):
        text = self.address_bar.text().strip()
        if not text:
            return

        if text.startswith("/") or text.startswith("C:\\") or text.startswith(".\\"):
            self.load_file(text)
        else:
            self.load_url(text)



    # Обновляем адресную строку и заголовок вкладки
    def on_url_changed(self, url):
        self.address_bar.setText(url.toString())

        # Обновляем название вкладки
        browser = self.get_current_browser()
        if browser:
            title = browser.page().title()
            if not title:
                title = url.toString()

            current_index = self.tab_widget.currentIndex()
            self.tab_widget.setTabText(current_index, title[:30])  #  Обрезаем название



    # Применяем тему
    def apply_theme(self, theme_name):
        global theme
        theme = theme[theme_name]
        self.current_theme = theme_name

        # CSS стили для интерфейса
        style_sheet = f"""
        QMainWindow {{
            background-color: {theme["bg"]};
        }}
        QLineEdit {{
            background-color: {theme["abg"]};
            color: {theme["afg"]};
            border: 1px solid {theme["bfg"]};
            border-radius: 4px;
            padding: 5px;
        }}
        QPushButton {{
            background-color: {theme["bbg"]};
            color: {theme["bfg"]};
            border: none;
            border-radius: 4px;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {theme["tfg"]};
        }}
        QComboBox {{
            background-color: {theme["abg"]};
            color: {theme["afg"]};
            border: 1px solid {theme["bfg"]};
            border-radius: 4px;
            padding: 5px;
        }}
        QTabWidget {{
            background-color: {theme["bg"]};
        }}
        QTabBar::tab {{
            background-color: {theme["bbg"]};
            color: {theme["bfg"]};
            padding: 5px 15px;
        }}
        QTabBar::tab:selected {{
            background-color: {theme["tbg"]};
            color: {theme["tfg"]};
        }}
        """

        self.setStyleSheet(style_sheet)



# Если file=True, url рассматривается как путь к файлу
# html - HTML код для отображения в строковой переменной
def B(url="https://duckduckgo.com", file=False, html=False, RUN_IN_RECOVERY=False, DEBUG_MODE=False):
    if DEBUG_MODE:
        logger.debug(f"B -{l("browser_called")} : url={url}, file={file}, html={html}, RUN_IN_RECOVERY={RUN_IN_RECOVERY}")

    if RUN_IN_RECOVERY:
        QMessageBox.warning(None, RS(), l("browser_run_in_recovery"))

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    browser_window = BrowserWindow(
        DEBUG_MODE=DEBUG_MODE,
        url=url,
        file=file,
        html=html
    )
    browser_window.show()

    app.exec()

if __name__ == "__main__":
    B()
