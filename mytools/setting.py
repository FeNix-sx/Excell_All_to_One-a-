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

            self.purchase_amount = self.__purchase_amount
            self.models = self.__models
            self.token = self.__token
            self.only = self.__only
            self.folder_sett = self.__folder_sett

        except Exception as ex:
            print(ex)

    @property
    def __purchase_amount(self):
        try:
            PURCHASE_AMOUNT = os.getenv('PURCHASE_AMOUNT')
            return float(PURCHASE_AMOUNT)

        except Exception as ex:
            print(ex)

    @property
    def __folder_sett(self)->str:
        try:
            FOLDER_SETT = os.getenv('FOLDER_SETT')
            return FOLDER_SETT

        except Exception as ex:
            print(ex)

    @property
    def __token(self)->str:
        try:
            YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')
            return YANDEX_TOKEN

        except Exception as ex:
            print(ex)

    @property
    def __models(self) -> str:
        try:
            FILE_NAME = os.getenv('MODELS_FILE')
            return FILE_NAME

        except Exception as ex:
            print(ex)

    @property
    def __only(self) -> str:
        try:
            ONLY = os.getenv('ONLY')
            if ONLY not in ("phones", "stickers"):
                raise ValueError(f'Значение ONLY в файле "setting.env" должно быть "phones или "stickers"')
            return ONLY

        except Exception as ex:
            print(ex)

setting = Setting()