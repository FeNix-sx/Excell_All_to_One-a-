import os

from dotenv import load_dotenv

class Setting:
    def __init__(self):
        try:
            dotenv_path = 'setting.env'

            if not os.path.isfile(dotenv_path):
                raise (f"Файл {dotenv_path} не найден!.")

            if os.path.exists(dotenv_path):
                load_dotenv(dotenv_path)

        except Exception as ex:
            print(ex)

    @property
    def folder_sett(self)->str:
        try:
            FOLDER_SETT = os.getenv('FOLDER_SETT')
            return FOLDER_SETT

        except Exception as ex:
            print(ex)

    @property
    def token(self)->str:
        try:
            YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')
            return YANDEX_TOKEN

        except Exception as ex:
            print(ex)

    @property
    def models(self) -> str:
        try:
            FILE_NAME = os.getenv('MODELS_FILE')
            return FILE_NAME

        except Exception as ex:
            print(ex)


setting = Setting()