import os
import time
import pandas as pd

from datetime import datetime, timedelta
from pandas import DataFrame
from mytools.tool_class import NamesPhone, ColorInput, ColorPrint


printer = ColorPrint().print_error
printinf = ColorPrint().print_info
printw = ColorPrint().print_warning
printw("version 1.6 (29.08.2023)")

change_series = NamesPhone()
FILTER_RES = ["Продажа", "Логистика", "Возврат"]

class ExcelAllInOne:
    def __init__(self):
        printw("Программа собирает информацию из ВСЕХ *.xlsx файлов,\nнаходящихся в папке 'Excel_Files'")
        self.xlsx_files = list()
        self.df_full = DataFrame()
        self.df_art_date = DataFrame()
        self.date_begin = None
        self.date_end = None
        self.inp_begin = None
        self.inp_end = None
        time.sleep(2)

    def get_files_names(self) -> list:
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
            self.xlsx_files = [file for file in file_list if file.endswith('.xlsx')]

            printinf("Обнаружены файлы:\n", *self.xlsx_files)
            return self.xlsx_files

        except Exception as ex:
            print(f"Ошибка! {ex}")

    def check_xlsx_files(self)->bool:
        """проверка наличиня *.xlsx файлов"""
        if not self.xlsx_files:
            printer("Файлы не найдены. Программа завершена")
            time.sleep(3)
            return False
        return True

    def merge_data(self) -> None:
        try:
            df_full = DataFrame()

            for file in self.xlsx_files:
                df_full = pd.concat([df_full, self.load_dataframe(file)], ignore_index=True)
                printinf(f"файл {file} загружен")
            print()

            self.df_full = df_full
            self.data_begin = df_full["дата"].min().date()
            self.date_end = df_full["дата"].max()

        except Exception as ex:
            print(f"Ошибка! {ex}")

    def set_date_begin_end(self) -> None:
        try:
            printw(f"Задайте интересующий временной интервал для выборки данных",
                   f"нижняя граница: {self.data_begin}",
                   f"верхняя граница: {self.date_end.date()}",
                   sep="\n")

            inputdata = ColorInput([self.data_begin, self.date_end]).cinput_date

            inp_begin = inputdata(" c ->: ")
            inp_end = inputdata("по ->: ")
            print()

            printinf(f"Выбран диапазон дат: {inp_begin.strftime('%d.%m.%Y')} - {inp_end.strftime('%d.%m.%Y')}")

            self.inp_begin, self.inp_end = inp_begin, inp_end

        except Exception as ex:
            print(f"Ошибка! {ex}")

    def transformation_dataframe(self):
        try:
            # заменяем текстовое поле обоснование на поля с int
            df_dummies = pd.get_dummies(self.df_full["обоснование"], dtype=int)

            df_full = pd.concat([self.df_full, df_dummies], axis=1)
            del df_dummies

            # налог и прибыль не учитывается когда был возврат
            if 'Возврат' not in df_full.columns:
                df_full["Возврат" ] = 0
                print("Добавлены Возврат")

            df_full.loc[df_full['Возврат'] == 1, 'налог'] *= 0
            df_full.loc[df_full['Возврат'] == 1, 'к перечислению'] *= 0

            self.df_art_date = df_full[["артикул", "дата"]].copy()

            df_full = df_full[
                (df_full["дата"] >= self.inp_begin) &
                (df_full["дата"] <= self.inp_end)
            ]
            # удаляем поле ["дата", "обоснование"]
            df_full.drop(["дата", "обоснование", "Телефон"], axis=1, inplace=True)
            # создаем поле с чистой прибылью
            df_full.insert(
                loc=3,
                column="чистая прибыль",
                value=df_full["к перечислению"] -
                      df_full["налог"] -
                      df_full["логистика_затраты"] -
                      df_full["штрафы_затраты"] -
                      df_full["Логистика"] * 157.5
            )
            if 'Штрафы' not in df_full.columns:
                df_full["Штрафы" ] = 0
                print("Добавлены Штрафы")

            # меняем местами столбцы
            self.df_full = df_full[
                [
                    'артикул', 'код принта', 'Кол-во', 'чистая прибыль', 'к перечислению',
                    'налог', 'логистика_затраты', 'штрафы_затраты', 'телефон',
                    'код', 'Возврат', 'Логистика', 'Продажа', 'Штрафы'
                ]
            ]
            del df_full

            return self.df_full

        except Exception as ex:
            print(f"Ошибка! {ex}")

    @staticmethod
    def load_dataframe(filename: str = None) -> DataFrame:
        """
        Загрузка каждого файла из папки Excel_Files в датафрейм
        :param filename:
        :return:
        """
        try:
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
            # test1 = change_series.get_names_phone(df_source["Артикул поставщика"])
            df_source["телефон"] = change_series.get_names_phone(df_source["Артикул поставщика"])
            # test2 = df_source["Артикул поставщика"].str[-3:]
            df_source["Название"] = df_source["Артикул поставщика"].str[-3:]
            # test3 = df_source["Артикул поставщика"]
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

    def create_table_to_excel(self, group, GROUP_LIST):
        """
        Создаем таблицу для выгрузки в Excel
        :param group:
        :param GROUP_LIST:
        :return:
        """
        # задаем список полей для агрегации
        agg_list = [item for item in self.df_full.columns if item not in GROUP_LIST]
        agg_dict = {item: "sum" for item in agg_list}
        df_result = self.df_full.groupby(  # группировка DataFrame по параметру списка group
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
        return df_result

    def last_seven_days_table(self) -> DataFrame:
        """
        Создаем таблицу для подсчета продаж за последние 5 дней для каждого артикула
        (хз для чего она ему!?!?!)
        :return:
        """
        try:
            # выбираем последние 7 дней
            # для сравнения использовать формат ТОЛЬКО ТАКОЙ: 2023-04-01 00:00:00
            df_test = self.df_art_date[(self.df_art_date["дата"] >= self.date_end - timedelta(days=6))]
            # заменяем текстовое поле обоснование на поля с int (строки стали столбцами)
            df_dummies = pd.get_dummies(df_test["дата"], dtype=int)
            # приводим заголовки к виду "00.00.0000"
            column_names_dict = dict()
            for date in df_dummies.columns.tolist():
                column_names_dict[date] = date.strftime('%d.%m.%Y')
            df_dummies = df_dummies.rename(columns=column_names_dict)

            df_test = pd.concat([df_test[["артикул"]], df_dummies], axis=1)
            del df_dummies
            # группировка и агрегирование по артикулу
            df_result = df_test.groupby(  # группировка DataFrame по полю "артикул"
                ["артикул"],
                as_index=False
            ).aggregate(  # агрегирование столбцов
                "sum"
            )
            df_result["дней"] = df_result.iloc[:, 1:].apply(lambda x: x[x !=0].count() ,axis=1)
            df_result["количество"] = df_result.iloc[:, 1:-1].sum(axis=1)
            df_result["ср.коэф"] = round(df_result["количество"]/7, 6)
            del df_test
            columns = list(df_result.columns)
            # меняем местами столбцы
            columns[-3], columns[-2], columns[-1] = columns[-1], columns[-3], columns[-2]
            df_result = df_result[columns]
            self.df_art_date = df_result.sort_values("ср.коэф", ascending=False)

        except Exception as ex:
            print(ex)

    def write_to_excel(self) -> None:
        """
        Запись данных в Excel-файл
        :return:
        """
        try:
            GROUP_LIST = [
                'артикул',
                'телефон',
                'код принта',
                'код'
            ]
            df_full = self.df_full
            result_file_name = f"RESULT.xlsx"
            # создаем файл result_file_name
            with pd.ExcelWriter(result_file_name, engine='xlsxwriter') as writer:
                for group in GROUP_LIST:
                    df_result = self.create_table_to_excel(group, GROUP_LIST)
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
                    # закрепляем первую строку
                    worksheet.freeze_panes(1, 0)

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

                # создаем лист seven_days в файле result_file_name и записываем туда df_art_date
                self.df_art_date.to_excel(
                    writer,
                    sheet_name=f"seven_days",
                    index=False,
                    startrow=0
                )

                # получаем объект workbook и worksheet нужного листа
                workbook = writer.book
                worksheet = writer.sheets[f"seven_days"]
                # закрепляем первую строку
                worksheet.freeze_panes(1, 0)

                # задаем ширину столбцов
                for i, col in enumerate(self.df_art_date):
                    max_width = max(self.df_art_date[col].astype(str).map(len).max(), len(col))
                    worksheet.set_column(i, i, max_width + 2)

                # задаем стиль для заголовка таблицы
                header_style = workbook.add_format({
                    'bg_color': 'black', 'font_color': 'white',
                    'bold': True, 'align': 'center'
                })

                # Задаем заголовок таблицы
                for i, header in enumerate(self.df_art_date.columns):
                    worksheet.write(0, i, header, header_style)

            printinf(f"Файл {result_file_name} создан.")
            printinf("Программа успешно завершена")
            time.sleep(3)

        except Exception as ex:
            print(f"Ошибка! {ex}")

    def main(self):
        try:
            self.get_files_names()
            if not self.check_xlsx_files():
                return
            self.merge_data()
            self.set_date_begin_end()
            self.transformation_dataframe()
            self.last_seven_days_table()
            self.write_to_excel()
        except:
            pass

if __name__ == '__main__':
    runscript = ExcelAllInOne()
    runscript.main()
