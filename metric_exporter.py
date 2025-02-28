import json
import os
import datetime
import time
import multiprocessing
from pprint import pprint as pp

# Получение текущей даты для имени файла
day = datetime.datetime.today().today().strftime("%Y-%m-%d")
# Путь к директории для логов
log_path = "/var/log"
# Имя файла лога
file_name = day + "-metric-monitoring.log"
# Текущая метка времени в наносекундах
unix_time = time.time_ns()

# Функция для получения процента времени ожидания ввода-вывода (iowait) процессора.
def proc_stat():
    # Получение количества тиков в секунду
    jiffy = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
    # Получение количества доступных процессоров
    num_cpu = multiprocessing.cpu_count()

    # Чтение статистики процессора из /proc/stat
    with open('/proc/stat') as stat_fd:
        for stat in stat_fd.readlines():
            if stat.startswith("cpu "):
                iowait = float(stat.split(' ')[6])  # Получение значения iowait

    # Ожидание 1 секунды для получения новых данных
    time.sleep(1)

    # Чтение статистики процессора снова
    with open('/proc/stat') as stat_fd:
        for stat in stat_fd.readlines():
            if stat.startswith("cpu "):
                iowait_n = float(stat.split(' ')[6])  # Получение нового значения iowait
    
    # Вычисление процента времени ожидания ввода-вывода
    iowait_s = round(((iowait_n - iowait) * 100 / jiffy) / num_cpu, 2)
    return iowait_s  # Возврат значения iowait

# Функция для записи метрик в файл.
def write_file_metrics(metrics_dict):
    if not os.path.isdir(log_path):
        # Создание директории, если она не существует
        os.mkdir(log_path)

    if not os.path.exists(log_path + "/" + file_name):
        # Создание файла, если он не существует
        with open(log_path + "/" + file_name, 'w') as f:
            pass

    if os.path.isfile(log_path + "/" + file_name):
        # Запись метрик в файл
        with open(log_path + "/" + file_name, "a") as f:
            f.write(json.dumps(metrics_dict) + '\n')

# Функция для получения средней загрузки системы.
def load_average():
    with open("/proc/loadavg") as file:
        # Чтение средней загрузки
        load_average = file.read().split(' ')[0]
        # Возврат значения средней загрузки
        return float(load_average)

# Функция для получения информации о памяти.
def mem_info():
    with open("/proc/meminfo") as file:
        mem_available = swap_free = mem_active = None  # Инициализация переменных значением None
        for mem in file.readlines():
            # Доступная память
            if mem.startswith("MemAvailable:"):
                mem_available = int(mem.split(':')[1].lstrip().split(' ')[0])
            # Свободное пространство подкачки
            elif mem.startswith("SwapFree:"):
                swap_free = int(mem.split(':')[1].lstrip().split(' ')[0])
            # Активная память
            elif mem.startswith("Active:"):
                mem_active = int(mem.split(':')[1].lstrip().split(' ')[0])
        # Возврат информации о памяти        
        return [mem_available, swap_free, mem_active]

# Сбор метрик
load_average = load_average()  # Получение средней загрузки
iowait = proc_stat()  # Получение значения iowait
# Получение информации о памяти
mem_available, swap_free, mem_active = mem_info()

# Создание словаря с метриками
metrics_dict = {
    "timestamp": unix_time,  # Время в наносекундах, когда были собраны метрики
    "load average": load_average,  # Средняя загрузка системы за последние 1, 5 и 15 минут
    "iowait": iowait,  # Процент времени ожидания ввода-вывода процессора
    "mem_available": mem_available,  # Доступная память в килобайтах
    "swap_free": swap_free,  # Свободное пространство подкачки в килобайтах
    "mem_active": mem_active  # Активная память в килобайтах
}

# Запись метрик в файл
write_file_metrics(metrics_dict)

# Вывод информации о записанных метриках в консоль для отладки
# pp(f"Записаны метрики в файл: {log_path}/{file_name}")
# pp(metrics_dict)  # Вывод содержимого записанных метрик