import os
import time
import pandas as pd
import numpy as np

from mytools.tool_class import NamesPhone

def get_files_names() -> list:
    """
    Получение списка файлов из папки Excel_Files
    :return: list
    """
    try:
        folder_path = 'Excel_Files'
        file_list = os.listdir(folder_path)
        xlsx_files = [file for file in file_list if file.endswith('.xlsx')]
        return xlsx_files
    except Exception as ex:
        print(f"Ошибка! {ex}")

def load_dataframe():
    try:
        phones_names = NamesPhone()
        namefile = "Excel_Files/0.xlsx"
        df_full = pd.read_excel(
                namefile)
        print(df_full.columns.tolist())

        df_full = df_full[[
            "Артикул поставщика",
            "Название",
            "Обоснование для оплаты",
            "Кол-во",
            "Цена розничная с учетом согласованной скидки",
            "К перечислению Продавцу за реализованный Товар",
            "Услуги по доставке товара покупателю",
            "Общая сумма штрафов"
        ]]
        df_full.insert(loc=1, column="Телефон", value="")
        df_full["Телефон"] = phones_names.get_names(df_full["Артикул поставщика"].str[:6:])
        print(df_full.columns.tolist())
        print(df_full[["Телефон", "Артикул поставщика", "Название"]].head(30))

    except Exception as ex:
        print(f"Ошибка! {ex}")

def main():
    # list_file_xlsx = get_files_names()
    load_dataframe()


if __name__ == '__main__':
    main()