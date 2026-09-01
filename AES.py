# Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
# Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
# ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
# В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
# ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
# Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
# Или в файле COPYING.txt в архиве с установщиком
# Copyleft 🄯 NEO Organization, Departament K 2024 - 2026
# Coded by AnonimNEO (Github)

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
try:
    from OF import Logger
    logger = Logger()
except:
    from loguru import logger
import hashlib
import base64
import os

def AES(text, password, decrypt=False, DEBUG_MODE=False):
    """
    Универсальная функция шифрования/расшифровки AES-256-CBC с PBKDF2
    text - Текст для шифрования ИЛИ зашифрованная текст для расшифровки
    password (str) - Пароль для шифрования/расшифровки
    decrypt - True для расшифровки, False для шифрования
    return - Текст или None при ошибке
    """
    try:
        # Расшифровка
        if decrypt:
            # Декодируем base64
            text = text.strip()
            encrypted_data = base64.b64decode(text)
            if DEBUG_MODE:
                logger.debug(f"AES - Декодировано из base64: {len(encrypted_data)} байт")

            # Извлекаем компоненты
            if len(encrypted_data) < 32:
                return None

            salt = encrypted_data[:16]
            iv = encrypted_data[16:32]
            ciphertext = encrypted_data[32:]

            # Генерируем ключ из пароля
            key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)

            # Расшифровываем
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Удаляем PKCS7 паддинг
            padding_length = padded_plaintext[-1]

            if padding_length < 1 or padding_length > 16:
                logger.error(f"AES - Ошибка паддинга: {padding_length} (возможно, неверный пароль)")
                return None

            plaintext = padded_plaintext[:-padding_length]
            result = plaintext.decode("utf-8")
            logger.debug(f"AES - Расшифровано успешно: {len(result)} символов")
            return result

        # Шифрования
        else:
            # Генерируем соль и IV
            salt = os.urandom(16)
            iv = os.urandom(16)

            # Генерируем ключ из пароля
            key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)

            # Добавляем PKCS7 паддинг
            plaintext = text.encode("utf-8")
            padding_length = 16 - (len(plaintext) % 16)
            padded_plaintext = plaintext + bytes([padding_length] * padding_length)

            # Шифруем
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

            # Объединяем и кодируем в base64
            encrypted_data = salt + iv + ciphertext
            result = base64.b64encode(encrypted_data).decode("utf-8")
            if DEBUG_MODE:
                logger.debug(f"AES - Зашифровано успешно: {len(result)} символов (base64)")
            return result

    except:
        logger.exception(f"AES - Неизвестная ошибка")
        return None


if __name__ == "__main__":
    decrypt = input("Расшифруем? ").strip().lower() in ("1", "true", "yes", "y", "да")
    print(AES(input("Текст: "), input("Ключ: "), decrypt))