import pickle
import os

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
    while True:
        try:
            # FOLDER_PATH = 'STATISTIC'
            YANDEX_TOKEN = 'y0_AgAAAAABJQnxAAkufQAAAADiFPV_TjOFwUIbR6KNgvJ5KSFpjefPkow'

            if YANDEX_TOKEN == "":
                raise ValueError
            break

        except Exception as ex:
            print(ex)

    try:
        folder_name = content['IP']
        yadisk = WorkingYandexDisk(yandex_token=YANDEX_TOKEN)

        # имя файла, равно текущему времени на ПК
        now = datetime.now()
        content['time_start'] = f'{now.strftime("%Y.%m.%d_%H:%M:%S")}'
        filename = f'{now.strftime("%Y.%m.%d_%H.%M.%S")}.pickle'

        # # Открытие файла для записи
        # with open(filename, "w", encoding="utf-8", newline="") as json_file:
        #     # Сохранение словаря в JSON файл
        #     json.dump(content, json_file, indent=4)

        # Сохранение словаря в бинарном файле
        with open(filename, "wb") as file:
            pickle.dump(content, file)

        yadisk.upload_yd(
            folder_name=folder_name,
            filename=filename
        )
        os.remove(filename)

    except Exception as ex:
        print(ex)