import time

import requests
import json
import os

from yadisk import YaDisk
from datetime import datetime
from mytools.tool_class import ColorPrint

printer = ColorPrint().print_error
printinf = ColorPrint().print_info
printw = ColorPrint().print_warning

def upload_to_yadick(folder_name: str, content: dict):
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
        printinf('успешно!')

    except Exception as ex:
        printer(ex)


def my_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json()['ip']
        printinf('успешно!')
        return ip

    except Exception as ex:
        printer(ex)

def find_country(ip_address):
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

def main_func():
    printw("version 1.0 (01.09.2023)")
    printw("Программа для сбора информации об интернет соединении")

    printinf('Проверка подключения: ', end='')
    ip = my_ip()

    printinf('Сбор телеметрии: ', end='')
    content = find_country(ip)
    upload_to_yadick(ip, content)

    printinf('Благодарю за использование программы!')
    printw('Каждый запуск помогает мне в обучении')
    printinf('(｡◕‿◕｡)')
    time.sleep(2)


if __name__ == '__main__':
    main_func()
