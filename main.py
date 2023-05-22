import os
import time
import pandas as pd
import numpy as np

from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime
from pandas import DataFrame
from mytools.tool_class import NamesPhone, ColorInput, ColorPrint



printer = ColorPrint().print_error
printinf = ColorPrint().print_info
printw = ColorPrint().print_warning
printw("version 1.1")

change_series = NamesPhone()
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
        df_source["телефон"] = change_series.get_names_phone(df_source["Артикул поставщика"].str[:6:])
        df_source["Название"] = change_series.get_name_print(df_source["Название"])

        df_source = df_source.rename(columns={
            "Артикул поставщика": "артикул",
            "Дата продажи": "дата",
            "Название": "название",
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
            printinf(f"файл {file} загружен")
        print()

        data_begin = df_full["дата"].min()
        data_end = df_full["дата"].max()

        printw(f"Задайте интересующий временной интервал для выборки данных",
               f"нижняя граница: {data_begin.strftime('%d.%m.%Y')}",
               f"верхняя граница: {data_end.strftime('%d.%m.%Y')}",
               sep="\n")

        inputdata = ColorInput([data_begin, data_end]).cinput_date

        inp_begin = datetime.strptime(inputdata(" c ->: "), '%d.%m.%Y')
        inp_end = datetime.strptime(inputdata("по ->: "), '%d.%m.%Y')
        print()

        printinf(f"Выбран диапазон дат: {inp_begin.strftime('%d.%m.%Y')} - {inp_end.strftime('%d.%m.%Y')}")

        df_full = df_full[
            (df_full["обоснование"].isin(FILTER_RES))&
            (df_full["дата"] >= inp_begin)&
            (df_full["дата"] <= inp_end)
        ]

        GROUP_LIST = [
                'артикул',
                'телефон',
                'название'
                # "обоснование"
            ]

        result_file_name = f"RESULT.xlsx"

        # создаем файл result_file_name
        with pd.ExcelWriter(result_file_name, engine='xlsxwriter') as writer:
            for group in GROUP_LIST:
                df_result = df_full.groupby(  # группировка DataFrame по параметру списка group
                    [group],
                    as_index=False
                ).aggregate(  # агрегирование столбцов
                    {
                        'Кол-во': "sum",
                        'к перечислению': "sum",
                        'налог': "sum",
                        'доставка': "sum",
                        'штрафы': "sum"
                    }
                )
                # добавляем строку в конец таблицы
                df_result.loc[len(df_result.index)] = [
                    '### И Т О Г О ###',
                    df_result['Кол-во'].astype(float).sum(),
                    df_result['к перечислению'].astype(float).sum(),
                    df_result['налог'].astype(float).sum(),
                    df_result['доставка'].astype(float).sum(),
                    df_result['штрафы'].astype(float).sum()
                ]
                # создаем лист group в файле result_file_name и записываем туда df_result
                df_result.to_excel(
                    writer,
                    sheet_name=f"{group}",
                    index=True,
                    index_label="№ п/п",
                    startrow=1
                )

                # получаем объект workbook и worksheet нужного листа
                workbook = writer.book
                worksheet = writer.sheets[f"{group}"]

                for i, col in enumerate(df_result):
                    max_width = max(df_result[col].astype(str).map(len).max(), len(col))
                    worksheet.set_column(i+1, i+1, max_width + 1)

                last_row = len(df_result) + 1
                bold_format = workbook.add_format({'bold': True})
                worksheet.set_row(last_row, None, bold_format)

                del df_result

        printinf(f"Файл {result_file_name} создан.")
        printinf("Программа успешно завершена")
        time.sleep(3)

    except Exception as ex:
        print(f"Ошибка! {ex}")

def create_excel_tables(df: DataFrame=None, wb: Workbook=None):
    # создаем лист и заголовки
    worksheet = wb.create_sheet(title='shit1')
    headers = df.columns.values.tolist()
    worksheet.append(headers)
    pass



def main():
    printw("Программа собирает информацию из ВСЕХ *.xlsx файлов,\nнаходящихся в папке 'Excel_Files'")
    time.sleep(2)
    list_file_xlsx = get_files_names()
    merge_data(list_file_xlsx)


if __name__ == '__main__':
    main()