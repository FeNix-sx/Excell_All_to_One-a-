import csv
import os
import time
import openpyxl
import requests
import subprocess

from datetime import datetime
from pandas import Series
from colorama import init, Fore, Style
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
    """принимает имя файла csv, из которого потом может прочитать значения"""
    def __init__(self, filename):
        self.__filename = self.__chek_name(filename)

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
        Читает модели телефона из файла csv и возвращает словарь с ними:
        ключ - название (вместо "/" пробел)
        значение - код из 6 цифр
        :return: dict (ключ: str, значения: list)
        """
        try:
            workbook = openpyxl.load_workbook(self.__filename)
            sheet = workbook.active
            models = {}

            for row in sheet.iter_rows(min_row=2):
                key = row[0].value
                value = row[1].value.split(",")

                if key:
                    models[key] = value

            return models

        except Exception as ex:
            print(ex)
            print("Не удалось загрузить список смартфоном. Возможно отсутствует файл 'models.xlsx'")
            return None


class NamesPhone:
    def __init__(self):
        self.__phonename = self.__chek_folder_name()

    def __chek_folder_name(self) -> dict:
        """проверка загрузки файла с моделями models.xlsx"""
        try:
            names_codes_dict: dict = CodeNamePhone("models.xlsx").get_names_code_xlsx
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

    def __find_name(self, item):
        item = item.split("d")[0]
        for key, value in self.__phonename.items():
            if item in value:
                return key

    def get_names_phone(self, series: Series) -> Series:
        """
        Получает pandas Series из кодов телефонов, и возвращает Series из названий телефонов
        :param series:
        :return:
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


