import csv
import os
import shutil
import re
import time

from pandas import Series

from colorama import init, Fore, Style
init(autoreset=True)


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



