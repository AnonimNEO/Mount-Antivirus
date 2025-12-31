#Данное Свободное Программное Обеспечение распространяется по лицензии GPL-3.0-only или GPL-3.0-or-later
#Вы имеете право копировать, изменять, распространять, взимать плату за физический акт передачи копии, и вы можете по своему усмотрению предлагать гарантийную защиту в обмен на плату
#ДЛЯ ИСПОЛЬЗОВАНИЯ ДАННОГО СВОБОДНОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ, ВАМ НЕ ТРЕБУЕТСЯ ПРИНЯТИЕ ЛИЦЕНЗИИ Gnu GPL v3.0 или более поздней версии
#В СЛУЧАЕ РАСПРОСТРАНЕНИЯ ОРИГИНАЛЬНОЙ ПРОГРАММЫ И/ИЛИ МОДЕРНИЗИРОВАННОЙ ВЕРСИИ И/ИЛИ ИСПОЛЬЗОВАНИЕ ИСХОДНИКОВ В СВОЕЙ ПРОГРАММЕ, ВЫ ОБЯЗАНЫ ЗАДОКУМЕНТИРОВАТЬ ВСЕ ИЗМЕНЕНИЯ В КОДЕ И ПРЕДОСТАВИТЬ ПОЛЬЗОВАТЕЛЯМ ВОЗМОЖНОСТЬ ПОЛУЧИТЬ ИСХОДНИКИ ВАШЕЙ КОПИИ ПРОГРАММЫ, А ТАКЖЕ УКАЗАТЬ АВТОРСТВО ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ
#ПРИ РАСПРОСТРАНЕНИИ ПРОГРАММЫ ВЫ ОБЯЗАНЫ ПРЕДОСТАВИТЬ ВСЕ ТЕЖЕ ПРАВА ПОЛЬЗОВАТЕЛЮ ЧТО И МЫ ВАМ, А ТАКЖЕ ЛИЦЕНЗИЯ GPL v3
#Прочитать полную версию лицензии вы можете по ссылке Фонда Свободного Программного Обеспечения - https://www.gnu.org/licenses/gpl-3.0.html
#Или в файле COPYING.txt в архиве с установщиком
#Copyleft 🄯 NEO Organization, Departament K 2024 - 2025
#Coded by @AnonimNEO (Telegram)

knot_version = "0.5.5 Beta"

symbol_list = '`~!@#$%^&*()"№;:?-_+=[]{}|/\<>.,' + "'"
cyrillic_list = "абвгдеёжзийклмопрстуфъцчшщъыьэюя"
latin_list = "abcdefghijklmnopstuvxyz"
number_list = "0123456789"

def K(code, text, encryption=True, debug_mode=False):
	if debug_mode:
		print(f"Шифровщик Узел версии {knot_version}")
		print("Включен Debug Mode")
		print(f"Ключ Шифрования: {code}\nТекст: {text}\nШифрование: {encryption}")
	text = text.lower()
	final_text = ""
	if len(code) < len(text):
		result_len = len(text) - len(code)
		result_code = code
		final_for = -1
		for i in range(result_len):
			if i > len(code):
				final_for += 1
				result_code += code[final_for]
			elif i < len(code):
				result_code += code[i]
		code = result_code

	def varible_symbol(index, list, _number_code=0):
		_number_code = int(_number_code)
		index += _number_code
		while True:
			index -= len(list)
			if index == len(list)-1 or index == len(list):
				print("sas")
				index -= len(list)
			if index < len(list)-1:
				break
		return index

	try:
		a = int(code)
		del(a)
	except Exception:
		if debug_mode:
			print("Код шифрования содержит буквы перевод в числа...")
		final_code = ""
		for i in range(len(code)):
			number = code[i]
			_code = code[i]

			if _code in cyrillic_list:
				_code_ = cyrillic_list.index(_code)
			elif _code in latin_list:
				_code_ = latin_list.index(_code)
			elif _code in number_list:
				_code_ = number_list.index(_code)
			elif _code in symbol_list:
				_code_ = symbol_list.index(_code)

			if number in cyrillic_list:
				#_number = cyrillic_list.index(number)
				#if (_number+_code_) > len(cyrillic_list)-1:
				#	number = varible_symbol(_number, cyrillic_list, _code_)
				final_number = cyrillic_list.index(_code)
			elif number in latin_list:
				#_number = latin_list.index(number)
				#if (_number+_code_) > len(latin_list)-1:
				#	number = varible_symbol(_number, latin_list, _code_)
				final_number = latin_list.index(_code)
			elif number in number_list:
				if not encryption:
					number = int(number)
					number = -number
				number = int(number)
				if (number+_code_) > len(number_list)-1:
					number = varible_symbol(number, number_list, _code_)
				final_number = number_list[number]
			elif number in symbol_list:
				#_number = symbol_list.index(number)
				#if (_number+_code_) > len(symbol_list)-1:
				#	number = varible_symbol(_number, symbol_list, _code_)
				final_number = symbol_list.index(_code)
			else:
				print("Обнаружен неизвестный символ, пропуск")
				final_number = number

			final_code += str(final_number)

		code = final_code

	if debug_mode:
		print("Работа с текстом...")

	for i in range(len(text)):
		letter = text[i]
		if encryption:
			number_code = code[i]
			_number_code = int(number_code)
			if _number_code == 0:
				_number_code = 1
		elif not encryption:
			number_code = code[i]
			number_code = int(number_code)
			if number_code == 0:
				_number_code = -1
			else:
				_number_code = -number_code

		current_list = None
		if letter in cyrillic_list:
			current_list = cyrillic_list
		elif letter in latin_list:
			current_list = latin_list
		elif letter in number_list:
			current_list = number_list
		elif letter in symbol_list:
			current_list = symbol_list

		if current_list:
			index_letter = current_list.index(letter)
			new_index = (index_letter + _number_code) % len(current_list)
			final_letter = current_list[new_index]
		else:
			final_letter = letter

		final_text += final_letter

	final_text += final_letter

	return final_text