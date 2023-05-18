import os
import time
import pandas as pd
import numpy as np

from pandas import DataFrame
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

def load_dataframe(filename: str=None) -> DataFrame:
    try:
        change_series = NamesPhone()
        filename = f"Excel_Files/{filename}"
        df_source = pd.read_excel(filename)

        df_source = df_source[[
            "Артикул поставщика",
            "Название",
            # "Дата продажи",
            "Обоснование для оплаты",
            "Кол-во",
            "Цена розничная с учетом согласованной скидки",
            "К перечислению Продавцу за реализованный Товар",
            "Услуги по доставке товара покупателю",
            "Общая сумма штрафов"
        ]]

        df_source.insert(loc=1, column="Телефон", value="")
        df_source["Телефон"] = change_series.get_names_phone(df_source["Артикул поставщика"].str[:6:])
        df_source["Название"] = change_series.get_name_print(df_source["Название"])

        df_source = df_source.rename(columns={
            "Артикул поставщика": "артикул",
            # "Дата продажи": "дата",
            "Обоснование для оплаты": "обоснование",
            "Цена розничная с учетом согласованной скидки": "цена со скидкой",
            "К перечислению Продавцу за реализованный Товар": "к перечислению",
            "Услуги по доставке товара покупателю": "доставка",
            "Общая сумма штрафов": "штрафы"
        })
        print(df_source[["Телефон", "Название"]].tail(30))

        return df_source

    except Exception as ex:
        print(f"Ошибка! {ex}")

def merge_data(list_file_xlsx: list=None) -> None:
    try:
        df_full = DataFrame()

        for file in list_file_xlsx:
            df_full = pd.concat([df_full, load_dataframe(file)], ignore_index=True)

        df_full = df_full[df_full["обоснование"]=="Возврат"]
        df_result = df_full.groupby(  # группировка DataFrame по 3-м параметрам (столбикам)
            ['артикул', 'Телефон', 'Название', "обоснование"],
            as_index=False
        ).aggregate(  # агрегирование столбца Количество
            {
                'Кол-во': "sum",
                'цена со скидкой': "sum",
                'к перечислению': "sum",
                'доставка': "sum",
                'штрафы': "sum"
            }
        )

        print(df_result.columns.tolist())
        print(df_result.tail())

        df_result.to_excel("RESULT_возврат.xlsx", sheet_name="ИТОГ")

    except Exception as ex:
        print(f"Ошибка! {ex}")


def main():
    list_file_xlsx = get_files_names()
    merge_data(list_file_xlsx)


if __name__ == '__main__':
    main()