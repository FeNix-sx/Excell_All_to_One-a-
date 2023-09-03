import pickle
import json
import os

def main():
    # Получаем текущую папку
    current_dir = os.getcwd()

    # Проходимся по всем файлам в текущей папке
    for filename in os.listdir(current_dir):
        if filename.endswith('.pickle'):
            # Создаем новое имя файла с расширением .json
            new_filename = os.path.splitext(filename)[0] + '.json'

            # Открываем файл pickle для чтения
            with open(filename, 'rb') as pickle_file:
                # Загружаем данные из файла pickle
                data = pickle.load(pickle_file)

            # Открываем файл json для записи
            with open(new_filename, 'w') as json_file:
                # Преобразование данных в JSON формат и запись в файл
                json.dump(data, json_file, indent=4)

            print(f'Файл {filename} успешно пересохранен в {new_filename}.')

if __name__ == '__main__':
    main()
