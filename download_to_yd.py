import time

import requests
import json
import os
import subprocess

from yadisk import YaDisk
from datetime import datetime
from multiprocessing import Process
from mytools.tool_class import ColorPrint, StatisticColection

printer = ColorPrint().print_error
printinf = ColorPrint().print_info
printw = ColorPrint().print_warning
printy = ColorPrint().print_yellow
statistic = StatisticColection()

def out_info(text: str, func=print, sleep_time: float=0.025)->None:
    for i in text:
        func(i, end='', flush=True)
        time.sleep(sleep_time)
    print()

def my_cpu(content: dict)->None:
    # Получить модель процессора
    cmd_cpu = "wmic cpu get name"
    result_cpu = [
        item.strip() for item in subprocess.run(cmd_cpu, capture_output=True, text=True).stdout.split('\n') if item
    ]
    content['CPU'] = ', '.join(result_cpu)
    printinf("Процессор: ", end='')
    out_info(', '.join(result_cpu), printw)

def my_mohter_board(content: dict)->None:
    # Получить модель материнской платы
    cmd_motherboard = "wmic baseboard get product"
    result_motherboard = [
        item.strip() for item in subprocess.run(cmd_motherboard, capture_output=True, text=True).stdout.split('\n') if item
    ]
    content['MB'] = ', '.join(result_motherboard)
    printinf("Материнская плата: ", end='')
    out_info(', '.join(result_motherboard), printw)

def my_gpu(content: dict)->None:
    # Получить информацию о видеокарте
    cmd_gpu = "wmic path win32_videocontroller get name"
    result_gpu = [
        item.strip() for item in subprocess.run(cmd_gpu, capture_output=True, text=True).stdout.split('\n') if item
    ]
    content['GPU'] = ', '.join(result_gpu)
    printinf("Видеокарта: ", end='')
    out_info(', '.join(result_gpu), printw)

def my_cmd_memory(content: dict)->None:
    # Получить информацию об оперативной памяти
    cmd_memory = "wmic memorychip get capacity"
    result_memory = subprocess.run(cmd_memory, capture_output=True, text=True).stdout.strip().split('\n')

    memory_modules = [
        str(int(memory.strip())/(1024**3))+ ' GB' for memory in result_memory if memory.strip().isdigit()
    ]
    content['Memory'] = ', '.join(memory_modules)
    printinf(f"Оперативная память (ГБ): ", end='')
    out_info(', '.join(memory_modules), printw)

def my_os(content: dict)->None:
    # Получить установленную версию операционной системы
    cmd_os_version = "wmic os get caption"
    result_os_version = [
        item.encode('cp1251').decode('cp1251') for item in subprocess.run(cmd_os_version, capture_output=True, text=True).stdout.split()
    ]
    content['OS version'] = ' '.join(result_os_version)
    printinf("Версия операционной системы: ", end='')
    out_info(' '.join(result_os_version), printw)

def upload_to_yadick(content: dict)->None:
    """
    Загружает на яндекс диск в папку folder_name(ip-адрес пользователя)
    статистику по работе программы:
    :param folder_name: IP-адрес пользователя
    :return:
    """
    # загрузка параметров: FOLDER_PATH - папка, в которую сохранится folder_name на яддекс_диске
    # YANDEX_TOKEN - токен яндекс REST API
    while True:
        try:
            FOLDER_PATH = 'STATISTIC'
            YANDEX_TOKEN = 'y0_AgAAAAABJQnxAAkufQAAAADiFPV_TjOFwUIbR6KNgvJ5KSFpjefPkow'

            if YANDEX_TOKEN == "":
                raise ValueError
            break

        except Exception as ex:
            print(ex)

    try:
        folder_name = content['IP']
        yadisk = YaDisk(token=YANDEX_TOKEN)

        # if not yadisk.check_token():
        #     print("Неверный токен доступа")
        #     exit()

        if yadisk.check_token():
            # print("Connection to YD")
            pass
        else:
            # print(f"Ошибка!\nНе удалось подключиться к яндекс-диску.")
            return

        path_name = ""
        # создаем папку на яндекс-диске, если ее там нет
        if FOLDER_PATH != "":
            if not yadisk.is_dir(f"{FOLDER_PATH}"):
                yadisk.mkdir(f"{FOLDER_PATH}")
            else:
                if not yadisk.is_dir(f"{FOLDER_PATH}/{folder_name}/"):
                    yadisk.mkdir(f"{FOLDER_PATH}/{folder_name}/")

            path_name = f"{FOLDER_PATH}/{folder_name}/"
        else:
            if not yadisk.is_dir(f"{folder_name}/"):
                yadisk.mkdir(f"{folder_name}/")
                path_name = f"{folder_name}/"

    except Exception as ex:
        printer(ex)
        return

    try:
        # имя файла, равно текущему времени на ПК
        now = datetime.now()
        content['time_start'] = f'{now.strftime("%Y.%m.%d_%H:%M:%S")}'
        filename = f'{now.strftime("%Y.%m.%d_%H.%M.%S")}.json'
        destination_path = f"{path_name + filename}"

        # Открытие файла для записи
        with open(filename, "w", encoding="utf-8", newline="") as json_file:
            # Сохранение словаря в JSON файл
            json.dump(content, json_file, indent=4)

        yadisk.upload(filename, destination_path, overwrite=True)
        os.remove(filename)

    except Exception as ex:
        printer(ex)

