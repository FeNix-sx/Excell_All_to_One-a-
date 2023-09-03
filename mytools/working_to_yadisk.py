from yadisk import YaDisk


class WorkingYandexDisk:
    def __init__(self, yandex_token):
        try:
            self.token = yandex_token
            if self.token == "":
                raise ValueError

            self.__my_disk = YaDisk(self.token)

            if self.__my_disk.check_token():
                # print("Connection to YD")
                pass
            else:
                # print(f"Ошибка!\nНе удалось подключиться к яндекс-диску.")
                raise ConnectionError

        except Exception as ex:
            print(ex, f"Ошибка!\nНе удалось подключиться к яндекс-диску.")

    def download(self, folder_name: str='SETTINGS', filename: str= 'models.xlsx')->bool:
        if folder_name:
            path = f'/{folder_name}/{filename}'
        else:
            path = f'/{filename}'

        try:
            self.__my_disk.download(path, filename)
            return True
        except Exception as ex:
            print(ex)

    def upload(self, folder_name: str='TEST',filename: str=None)->bool:
        try:
            FOLDER_PATH = 'STATISTIC'
            path_name = ""
            # создаем папку на яндекс-диске, если ее там нет
            if FOLDER_PATH != "":
                if not self.__my_disk.is_dir(f"{FOLDER_PATH}"):
                    self.__my_disk.mkdir(f"{FOLDER_PATH}")
                else:
                    if not self.__my_disk.is_dir(f"{FOLDER_PATH}/{folder_name}/"):
                        self.__my_disk.mkdir(f"{FOLDER_PATH}/{folder_name}/")

                path_name = f"{FOLDER_PATH}/{folder_name}/"
            else:
                if not self.__my_disk.is_dir(f"{folder_name}/"):
                    self.__my_disk.mkdir(f"{folder_name}/")
                    path_name = f"{folder_name}/"

            self.__my_disk.upload(filename, path_name+filename, overwrite=True)

        except Exception as ex:
            print(ex)