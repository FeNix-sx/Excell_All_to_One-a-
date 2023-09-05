from mytools import WorkingYandexDisk
from mytools import Setting


def print_folder_contents(yadisk, folder):
    # Получаем список всех элементов в папке
    items = yadisk.listdir(folder)

    print(items)
    for item in items:
        print(item.name, end=' ')
        if item['type'] == 'dir':
            print(item['path'])  # Выводим имя папки
            # print_folder_contents(yadisk, item['path'])  # Выводим содержимое вложенных папок

def main():
    try:
        setting = Setting()
        token = setting.token
        yadisk = WorkingYandexDisk(token)

        # Вызываем функцию для вывода содержимого корневой папки
        print_folder_contents(yadisk, '/SETTINGS')
        # yadisk.remove('/models.xlsx')
        yadisk.upload_of_yd(folder_name='SETTINGS', filename='models.xlsx', folder_path='')
        print_folder_contents(yadisk, '/SETTINGS')

    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()
