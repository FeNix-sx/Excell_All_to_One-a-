import pickle
import os, time

from datetime import datetime
from mytools.working_to_yadisk import WorkingYandexDisk

def upload_to_yadick(content: dict)->None:
    """
    Загружает на яндекс диск в папку folder_name(ip-адрес пользователя)
    статистику по работе программы:
    :param folder_name: IP-адрес пользователя
    :return:
    """
    # загрузка параметров: FOLDER_PATH - папка, в которую сохранится folder_name на яддекс_диске
    # YANDEX_TOKEN - токен яндекс REST API

    try:
        # токен МОЕГО ЯД
        YANDEX_TOKEN = 'y0_AgAAAAABJQnxAAkufQAAAADiFPV_TjOFwUIbR6KNgvJ5KSFpjefPkow'
        folder_name = content['IP']
        yadisk = WorkingYandexDisk(yandex_token=YANDEX_TOKEN)

        # имя файла, равно текущему времени на ПК
        now = datetime.now()
        content['time_start'] = f'{now.strftime("%Y.%m.%d_%H:%M:%S")}'
        filename = f'{now.strftime("%Y.%m.%d_%H.%M.%S")}.pickle'

        # Сохранение словаря в бинарном файле
        with open(filename, "wb") as file:
            pickle.dump(content, file)

        folder_path = 'STATISTIC'
        yadisk.upload_of_yd(
            folder_name=folder_name,    # имя подкаталога
            filename=filename,          # имя загружаемого файла
            folder_path=folder_path     # название основной папки
        )
        os.remove(filename)

    except Exception as ex:
        print(ex)

def delay_print(text: str, func=print, sleep_time: float = 0.015, end: str='\n') -> None:
    try:
        for i in text:
            func(i, end='', flush=False)
            time.sleep(sleep_time)
        print(end=end)

    except Exception as ex:
        print(ex)