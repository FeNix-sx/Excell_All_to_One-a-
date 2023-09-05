import pickle
import json
import time
import os

def main():
    try:

        pickle_files = [file for file in os.listdir('.') if file.endswith('.pickle')]
        print(pickle_files)

        for file in pickle_files:

            # Загрузка словаря из файла pickle
            with open(file, 'rb') as f:
                loaded_dict = pickle.load(f)

            # Запись словаря в файл JSON
            file_json = f"{file[:-7:]}.json"
            with open(file_json, 'w') as f:
                json.dump(loaded_dict, f, indent=4)

            print(f"Файл {file} успешно перезаписан в файл JSON!")
        time.sleep(3)

    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()
