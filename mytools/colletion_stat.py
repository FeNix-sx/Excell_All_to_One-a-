import random
import socket
import getpass
import psutil
import subprocess
import requests
import time
import platform
import wmi
import pythoncom

from datetime import datetime

from mytools.draws import DRAWS
from mytools import ColorPrint


class StatisticCollection:
    def __init__(self):
        self.__collection_dict = dict()
        self.__drawing = random.choice(DRAWS)

    @staticmethod
    def __out_error(error_srt: str )->None:
        print(error_srt)

    def __out_info(self, text: str, func=print, sleep_time: float =0.025) -> None:
        try:
            for i in text:
                func(i, end='', flush=False)
                time.sleep(sleep_time)
            print()

        except Exception as ex:
            self.__out_error(ex)

    def get_my_ip(self) -> str:
        try:
            response = requests.get('https://api.ipify.org?format=json')
            ip = response.json()['ip']
            self.__collection_dict['IP'] = ip
            return ip

        except Exception as ex:
            self.__out_error(ex)

    def get_my_country(self) -> dict:
        try:
            url = f'http://ip-api.com/json/{self.__collection_dict["IP"]}'
            response = requests.get(url).json()

            self.__collection_dict = {
                'IP': response.get('query'),
                'Prov': response.get('isp'),
                'Org': response.get('org'),
                'Country': response.get('country'),
                'regionName': response.get('regionName'),
                'lat': response.get('lat'),
                'lon': response.get('lon')
            }
            return self.__collection_dict

        except Exception as ex:
            self.__out_error(ex)

    def get_cpu_info(self) -> None:
        try:
            # Создание словаря для сохранения результатов
            cpu_dict = {}
            cpu_dict['physical_cores'] = psutil.cpu_count(logical=False)
            cpu_dict['logical_cores'] = psutil.cpu_count(logical=True)
            # Получение информации о частоте работы процессора
            cpu_freq = psutil.cpu_freq()
            cpu_dict['min frequency'] = cpu_freq.min
            cpu_dict['max frequency'] = cpu_freq.max
            cpu_dict['current frequency'] = cpu_freq.current
            self.__collection_dict['CPU'] = cpu_dict

        except Exception as ex:
            self.__out_error(ex)

    def get_rand_access_memory_info(self) -> None:
        try:
            # Инициализация COM
            pythoncom.CoInitialize()
            # Инициализация WMI
            wmi_obj = wmi.WMI()

            # Получение информации о модуле оперативной памяти
            memory_modules = wmi_obj.Win32_PhysicalMemory()

            # Создание словаря для сохранения результатов
            ram_dict = {}
            ram_dict['RAM_modules'] = len(memory_modules)

            for i, module in enumerate(memory_modules):
                ram_dict[module.BankLabel] = {
                    'manufacturer': module.Manufacturer,
                    'model': module.PartNumber,
                    'capacity': str(int(module.Capacity)/(1024**3))+'GB',
                    'speed': module.Speed
                }

            self.__collection_dict['RAM'] = ram_dict

        except Exception as ex:
            self.__out_error(ex)

    def get_hdd_info(self):
        try:
            # Создание словаря для сохранения результатов
            hard_disks = psutil.disk_partitions()
            hdd_dict = {}

            for disk in hard_disks:
                device = disk.device
                try:
                    disk_info = psutil.disk_usage(device)
                    total_size = disk_info.total
                    interface = disk.opts

                    hdd_dict[device] = {
                        'model': '',
                        'manufacturer': '',
                        'total_size': total_size,
                        'interface': interface
                    }
                except Exception as e:
                    pass

            self.__collection_dict['HDD'] = hdd_dict

        except Exception as ex:
            self.__out_error(ex)

    def get_gpu_info(self) -> None:
        try:
            # Получить информацию о видеокарте
            video_card_info = {}

            try:
                wmi_obj = wmi.WMI()
                query = "SELECT * FROM Win32_VideoController"
                video_cards = wmi_obj.query(query)

                for card in video_cards:
                    adapter = card.AdapterCompatibility
                    videoprocessor = card.VideoProcessor

                    video_card_info[card.DeviceID] = {
                        'manufacturer': adapter,
                        'model': videoprocessor,
                    }
            except Exception as e:
                pass

            self.__collection_dict['GPU'] = video_card_info

        except Exception as ex:
            self.__out_error(ex)

    def get_mohter_board_info(self) -> None:
        try:
            # Получить модель материнской платы
            cmd_motherboard = "wmic baseboard get product"
            result_motherboard = [
                item.strip() for item in subprocess.run(cmd_motherboard, capture_output=True, text=True).stdout.split('\n')
                if item
            ]
            self.__collection_dict['MB'] = ', '.join(result_motherboard)

        except Exception as ex:
            self.__out_error(ex)

    def get_os_info(self) -> None:
        try:
            os_list = dict()
            # Получение имени операционной системы
            os_list['os_name'] = platform.system()
            # Получение версии операционной системы
            os_list['os_version'] = platform.release()
            # Получение архитектуры операционной системы
            os_list['os_architecture'] = platform.machine()
            # # Получение информации о конкретном дистрибутиве (только для Linux)
            if platform.system() == 'Linux':
                os_list['distro_info'] = platform.linux_distribution()

            self.__collection_dict['OS'] = os_list

        except Exception as ex:
            self.__out_error(ex)

    def get_user_name(self )->None:
        try:
            # Имя пользователя и доменное имя
            username = getpass.getuser()
            domenname = socket.getfqdn()

            self.__collection_dict["Username"] = username
            self.__collection_dict["domenname"] = domenname

        except Exception as ex:
            self.__out_error(ex)

    def get_time_start(self):
        try:
            boot_time = psutil.boot_time()
            formatted_time = datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
            self.__collection_dict['start_time'] = formatted_time

        except Exception as ex:
            self.__out_error(ex)

    def get_net_setting(self):
        try:
            net_dict = dict()
            net_info = socket.getaddrinfo(socket.gethostname(), None)

            for i, info in enumerate(net_info):
                family = info[0]
                address = info[4][0]
                if family == socket.AF_INET:
                    net_dict[f"IPv4 {i+1}"] = address
                elif family == socket.AF_INET6:
                    net_dict[f"IPv6 {i + 1}"] = address

            self.__collection_dict['NET'] = net_dict

        except Exception as ex:
            self.__out_error(ex)

    @property
    def get_full_info(self )->dict:
        try:
            self.get_my_ip()
            self.get_my_country()
            self.get_os_info()
            self.get_cpu_info()
            self.get_rand_access_memory_info()
            self.get_hdd_info()
            self.get_gpu_info()
            self.get_mohter_board_info()
            self.get_user_name()
            self.get_time_start()
            self.get_net_setting()
            return self.__collection_dict

        except Exception as ex:
            self.__out_error(ex)

    def draw(self):
        printy = ColorPrint().print_yellow
        text = self.__drawing
        self.__out_info(text, printy, sleep_time=0.002)

    def print_smile(self):
        try:
            printy = ColorPrint().print_yellow
            text = '''
                         ............
                      ..................
                    ......................
                  .........::.....^:........
                 .........:@@^...7@#.........
                ...........B&:...~&5..........
                ....^....................:^...
                ...^57..................:YY:..
                .....^J?^............:~??:....
                 ......~5GPY?!!~!7?YP5?:.....
                  ........~?5GBGG5J!:.......
                   .......................
                      ..................
                         ............
            '''
            self.__out_info(text, printy, sleep_time=0.0001)

        except Exception as ex:
            self.__out_error(ex)