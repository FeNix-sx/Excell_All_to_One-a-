import csv
import os
import time
from datetime import datetime

from pandas import Series
from colorama import init, Fore, Style
init(autoreset=True)

class ColorInput:
    def __init__(self, patern: list=None) -> None:
        self.__patern = self.__check_value(patern)

    @staticmethod
    def __check_value(patern):
        if patern and isinstance(patern, list):
            return patern
        else:
            raise ValueError(Fore.LIGHTRED_EX + Style.BRIGHT + "Не задан список допустимых значений")

    def cinput_date(self, message):
        while True:
            try:
                input_data = input(Fore.CYAN + Style.BRIGHT + message)

                if  self.__patern[0] <= datetime.strptime(input_data, '%d.%m.%Y') <= self.__patern[1]:
                    break
                else:
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "Дата за пределами диапазона. Повторите попытку.")

            except Exception as ex:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + "Ошибка! Формат ввода 00.00.0000\nПовторите попытку.")

        return input_data

    def cinput_int(self, message):
        while True:
            try:
                index = input(Fore.CYAN + Style.BRIGHT + message)

                if int(index) in list(range(1, 4)):
                    break
                else:
                    print(Fore.LIGHTRED_EX + Style.BRIGHT + "Неверное значение. Повторите попытку.")

            except Exception as ex:
                print(Fore.LIGHTRED_EX + Style.BRIGHT + "Ошибка! Формат ввода 00.00.0000\nПовторите попытку.")

        return int(index)

class ColorPrint:

    def __print(self, color_style, *args, **kwargs):
        message = [color_style + arg for arg in args]
        print(*message, **kwargs)
    def print_error(self, *args, **kwargs):
        self.__print(Fore.LIGHTRED_EX + Style.BRIGHT, *args, **kwargs)

    def print_info(self, *args, **kwargs):
        self.__print(Fore.GREEN + Style.BRIGHT, *args, **kwargs)

    def print_warning(self, *args, **kwargs):
        self.__print(Fore.CYAN + Style.BRIGHT, *args, **kwargs)


class CodeNamePhone:
    def __init__(self, filename):
        self.__filename = self.__chek_name(filename)

    def __chek_name(self, filename: str) -> str:
        if filename.endswith("models.csv"):
            return filename
        else:
            print("Ошибка! Не найден файл 'models.csv', или имя файла изменено!")

    @property
    def get_names_code(self) -> dict:
        """
        Читает модели телефона возвращает словарь с ними:
        ключ - название (вместо "/" пробел)
        значение - код из 6 цифр
        :return: dict
        """
        try:
            name_code_dict = dict()
            with open(self.__filename, encoding='utf-8') as r_file:
                # Создаем объект reader, указываем символ-разделитель ";"
                file_reader = csv.reader(r_file, delimiter=";")
                print("Файл с моделями загружен")
                # Счетчик для подсчета количества строк и вывода заголовков столбцов
                count = 0
                # Считывание данных из CSV файла
                for row in file_reader:
                    if count > 0:
                        # запись в словарь имен из файла с моделями
                        name_code_dict[row[0]] = row[1].replace("/", " ")

                    count += 1

                print(f'Найдено моделей телефонов: {count}.')

                return name_code_dict

        except Exception as ex:
            print(ex)
            print("Не удалось загрузить список смартфоном. Возможно отсутствует файл 'models.csv'")
            return None


class NamesPhone:
    def __init__(self):
        self.__phonename = self.__chek_folder_name()

    def __chek_folder_name(self) -> dict:
        try:
            names_codes_dict: dict = CodeNamePhone("models.csv").get_names_code
            return names_codes_dict

        except ValueError:
            print(
                Fore.LIGHTRED_EX + f"Ошибка! Должна быть одна папка с названием/кодом телефона.\n",
                Fore.LIGHTRED_EX + f"Проверьте наличие папки, её название или удалите лишние папки.",
                sep=''
            )
            time.sleep(3)
            return False

    def __rename_folder(self, old_name: str, new_name: str) -> None:
        os.rename(old_name, new_name)

    def get_names_phone(self, series: Series) -> Series:
        """
        Получает pandas Series из кодов телефонов, и возвращает Series из названий телефонов
        :param series:
        :return:
        """
        try:
            result = Series(self.__phonename[item] for item in series)
            return result
        except Exception as ex:
            print(f"Ошибка! {ex}")

    def get_name_print(self, series: Series) -> Series:
        result = Series(self.__split_text(item) for item in series)
        return result

    @staticmethod
    def __split_text(string: str):
        try:
            if " с принтом " in string:
                return string.split(" с принтом ")[1]
            elif " принт " in string:
                return string.split(" принт ")[1]
            else:
                return string
        except Exception as ex:
            print(f"Ошибка! {ex}")

    @property
    def get_code_name(self) -> str:
        return self.__phonename