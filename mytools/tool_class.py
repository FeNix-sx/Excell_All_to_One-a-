import csv
import os
import time
import openpyxl


from datetime import datetime
from pandas import Series
from colorama import init, Fore, Style

from mytools.working_to_yadisk import WorkingYandexDisk
from mytools.setting import setting

init(autoreset=True)

class ColorInput:
    def __init__(self, patern: list=None) -> None:
        self.__patern = [
            item.strftime('%d.%m.%Y') for item in self.__check_value(patern)
        ]

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
                input_data = datetime.strptime(input_data, '%d.%m.%Y')

                if datetime.strptime(self.__patern[0], '%d.%m.%Y') <= \
                        input_data \
                        <= datetime.strptime(self.__patern[1], '%d.%m.%Y'):
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

    def print_yellow(self, *args, **kwargs):
        self.__print(Fore.YELLOW + Style.BRIGHT, *args, **kwargs)


class CodeNamePhone:
    """принимает имя файла *.xlsx, из которого потом может прочитать значения"""
    def __init__(self, filename):
        self.__filename = self.__chek_name(filename)

        # self.token = setting.token
        self.token = 'y0_AgAAAAABJQnxAAkufQAAAADiFPV_TjOFwUIbR6KNgvJ5KSFpjefPkow'

    def __chek_name(self, filename: str) -> str:
        if filename.endswith("models.xlsx"):
            return filename
        else:
            print("Ошибка! Не найден файл 'models.xlsx', или имя файла изменено!")

    @property
    def get_names_code_csv(self) -> dict:
        """
        Читает модели телефона из файла csv и возвращает словарь с ними:
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

    @property
    def get_names_code_xlsx(self)->dict:
        """
        Читает модели телефона из файла xlsx и возвращает словарь с ними:
        ключ - название (вместо "/" пробел)
        значение - код из 6 цифр
        :return: dict (ключ: str, значения: list)
        """
        try:
            # загрузка файла моделей с яндекса
            self.download_models_to_yadisk(filename=self.__filename)
            # обработка файла моделей
            workbook = openpyxl.load_workbook(self.__filename)
            sheet = workbook.active
            models = {}

            for row in sheet.iter_rows(min_row=2):
                key = row[0].value
                value = row[1].value.split(",")

                if key:
                    models[key] = value

            os.remove(self.__filename)
            return models

        except Exception as ex:
            print(ex)
            print(f"Не удалось загрузить список смартфоном. Возможно отсутствует файл {self.__filename}")
            return False

    def download_models_to_yadisk(self, filename: str)->None:
        try:
            yadisk = WorkingYandexDisk(yandex_token=self.token)
            yadisk.download_to_yd()

        except Exception as ex:
            print(ex)


class NamesPhone:
    def __init__(self):
        self.__phonename: dict=self.__chek_folder_name()
        if not self.__phonename:
            raise ConnectionError(f"Не удалось загрузить список смартфоном. Возможно отсутствует файл c моделями с яндекс-диска!")

    def __chek_folder_name(self) -> dict:
        """проверка загрузки файла с моделями models.xlsx"""
        try:
            # название файла берется из файла с настройками
            file_models = setting.models
            names_codes_dict: dict=CodeNamePhone(file_models).get_names_code_xlsx
            return names_codes_dict

        except ValueError:
            print(
                Fore.LIGHTRED_EX + f"Ошибка! Должна быть одна папка с названием/кодом телефона.\n",
                Fore.LIGHTRED_EX + f"Проверьте наличие папки, её название или удалите лишние папки.",
                sep=''
            )
            time.sleep(3)
            return False

    def __rename_folder(self, old_name: str, new_name: str)->None:
        os.rename(old_name, new_name)

    def __find_name(self, item: str)->str:
        """ ищет соответсвие кода телефона его названию"""
        item = item.split("d")[0]

        for key, value in self.__phonename.items():
            if item in value:
                return key

    def get_series_names_phone(self, series: Series)->Series:
        """
        Получает pandas.Series из кодов телефонов, и возвращает Series из названий телефонов
        :param series: Series из кодов телефонов
        :return: Series
        """
        try:
            result = Series(self.__find_name(item) for item in series)
            return result
        except Exception as ex:
            print(f"Ошибка! {ex}")

    def get_name_print(self, series: Series) -> Series:
        result = Series(self.__split_text(item) for item in series)
        return result

    @staticmethod
    def __split_text(string: str)->str:
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
    def get_phonename(self) -> dict:
        return self.__phonename
