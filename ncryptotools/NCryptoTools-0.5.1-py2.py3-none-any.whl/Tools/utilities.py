# -*- coding: utf-8 -*-
"""
Серия функций-помошников, к которым часто приходится обращаться
"""
import os
import json
import re
import datetime


# Данную функцию можно уже не использовать напряму,
# для этого имеется одноимённая функция в классе JIMBase модуля jim_base.py
def serialize(msg_dict):
    """
    Производит сериализацию данных.
    @param msg_dict: словарь с данными клиента/сервера.
    @return: байтовое представление исходного словаря.
    """
    # Проверка, что в качестве параметра был принят именно словарь
    if not isinstance(msg_dict, dict):
        raise TypeError('Входной параметр не относится к типу dict!')

    # Преобразование словаря в JSON строку
    json_msg_str = json.dumps(msg_dict)

    # Преобразование JSON строки в байты
    msg_bytes = json_msg_str.encode('utf-8')

    # Проверка, что в результате преобразования получились байты
    if isinstance(msg_bytes, bytes):
        return msg_bytes
    else:
        raise TypeError('Сериализованные данные не относятся к типу bytes!')


# Данную функцию можно уже не использовать напряму,
# для этого имеется одноимённая функция в классе JIMBase модуля jim_base.py
def deserialize(msg_bytes):
    """
    Производит десериализацию данных.
    @param msg_bytes: данные, представленные в наборе байтов.
    @return: словарь с данными.
    """
    # Проверка, что в качестве параметра было принято сообщение в байтах
    if not isinstance(msg_bytes, bytes):
        raise TypeError('Входной параметр не относится к типу bytes!')

    # Преобразование байтов исходного сообщения в JSON строку
    json_msg_str = msg_bytes.decode('utf-8')

    # Преобразование JSON строки в словарь
    msg_dict = json.loads(json_msg_str)

    # Проверка, что получившаяся структура является словарём
    if isinstance(msg_dict, dict):
        return msg_dict
    else:
        raise TypeError('Десериализованные данные не относятся к типу dict!')


def is_correct_ipv4(ipv4_address):
    """
    Проверяет правильность Ip адреса.
    IPv4 адрес должен быть представлен в виде последовательности из 4 октетов,
    раздетённых точками; значение каждого октета должно быть от 0 до 255.
    @param ipv4_address: IPv4 адрес.
    @return: логическое значение проверки правильности IPv4.
    """
    re_ipv4 = re.compile('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}' +
                         '([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
    return re.fullmatch(re_ipv4, ipv4_address) is not None


def is_correct_port(port_number):
    """
    Проверяет правильность порта.
    Порт должен представлять из себя число в диапазоне от 1023 до 65535.
    Значения до 1023 являются зарезирвированными, поэтому не должны быть использованы.
    @param port_number: номер порта.
    @return: логическое значение проверки правильности порта.
    """
    re_port = re.compile('^(102[3-9]|1[3-9][0-9]{2}|[2-9][0-9]{3}|[1-5][0-9]{4}' +
                         '|6[0-4][0-9]{3}|655[0-2][0-9]|6553[0-5])$')
    return re.fullmatch(re_port, port_number) is not None


def send_msg(sock, msg):
    """
    Отсуществляеть отправку сообщения через сокет.
    @param sock: сокет, с помощью которого осуществляется пересылка.
    @param msg: сообщение, которое необходимо переслать.
    @return: -
    """
    serialized_msg = serialize(msg)
    sock.send(serialized_msg)


def recv_msg(sock):
    """
    Принимает сообщение через сокет и возвращает его в виде словаря.
    Если клиент закрыл соединение, то recv возвратит 0 байтов.
    @param sock: сокет, через который осуществляется приём сообщения.
    @return: словарь с данными сообщения.
    """
    msg_bytes = sock.recv(1024)
    return deserialize(msg_bytes)


def compose_log_file_name(log_file_path):
    """
    Форматирует строку с именем лог-лог файла, приводя его к приемлемому
    виду: добавляется дата/время для удобства.
    @param log_file_path: абсолютный/относительный путь к лог-файлу.
    @return: отформатированный абсолютный/относительный путь к лог-файлу.
    """
    # Если был передан относительный путь к файла, либо путь, который
    # не содержит '\\', то split() вернёт лист с единственным элементом
    path_tokens = log_file_path.split('\\')

    # Форматируем строку, которая содержит текущую временную отметку
    time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Разбивает на имя и расширение файла. Расширение начинается с точки
    file_name, file_extension = os.path.splitext(path_tokens[len(path_tokens)])

    # Обновляем имя файла, добавляя туда временную отметку
    path_tokens[len(path_tokens)] += file_name + '_' + time_str + file_extension

    # Возвращаем сконкатенированные токены пути к файлу
    return '\\'.join(path_tokens)


def is_correct_http_error_code(http_error_code):
    """
    Проверяет правильность кода ошибки HTTP.
    @param http_error_code: код ошибки HTTP.
    @return: логическое значение проверки правильности кода ошибки HTTP.
    """
    re_code = re.compile('^(10[01]|20[012]|40[0-9]|410|500)$')
    return re.fullmatch(re_code, http_error_code) is not None


def is_correct_chat_room_name(chat_room_name):
    """
    Проверяет правильность названия чат комнаты.
    Note: решение не окончательное, может быть изменено, пока
    ограничиваемся длинной названия (3 - 20 символов) и используемыми
    символами (латиница).
    @param chat_room_name: название чат-комнаты.
    @return: логическое значение проверки правильности названия
    чат-комнаты.
    """
    re_chat_room = re.compile('^(#[A-Za-z_]{3,20})$')
    return re.fullmatch(re_chat_room, chat_room_name) is not None


def get_current_time():
    """
    Возвращает текущее время.
    @return: отформатированная строка с текущим временем.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_formatted_date(unix_time_ms):
    """
    Форматирует UNIX-время, переводя его в читаемую форму.
    @param unix_time_ms: UNIX-время в миллисекундах.
    @return: строка с текущим временем и датой.
    """
    return datetime.datetime.fromtimestamp(unix_time_ms).strftime("%Y-%m-%d %H:%M:%S")
