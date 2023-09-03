from yadisk import YaDisk


class WorkingYandexDisk:
    def __init__(self, yandex_token):
        try:
            self.yadisk = YaDisk(token=yandex_token)

            if self.yadisk.check_token():
                # print("Connection to YD")
                pass
            else:
                # print(f"Ошибка!\nНе удалось подключиться к яндекс-диску.")
                raise ConnectionError

        except Exception as ex:
            print(ex, f"Ошибка!\nНе удалось подключиться к яндекс-диску.")

    def download_yd(self, folder_name: str='SETTINGS', filename: str='models.xlsx')->bool:
        if folder_name:
            path = f'/{folder_name}/{filename}'
        else:
            path = f'/{filename}'

        try:
            self.yadisk.download(path, filename)
            return True
        except Exception as ex:
            print(ex)

    def upload_yd(self, folder_name: str,filename: str)->bool:
        try:
            FOLDER_PATH = 'STATISTIC'
            path_name = ""
            # создаем папку на яндекс-диске, если ее там нет
            if FOLDER_PATH != "":
                if not self.yadisk.is_dir(f"{FOLDER_PATH}"):
                    self.yadisk.mkdir(f"{FOLDER_PATH}")
                else:
                    if not self.yadisk.is_dir(f"{FOLDER_PATH}/{folder_name}/"):
                        self.yadisk.mkdir(f"{FOLDER_PATH}/{folder_name}/")

                path_name = f"{FOLDER_PATH}/{folder_name}/"
            else:
                if not self.yadisk.is_dir(f"{folder_name}/"):
                    self.yadisk.mkdir(f"{folder_name}/")
                    path_name = f"{folder_name}/"

            self.yadisk.upload(filename, path_name + filename, overwrite=True)

        except Exception as ex:
            print(ex)