class StatisticColection:
    def __init__(self):
        self.__collection_dict = dict()

    @staticmethod
    def __out_error(error_srt: str)->None:
        print(error_srt)

    def __out_info(self, text: str, func=print, sleep_time: float=0.025) -> None:
        try:
            for i in text:
                func(i, end='', flush=False)
                time.sleep(sleep_time)
            print()
        except Exception as ex:
            self.__out_error(ex)

    def get_my_ip(self) -> str:
        try:
            response = requests.get('https://api.ipify.org?format=json')
            ip = response.json()['ip']
            self.__collection_dict['IP'] = ip
            return ip

        except Exception as ex:
            self.__out_error(ex)

    def get_my_country(self) -> dict:
        try:
            url = f'http://ip-api.com/json/{self.__collection_dict["IP"]}'
            response = requests.get(url).json()

            self.__collection_dict = {
                'IP': response.get('query'),
                'Prov': response.get('isp'),
                'Org': response.get('org'),
                'Country': response.get('country'),
                'regionName': response.get('regionName'),
                'lat': response.get('lat'),
                'lon': response.get('lon')
            }
            return self.__collection_dict

        except Exception as ex:
            self.__out_error(ex)

    def my_cpu(self) -> None:
        try:
            # Получить модель процессора
            cmd_cpu = "wmic cpu get name"
            result_cpu = [
                item.strip() for item in subprocess.run(cmd_cpu, capture_output=True, text=True).stdout.split('\n') if item
            ]
            self.__collection_dict['CPU'] = ', '.join(result_cpu)

        except Exception as ex:
            self.__out_error(ex)

    def my_mohter_board(self) -> None:
        try:
            # Получить модель материнской платы
            cmd_motherboard = "wmic baseboard get product"
            result_motherboard = [
                item.strip() for item in subprocess.run(cmd_motherboard, capture_output=True, text=True).stdout.split('\n')
                if item
            ]
            self.__collection_dict['MB'] = ', '.join(result_motherboard)

        except Exception as ex:
            self.__out_error(ex)

    def my_gpu(self) -> None:
        try:
            # Получить информацию о видеокарте
            cmd_gpu = "wmic path win32_videocontroller get name"
            result_gpu = [
                item.strip() for item in subprocess.run(cmd_gpu, capture_output=True, text=True).stdout.split('\n') if item
            ]
            self.__collection_dict['GPU'] = ', '.join(result_gpu)

        except Exception as ex:
            self.__out_error(ex)

    def my_cmd_memory(self) -> None:
        try:
            # Получить информацию об оперативной памяти
            cmd_memory = "wmic memorychip get capacity"
            result_memory = subprocess.run(cmd_memory, capture_output=True, text=True).stdout.strip().split('\n')

            memory_modules = [
                str(int(memory.strip()) / (1024 ** 3)) + ' GB' for memory in result_memory if memory.strip().isdigit()
            ]
            self.__collection_dict['Memory'] = ', '.join(memory_modules)

        except Exception as ex:
            self.__out_error(ex)

    def my_os(self) -> None:
        try:
            # Получить установленную версию операционной системы
            cmd_os_version = "wmic os get caption"
            result_os_version = [
                item.encode('cp1251').decode('cp1251') for item in
                subprocess.run(cmd_os_version, capture_output=True, text=True).stdout.split()
            ]
            self.__collection_dict['OS version'] = ' '.join(result_os_version)

        except Exception as ex:
            self.__out_error(ex)
    @property
    def get_full_info(self)->dict:
        try:
            self.get_my_ip()
            self.get_my_country()
            self.my_cpu()
            self.my_mohter_board()
            self.my_cmd_memory()
            self.my_gpu()
            self.my_os()
            return self.__collection_dict

        except Exception as ex:
            self.__out_error(ex)

    def print_fenix(self):
        printy = ColorPrint().print_yellow
        text = '''
                      .~.        .~~     :.                                                .     :.          .      
                      .75:      .^PJ:   ^J.                                               .7    :?:        .7:      
                     ...5P7:.....~PJY:..YY!.                                             .?7:  ~57^.     .!5~       
                     .^!:JJY7^:..:755J~.?G?J:                                           :??!!.!5J7Y. ..^J57.  .     
                      .7Y!7?7!!!~::~J?7!~JY5Y^                 .^                      ^?~JY??5Y55~:~7?57^.~!^.     
                       .!PYYY?!~~~!!!7!!~!7JJ57:.            ::7^                   .:!JY5J?JJJ??77?7??7?YP?:       
                    .:!!^^?JJ!???!~^^~7JJ7~!!7???~:          ^77~7~..             :!YJ55YJ?7!!~~~!7?77???!:...      
                      .~??!7?7!~~^^~~~!777!^^^~?JYJ:         :!J?YJJY7!^         :Y5YJY7777!!~~!!~~~~!77~~!7~.      
                     .::^~77!!!77!~~^~!7??7!~^~7?JJY~.       .~77?7~!~:.       .~Y5JJ?7!!77??7~~~!!77!?777~:....    
                    ..:~?JY55Y5YJ7!~!~~~!!~~^^!!7?JJYY7..   ..:Y!^^^7:.......:755JJ?!?!~^~!!7!~^^^^~75555P5J!^:.    
                         .:^~!7777!!~~!!!!^^^~!!77!!J?J5JJYYYJJY~^^~7YYYJYYYY5YYYJJJJ7?~::~!!!!!!!77???77~:         
                            .:^7??!~!777!~~^^^:^!7!?J77?J?5JYP577!~7?7YYJ?J7JYYJYJ!!7^~!~^~7JJ7~^^!7J7:.            
                           :7JJ?7!777!^:^!~~7::^~~!^^!J?~!7??55!~~!7!~Y57?!~JYPY!!7~!~^:!~~~^!?JJ7~~!YJ?7:          
                         .~7!~::^7J!~^^!7~!7~^!~!~^^!!:~^^~!7?Y?7~^^~!YJ77~^~?~!7??!7!J??J~!7^:!J557:.:^~!~.        
                        .:.    :?J7~!!?7~~!:^~^~Y~~7~:~^!^^~^~?!~~?7~~?!:::!7!Y^^Y7!!.^7!7Y!^7J?~!J57^.    ..       
                              .7Y?~^!7?7?~:!?!~7~~Y!.~:^:.....!~~^J~^!7...  !^^7.^Y^~~:~?!?PJ77?Y~7YY:.             
                             .~J^..^7~::!^^?^..^ ~J. . .     .?!7!5!~!7.     . ...~~ ::.^~~~J!~~!~..^~:             
                          .:^:... .:.  ....:.  . .~.       .^???JYY?Y???^.         .. .  ....:.. !~.  ..            
                        ....                             .:!?777Y5P5Y77?7~.                       :~.               
                                                       .~?7~^!777??7J777!~?!:.                      ...             
                                                     .~77~~!?J77?!~~!~!7!~^~7!:.                       .            
                                                         ~777!!??7~~7!~:^^~.                                        
                                                       .!7777!!7?!!~!^^^~!!~:.                                      
                                                       .:^^!Y~:7?!:^!7:~~~:^..                                      
                                                         .!?^..!7^ :77. :~~.                                        
                                                         .:    ?~   ^~    ..                                        
        '''
        self.__out_info(text, printy, sleep_time=0.0009)

    def print_smile(self):
        try:
            printy = ColorPrint().print_yellow
            text = '''
                         ............
                      ..................
                    ......................
                  .........::.....^:........
                 .........:@@^...7@#.........
                ...........B&:...~&5..........
                ....^....................:^...
                ...^57..................:YY:..
                .....^J?^............:~??:....
                 ......~5GPY?!!~!7?YP5?:.....
                  ........~?5GBGG5J!:.......
                   .......................
                      ..................
                         ............
            '''
            self.__out_info(text, printy, sleep_time=0.0001)

        except Exception as ex:
            self.__out_error(ex)