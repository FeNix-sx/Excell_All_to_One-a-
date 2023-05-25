import os
import time
import pandas as pd

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
        while True:
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                break
            else:
                printer("Папка Excel_Files не существует")
                printinf("Создайте Excel_Files, поместите в нее файлы *.xlsx")

                if input("Перезапустить программу?(y/n): ") in ("y", "да"):
                    continue
                else:
                    return None

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
            "Вайлдберриз реализовал Товар (Пр)",
            "Обоснование для оплаты",
            "Кол-во",
            "К перечислению Продавцу за реализованный Товар",
            "Услуги по доставке товара покупателю",
            "Общая сумма штрафов"
        ]]

        df_source.insert(loc=1, column="Телефон", value="")
        df_source["телефон"] = change_series.get_names_phone(df_source["Артикул поставщика"].str[:6:])
        df_source["Название"] = df_source["Артикул поставщика"].str[-3:]
        df_source["код телефона"] = df_source["Артикул поставщика"].str[:6]

        df_source = df_source.rename(columns={
            "Артикул поставщика": "артикул",
            "Дата продажи": "дата",
            "Название": "код принта",
            "Обоснование для оплаты": "обоснование",
            "Вайлдберриз реализовал Товар (Пр)": "налог",
            "К перечислению Продавцу за реализованный Товар": "к перечислению",
            "Услуги по доставке товара покупателю": "логистика_затраты",
            "Общая сумма штрафов": "штрафы_затраты",
            "код телефона": "код"
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
        # заменяем текстовое поле обоснование на поля с int
        df_dummies = pd.get_dummies(df_full["обоснование"], dtype=int)

        df_full = pd.concat([df_full, df_dummies], axis=1)
        del df_dummies

        # налог и прибыль не учитывается когда был возврат
        df_full.loc[df_full['Возврат'] == 1, 'налог'] *= 0
        df_full.loc[df_full['Возврат'] == 1, 'к перечислению'] *= 0

        df_full = df_full[
            (df_full["дата"] >= inp_begin)&
            (df_full["дата"] <= inp_end)
        ]
        # удалаем поле ["дата", "обоснование"]
        df_full.drop(["дата", "обоснование", "Телефон"], axis=1, inplace=True)
        # создаем поле с чистой прибылью
        df_full.insert(
            loc=3,
            column="чистая прибыль",
            value=df_full["к перечислению"] -
                  df_full["налог"] -
                  df_full["логистика_затраты"] -
                  df_full["штрафы_затраты"] -
                  df_full["Логистика"] * 157
        )
        # меняем местами столбцы
        df_full = df_full[
            [
                'артикул', 'код принта', 'Кол-во', 'чистая прибыль', 'к перечислению',
                'налог', 'логистика_затраты', 'штрафы_затраты', 'телефон',
                'код', 'Возврат', 'Логистика', 'Продажа', 'Штрафы'
            ]
        ]
        return df_full

    except Exception as ex:
        print(f"Ошибка! {ex}")


def write_to_excel(df_full: DataFrame=None) -> None:
    try:
        GROUP_LIST = [
                'артикул',
                'телефон',
                'код принта',
                'код'
            ]

        result_file_name = f"RESULT.xlsx"
        # создаем файл result_file_name
        with pd.ExcelWriter(result_file_name, engine='xlsxwriter') as writer:
            for group in GROUP_LIST:
                # задаем список полей для агрегации
                agg_list = [item for item in df_full.columns if item not in GROUP_LIST]
                agg_dict = {item:"sum" for item in agg_list}
                df_result = df_full.groupby(  # группировка DataFrame по параметру списка group
                    [group],
                    as_index=False
                ).aggregate(  # агрегирование столбцов
                    agg_dict
                )
                # сортировка
                df_result = df_result.sort_values('Кол-во', ascending=False)

                # создаем список столбцов для агрегации (суммирования в данном случае)
                colum_list = [
                    df_result[item].astype(float).sum() for item in agg_list
                ]
                # добавляем строку в конец таблицы
                df_result.loc[len(df_result.index)] = [
                    '### И Т О Г О ###',
                    *colum_list
                ]
                df_result.insert(loc=0, column='№ п/п', value=range(1, len(df_result) + 1))
                # создаем лист group в файле result_file_name и записываем туда df_result
                df_result.to_excel(
                    writer,
                    sheet_name=f"{group}",
                    index=False,
                    startrow=0
                )
                # получаем объект workbook и worksheet нужного листа
                workbook = writer.book
                worksheet = writer.sheets[f"{group}"]

                # задаем ширину столбцов
                for i, col in enumerate(df_result):
                    max_width = max(df_result[col].astype(str).map(len).max(), len(col))
                    worksheet.set_column(i, i, max_width + 2)

                # задаем стиль для заголовка таблицы
                header_style = workbook.add_format({
                    'bg_color': 'black', 'font_color': 'white',
                    'bold': True, 'align': 'center'
                })

                # Задаем заголовок таблицы
                for i, header in enumerate(df_result.columns):
                    worksheet.write(0, i, header, header_style)

                last_row = len(df_result)
                bold_format = workbook.add_format({
                    'bold': True, 'font_color': 'red'
                })
                worksheet.set_row(last_row, None, bold_format)

                del df_result

        printinf(f"Файл {result_file_name} создан.")
        printinf("Программа успешно завершена")
        time.sleep(3)

    except Exception as ex:
        print(f"Ошибка! {ex}")


def main():
    printw("Программа собирает информацию из ВСЕХ *.xlsx файлов,\nнаходящихся в папке 'Excel_Files'")
    time.sleep(2)
    list_file_xlsx = get_files_names()
    if not list_file_xlsx:
        printer("Файлы не найдены. Программа завершена")
        time.sleep(3)
        return

    df = merge_data(list_file_xlsx)
    write_to_excel(df)


if __name__ == '__main__':
    main()