def my_ip()->str:
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json()['ip']
        printinf('успешно!')
        return ip

    except Exception as ex:
        printer(ex)

def find_country(ip_address)->dict:
    try:
        url = f'http://ip-api.com/json/{ip_address}'
        response = requests.get(url).json()

        information = {
            'IP': response.get('query'),
            'Prov': response.get('isp'),
            'Org': response.get('org'),
            'Country': response.get('country'),
            'regionName': response.get('regionName'),
            'lat': response.get('lat'),
            'lon': response.get('lon')
        }
        # for k, v in information.items():
        #     print(f'{k}: {v}')
        return information

    except Exception as ex:
        print(ex)

def main_func()->None:
    printw("version 1.1 (01.09.2023)")
    printw("Программа для сбора информации об интернет соединении")
    content = statistic.get_full_info
    # printinf('Проверка подключения: ', end='')
    # ip = my_ip()
    #
    # printinf('Сбор телеметрии: ', end='')
    # content = find_country(ip)
    # printinf('успешно!')
    # my_cpu(content)
    # my_mohter_board(content)
    # my_gpu(content)
    # my_cmd_memory(content)
    # my_os(content)
    upload_to_yadick(content)
    #
    printinf('Благодарю за использование программы!')
    statistic.print_fenix()
    # out_info('''
    #       .~.        .~~     :.                                                .     :.          .
    #       .75:      .^PJ:   ^J.                                               .7    :?:        .7:
    #      ...5P7:.....~PJY:..YY!.                                             .?7:  ~57^.     .!5~
    #      .^!:JJY7^:..:755J~.?G?J:                                           :??!!.!5J7Y. ..^J57.  .
    #       .7Y!7?7!!!~::~J?7!~JY5Y^                 .^                      ^?~JY??5Y55~:~7?57^.~!^.
    #        .!PYYY?!~~~!!!7!!~!7JJ57:.            ::7^                   .:!JY5J?JJJ??77?7??7?YP?:
    #     .:!!^^?JJ!???!~^^~7JJ7~!!7???~:          ^77~7~..             :!YJ55YJ?7!!~~~!7?77???!:...
    #       .~??!7?7!~~^^~~~!777!^^^~?JYJ:         :!J?YJJY7!^         :Y5YJY7777!!~~!!~~~~!77~~!7~.
    #      .::^~77!!!77!~~^~!7??7!~^~7?JJY~.       .~77?7~!~:.       .~Y5JJ?7!!77??7~~~!!77!?777~:....
    #     ..:~?JY55Y5YJ7!~!~~~!!~~^^!!7?JJYY7..   ..:Y!^^^7:.......:755JJ?!?!~^~!!7!~^^^^~75555P5J!^:.
    #          .:^~!7777!!~~!!!!^^^~!!77!!J?J5JJYYYJJY~^^~7YYYJYYYY5YYYJJJJ7?~::~!!!!!!!77???77~:
    #             .:^7??!~!777!~~^^^:^!7!?J77?J?5JYP577!~7?7YYJ?J7JYYJYJ!!7^~!~^~7JJ7~^^!7J7:.
    #            :7JJ?7!777!^:^!~~7::^~~!^^!J?~!7??55!~~!7!~Y57?!~JYPY!!7~!~^:!~~~^!?JJ7~~!YJ?7:
    #          .~7!~::^7J!~^^!7~!7~^!~!~^^!!:~^^~!7?Y?7~^^~!YJ77~^~?~!7??!7!J??J~!7^:!J557:.:^~!~.
    #         .:.    :?J7~!!?7~~!:^~^~Y~~7~:~^!^^~^~?!~~?7~~?!:::!7!Y^^Y7!!.^7!7Y!^7J?~!J57^.    ..
    #               .7Y?~^!7?7?~:!?!~7~~Y!.~:^:.....!~~^J~^!7...  !^^7.^Y^~~:~?!?PJ77?Y~7YY:.
    #              .~J^..^7~::!^^?^..^ ~J. . .     .?!7!5!~!7.     . ...~~ ::.^~~~J!~~!~..^~:
    #           .:^:... .:.  ....:.  . .~.       .^???JYY?Y???^.         .. .  ....:.. !~.  ..
    #         ....                             .:!?777Y5P5Y77?7~.                       :~.
    #                                        .~?7~^!777??7J777!~?!:.                      ...
    #                                      .~77~~!?J77?!~~!~!7!~^~7!:.                       .
    #                                          ~777!!??7~~7!~:^^~.
    #                                        .!7777!!7?!!~!^^^~!!~:.
    #                                        .:^^!Y~:7?!:^!7:~~~:^..
    #                                          .!?^..!7^ :77. :~~.
    #                                          .:    ?~   ^~    ..
    # ''', printy,sleep_time=0.001)
    printw('Каждый запуск помогает мне в обучении')
    statistic.print_smile()
    # out_info('''
    #
    #              ............
    #           ..................
    #         ......................
    #       .........::.....^:........
    #      .........:@@^...7@#.........
    #     ...........B&:...~&5..........
    #     ....^....................:^...
    #     ...^57..................:YY:..
    #     .....^J?^............:~??:....
    #      ......~5GPY?!!~!7?YP5?:.....
    #       ........~?5GBGG5J!:.......
    #        .......................
    #           ..................
    #              ............
    # ''', printy, sleep_time=0.0001)
    time.sleep(2)


if __name__ == '__main__':
    main_func()