import os
import time
import pandas as pd
import numpy as np

from datetime import datetime
from pandas import DataFrame
from mytools.tool_class import NamesPhone, ColorInput, ColorPrint

change_series = NamesPhone()
printer = ColorPrint().print_error
printinf = ColorPrint().print_info
printw = ColorPrint().print_warning

FILTER_RES = ["Продажа", "Логистика", "Возврат"]

def get_files_names() -> list:
    """
    Получение списка файлов из папки Excel_Files
    :return: list
    """
    try:
        folder_path = 'Excel_Files'
        file_list = os.listdir(folder_path)
        xlsx_files = [file for file in file_list if file.endswith('.xlsx')]

        printinf("Обнаружены файлы:\n", *xlsx_files)
        return xlsx_files

    except Exception as ex:
        print(f"Ошибка! {ex}")

def load_dataframe(filename: str=None) -> DataFrame:
    try:
        # change_series = NamesPhone()
        filename = f"Excel_Files/{filename}"
        df_source = pd.read_excel(filename)

        df_source = df_source[[
            "Артикул поставщика",
            "Название",
            "Дата продажи",
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
            "Дата продажи": "дата",
            "Обоснование для оплаты": "обоснование",
            "Цена розничная с учетом согласованной скидки": "налог",
            "К перечислению Продавцу за реализованный Товар": "к перечислению",
            "Услуги по доставке товара покупателю": "доставка",
            "Общая сумма штрафов": "штрафы"
        })

        df_source["налог"] = df_source["налог"] * 0.07
        df_source["дата"] = pd.to_datetime(df_source["дата"])

        return df_source

    except Exception as ex:
        print(f"Ошибка! {ex}")

def merge_data(list_file_xlsx: list=None) -> None:
    try:
        df_full = DataFrame()

        for file in list_file_xlsx:
            df_full = pd.concat([df_full, load_dataframe(file)], ignore_index=True)
            printinf(f"Файл {file} загружен")

        data_begin = df_full["дата"].min()
        data_end = df_full["дата"].max()

        printw(f"Задайте интересующий временной интервал",
               f"нижняя граница: {data_begin.strftime('%d.%m.%Y')}",
               f"верхняя граница: {data_end.strftime('%d.%m.%Y')}",
               sep="\n")

        inputdata = ColorInput([data_begin, data_end]).cinput_date
        inputindex = ColorInput([1, 3]).cinput_int

        inp_begin = datetime.strptime(inputdata(" c ->: "), '%d.%m.%Y')
        inp_end = datetime.strptime(inputdata("по ->: "), '%d.%m.%Y')

        # data_begin = datetime.strptime("01.04.2023", '%d.%m.%Y')
        # data_end = datetime.strptime("23.04.2023", '%d.%m.%Y')

        printinf(f"Выбран диапазон дат: {data_begin.strftime('%d.%m.%Y')} - {data_end.strftime('%d.%m.%Y')}")

        df_full = df_full[
            (df_full["обоснование"].isin(FILTER_RES))&
            (df_full["дата"] >= inp_begin)&
            (df_full["дата"] <= inp_end)
        ]

        printw(f"Выбирете один из показателей для расчетов:",
               f"1 - артикул, 2 - название телефона, 3 - Название принта",
               sep="\n")
        index = inputindex("--->: ")

        GROUP_LIST = [
                'артикул',
                'Телефон',
                'Название',
                "обоснование"
            ][index-1:index]

        df_result = df_full.groupby(  # группировка DataFrame по 3-м параметрам (столбикам)
            GROUP_LIST,
            as_index=False
        ).aggregate(  # агрегирование столбца Количество
            {
                'Кол-во': "sum",
                'к перечислению': "sum",
                'налог': "sum",
                'доставка': "sum",
                'штрафы': "sum"
            }
        )

        begin = f"{inp_begin.strftime('%d%m%Y')}"
        end = f"{inp_end.strftime('%d%m%Y')}"

        filter_name = "_".join(GROUP_LIST)
        result_file_name = f"RESULT_{filter_name}.xlsx"
        df_result.to_excel(
            result_file_name,
            sheet_name=f"{begin}-{end}",
            index=True,
            index_label="№ п/п",
            startrow=1
        )
        printw(f"файл {result_file_name} создан.")
        printinf("Программа успешно завершена")
        time.sleep(3)

    except Exception as ex:
        print(f"Ошибка! {ex}")


def main():
    list_file_xlsx = get_files_names()
    print()
    merge_data(list_file_xlsx)


if __name__ == '__main__':
    main()