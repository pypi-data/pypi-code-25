# -*- coding: utf-8 -*-
"""
Модуль, предназначенный для классов и функций, которые связаны с
JSON-объектами типа 'Action'.
"""
import abc
from NCryptoTools.JIM.jim_base import JIMBase, JSONObjectType


class JIMActionBase(JIMBase):
    """
    Базовый класс для всех JIM-классов типа 'Action'.
    """
    def __init__(self, json_object_type, action):
        """
        Конструктор.
        @param json_object_type: тип JSON-объекта.
        @param action: значение типа события.
        """
        super().__init__(json_object_type)
        self._action = action

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

# ########################################################################
# Сообщения от КЛИЕНТА к СЕРВЕРУ
# ########################################################################


class JIMToServerAuth(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_SERVER_AUTH.
    """
    def __init__(self, time, login, password):
        """
        Конструктор.
        @param time: текущее время.
        @param login: уникальный идентификатор пользователя (логин).
        @param password: пароль пользователя.
        """
        super().__init__(JSONObjectType.TO_SERVER_AUTH, 'authenticate')
        self._time = time
        self._user = ('login', 'password')
        self._login = login
        self._password = password

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'time': self._time,
                'user': {'login': self._login,
                         'password': self._password
                         }
                }

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Создаёт объект класса на основании поступившего JSON-объекта.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['time'],
                   msg_dict['msg']['login'],
                   msg_dict['msg']['password'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'time', 'user'} <= set(msg_dict) and \
               {'login', 'password'} <= set(msg_dict['user'])


class JIMToServerQuit(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_SERVER_QUIT.
    """
    def __init__(self):
        """
        Конструктор.
        """
        super().__init__(JSONObjectType.TO_SERVER_QUIT, 'quit')

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls()

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return 'action' in msg_dict


class JIMToServerPresence(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_SERVER_PRESENCE.
    """
    def __init__(self, time, login, status):
        """
        Конструктор.
        @param time: текущее время.
        @param login: уникальный идентификатор пользователя (логин).
        @param status: статус пользователя.
        """
        super().__init__(JSONObjectType.TO_SERVER_PRESENCE, 'presence')
        self._time = time
        self._type = 'status'
        self._user = ('account_name', 'status')
        self._login = login
        self._status = status

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'time': self._time,
                'type': self._type,
                'user': {'login': self._login,
                         'status': self._status
                         }
                }

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['time'],
                   msg_dict['user']['login'],
                   msg_dict['user']['status'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'time', 'type', 'user'} <= set(msg_dict) and \
               {'login', 'status'} <= set(msg_dict['user'])


class JIMToServerPersonalMsg(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_SERVER_PERSONAL_MSG.
    """
    def __init__(self, time, login_to, login_from, encoding, message):
        """
        Констуктор.
        @param time: текущее время.
        @param login_to: уникальный идентификатор получателя (логин).
        @param login_from: уникальный идентификатор отправителя (логин).
        @param encoding: кодировка.
        @param message: текст сообщения.
        """
        super().__init__(JSONObjectType.TO_SERVER_PERSONAL_MSG, 'msg')
        self._time = time
        self._login_to = login_to
        self._login_from = login_from
        self._encoding = encoding
        self._message = message

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'time': self._time,
                'to': self._login_to,
                'from': self._login_from,
                'encoding': self._encoding,
                'message': self._message}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['time'],
                   msg_dict['to'],
                   msg_dict['from'],
                   msg_dict['encoding'],
                   msg_dict['message'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'time', 'to', 'from', 'encoding', 'message'} <= set(msg_dict)


class JIMToServerChatMsg(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_SERVER_CHAT_MSG.
    """
    def __init__(self, time, login_to, login_from, message):
        """
        Конструктор.
        @param time: текущее время.
        @param login_to: имя пользователя-отправителя.
        @param login_from: имя пользователя-получателя.
        @param message: текст сообщения.
        """
        super().__init__(JSONObjectType.TO_SERVER_CHAT_MSG, 'msg')
        self._time = time
        self._login_to = login_to
        self._login_from = login_from
        self._message = message

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'time': self._time,
                'to': self._login_to,
                'from': self._login_from,
                'message': self._message
                }

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['time'],
                   msg_dict['to'],
                   msg_dict['from'],
                   msg_dict['message'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'time', 'to', 'from', 'message'} <= set(msg_dict)


class JIMToServerJoinChat(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_SERVER_JOIN_CHAT.
    """
    def __init__(self, time, login, chat_room):
        """
        Конструктор.
        @param time: текущее время.
        @param login: уникальный идентификатор пользователя (логин).
        @param chat_room: название чат-комнаты.
        """
        super().__init__(JSONObjectType.TO_SERVER_JOIN_CHAT, 'join')
        self._time = time
        self._login = login
        self._room = chat_room

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'time': self._time,
                'login': self._login,
                'room': self._room
                }

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['time'],
                   msg_dict['login'],
                   msg_dict['room'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'time', 'login', 'room'} <= set(msg_dict)


class JIMToServerLeaveChat(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_SERVER_LEAVE_CHAT.
    """
    def __init__(self, time, login, room):
        """
        Конструктор.
        @param time: текущее время.
        @param login: уникальный идентификатор пользователя (логин).
        @param room: название чат-комнаты.
        """
        super().__init__(JSONObjectType.TO_SERVER_LEAVE_CHAT, 'leave')
        self._time = time
        self._login = login
        self._room = room

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'time': self._time,
                'login': self._login,
                'room': self._room}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['time'],
                   msg_dict['login'],
                   msg_dict['room'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'time', 'login', 'room'} <= set(msg_dict)


class JIMToServerGetContacts(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_SERVER_GET_CONTACTS.
    """
    def __init__(self, time):
        """
        Конструктор.
        @param time: текущее время.
        """
        super().__init__(JSONObjectType.TO_SERVER_GET_CONTACTS, 'get_contacts')
        self._time = time

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'time': self._time}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['time'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'time'} <= set(msg_dict)


class JIMToServerManageContact(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_SERVER_ADD_CONTACT.
    """
    def __init__(self, action, time, contact_login):
        """
        Конструктор.
        @param action: тип действия по отношению к контакту. Возможные варианты:
        - "add_contact" - добавить контакт;
        - "del_contact" - удалить контакт.
        @param time: текущее время.
        @param contact_login: логин контакта, который должен быть добавлен/удалён.
        """
        super().__init__(JSONObjectType.TO_SERVER_ADD_CONTACT, action)
        self._time = time
        self._login = contact_login

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'time': self._time,
                'login': self._login}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['action'],
                   msg_dict['time'],
                   msg_dict['login'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'login', 'time'} <= set(msg_dict)


class JIMToServerGetMsgs(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_SERVER_GET_MSGS.
    """
    def __init__(self, time, chat_name):
        """
        Конструктор.
        @param time: текущее время.
        @param chat_name: название контакта (имя контакта или название чат-комнаты).
        """
        super().__init__(JSONObjectType.TO_SERVER_GET_MSGS, 'get_msgs')
        self._time = time
        self._chat_name = chat_name

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'time': self._time,
                'chat_name': self._chat_name}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['time'],
                   msg_dict['chat_name'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'time', 'chat_name'} <= set(msg_dict)

# ########################################################################
# Сообщения от СЕРВЕРА к КЛИЕНТУ
# Note: при запросе списка сообщений от сервера (JIMToServerGetMsgs) сер-
# вер возвращает следующие сообщения:
# (1) JIMToClientQuantity (количество возвращаемых сообщений);
# (2.1) JIMToServerPersonalMsg (персональное сообщение);
# (2.2) JIMToServerChatMsg (сообщение в чат-комнату).
# ########################################################################


class JIMToClientProbe(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_CLIENT_PROBE.
    """
    def __init__(self, time):
        """
        Конструктор.
        @param time: текущее время.
        """
        super().__init__(JSONObjectType.TO_CLIENT_PROBE, 'probe')
        self._time = time

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'time': self._time}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['time'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'time'} <= set(msg_dict)


class JIMToClientContactList(JIMActionBase):
    """
    JIM-класс для сообщений типа: JSONObjectType.TO_CLIENT_CONTACT_LIST.
    """
    def __init__(self, contact_list):
        """
        Конструктор.
        @param contact_list: логин контакта пользователя.
        """
        super().__init__(JSONObjectType.TO_CLIENT_CONTACT_LIST, 'contact_list')
        self._login = contact_list

    def to_dict(self):
        """
        Осуществляет преобразования полей класса в JSON-объект (словарь).
        @return: JSON-объект (словарь).
        """
        return {'action': self._action,
                'login': self._login}

    @classmethod
    def from_dict(cls, msg_dict):
        """
        Осуществляет распаковку JSON-объекта и заполняет поля класса.
        @param msg_dict: JSON-объект, который нуждается в распаковке.
        @return: экзепляр данного JIM-класса со значениями атрибутов,
        взятых из JSON-структуры.
        """
        return cls(msg_dict['login'])

    @staticmethod
    def is_correct_format(msg_dict):
        """
        Статический метод, который проверяет правильность JSON-структуры для
        данного типа JIM-объектов.
        @param msg_dict: JSON-структура, которая нуждается в проверке.
        @return: логическое значение правильности JSON-структуры. (Boolean)
        """
        return {'action', 'login'} <= set(msg_dict)
