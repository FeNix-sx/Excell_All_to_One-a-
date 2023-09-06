import time
import os
import pickle

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from mytools import ColorPrint
from mytools import StatisticCollection
from mytools import WorkingYandexDisk
from mytools import delay_print

printer = ColorPrint().print_error
printinf = ColorPrint().print_info
printw = ColorPrint().print_warning
printy = ColorPrint().print_yellow
statistic = StatisticCollection()

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

        # Сохранение словаря в бинарном файле
        with open(filename, "wb") as file:
            pickle.dump(content, file)

        yadisk.upload_of_yd(
            folder_name=folder_name,
            filename=filename
        )
        os.remove(filename)

    except Exception as ex:
        printer(ex)


def main_func()->None:
    content = statistic.get_full_info
    upload_to_yadick(content)


def main_multiprocessing():
    text = [
        "version 1.2.3 (06.09.2023)",
        "Программа собирает информацию об интернет соединении",
        "Благодарю за использование программы!"
    ]
    for item in text:
        delay_print(
            text=item,
            func=printw,
            sleep_time= 0.015
        )
    # Создаем экземпляр ThreadPoolExecutor с двумя потоками
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Запускаем функции statistic.draw и main_func в фоновом режиме
        future1 = executor.submit(statistic.draw)
        future2 = executor.submit(main_func)

        # Ожидаем завершение обоих функций
        future1.result()
        future2.result()


if __name__ == '__main__':
    main_multiprocessing()
    delay_print(
        text='Каждый запуск помогает мне в обучении',
        func=printw,
        sleep_time=0.015
    )
    statistic.print_smile()
    time.sleep(3)