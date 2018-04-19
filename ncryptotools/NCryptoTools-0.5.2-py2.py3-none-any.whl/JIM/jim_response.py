# -*- coding: utf-8 -*-
"""
Модуль, предназначенный для классов и функций, которые связаны с
JSON-объектами типа 'Response'.
"""
import abc
from NCryptoTools.JIM.jim_base import JIMBase, JSONObjectType


class JIMResponseBase(JIMBase):
    """
    Базовый класс для всех JIM-классов типа 'Response'.
    """
    def __init__(self, json_object_type, code):
        """
        Конструктор.
        @param json_object_type: тип JSON-объекта.
        @param code: HTTP-код.
        """
        super().__init__(json_object_type)
        self._response = code

    @abc.abstractmethod
    def to_dict(self):
        """
        Абстрактный метод. В классах наследниках он преобразует
        отдельные поля класса в JSON-объект с правильной структурой.
        @return: в классах наследниках возвращается сформированный JSON-объект.
        """
        pass

    @abc.abstractmethod
    def from_dict(self, msg_dict):
        """
        Абстракнтый метод. В классах наследниках он распаковывает
        JSON-объект и заполняет поля класса в соответствии со знаечниями,
        взятыми из словаря.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: в классах наследниках возвращает экзепляр JIM-класса
        со значениями атрибутов, взятых из JSON-структуры.
        """
        pass


class JIMToClientAlert(JIMResponseBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_CLIENT_INFO.
    """
    def __init__(self, code, alert):
        """
        Конструктор.
        @param code: HTTP-код.
        @param alert: текст сообщения от сервера.
        """
        super().__init__(JSONObjectType.TO_CLIENT_INFO, code)
        self._alert = alert

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'response': self._response,
                'alert': self._alert}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['response'],
                   msg_dict['alert'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность
        JSON-структуры для данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'response', 'alert'} <= set(msg_dict)


class JIMToClientError(JIMResponseBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_CLIENT_ERROR.
    """
    def __init__(self, code, error):
        """
        Конструктор.
        @param code: HTTP-код.
        @param error: текст ошибки от сервера.
        """
        super().__init__(JSONObjectType.TO_CLIENT_ERROR, code)
        self._error = error

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'response': self._response,
                'error': self._error}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['response'],
                   msg_dict['error'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность
        JSON-структуры для данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'response', 'error'} <= set(msg_dict)


class JIMToClientQuantity(JIMResponseBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_CLIENT_QUANTITY.
    """
    def __init__(self, code, quantity):
        """
        Конструктор.
        @param code: HTTP-код.
        @param quantity: количественный показатель контактов клиента.
        """
        super().__init__(JSONObjectType.TO_CLIENT_QUANTITY, code)
        self._quantity = quantity

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'response': self._response,
                'quantity': self._quantity}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['response'],
                   msg_dict['quantity'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность
        JSON-структуры для данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'response', 'quantity'} <= set(msg_dict)
