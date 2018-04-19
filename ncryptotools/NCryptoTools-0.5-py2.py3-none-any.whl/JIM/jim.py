# -*- coding: utf-8 -*-
"""
Вспомогательные функции и константы для протокола JIM.
"""
from Solution.NCryptoTools.Utils.utilities import is_correct_chat_room_name
from Solution.NCryptoTools.JIM.jim_base import UnknownJSONObjectType
from Solution.NCryptoTools.JIM.jim_action import *
from Solution.NCryptoTools.JIM.jim_response import *


class IncorrectHTTPErrorCode(Exception):
    """
    Класс для исключений, связанных с неверными кодами ошибок HTTP.
    """
    def __init__(self, http_error_code):
        """
        Конструктор. Созраняет некорректное значение кода ошибки HTTP.
        @param http_error_code: некорректное значение кода ошибки HTTP.
        """
        self.http_error_code = http_error_code

    def __str__(self):
        """
        Выводит текст исключения.
        @return: строка исключения в читаемой форме.
        """
        return 'Некорректное значение кода ошибки HTTP: {}'.format(self.http_error_code)


class IncorrectChatRoomName(Exception):
    """
    Класс для исключений, связанных с некорректными названиями чат-комнат.
    """
    def __init__(self, chat_room_name):
        """
        Конструктор. Созраняет некорректное значение названия чат-комнаты.
        @param chat_room_name: названия чат-комнаты.
        """
        self.chat_room_name = chat_room_name

    def __str__(self):
        """
        Выводит текст исключения.
        @return: строка исключения в читаемой форме.
        """
        return 'Некорректное имя чат-комнаты: {}'.format(self.chat_room_name)


class JIMManager:
    """
    Класс для генераций сущностей JIM.
    Реализован в качестве Factory-паттерна.
    """
    @staticmethod
    def create_jim_object(json_object_type, *args):
        """
        Статический метод, который возвращает экземпляр нужного JIM-класса.
        @param json_object_type: тип JSON-объекта.
        @param args: дополнительные аргументы для конструкторов JSON-объектов.
        @return:
        """
        if json_object_type == JSONObjectType.TO_SERVER_AUTH:
            return JIMToServerAuth(*args)

        if json_object_type == JSONObjectType.TO_SERVER_QUIT:
            return JIMToServerQuit()

        if json_object_type == JSONObjectType.TO_SERVER_PRESENCE:
            return JIMToServerPresence(*args)

        if json_object_type == JSONObjectType.TO_CLIENT_PROBE:
            return JIMToClientProbe(*args)

        if json_object_type == JSONObjectType.TO_SERVER_PERSONAL_MSG:
            return JIMToServerPersonalMsg(*args)

        if json_object_type == JSONObjectType.TO_SERVER_CHAT_MSG:
            if not is_correct_chat_room_name(args[1]):
                raise IncorrectChatRoomName(args[1])
            return JIMToServerChatMsg(*args)

        if json_object_type == JSONObjectType.TO_SERVER_JOIN_CHAT:
            if not is_correct_chat_room_name(args[len(args) - 1]):
                raise IncorrectChatRoomName(args[len(args)] - 1)
            return JIMToServerJoinChat(*args)

        if json_object_type == JSONObjectType.TO_SERVER_LEAVE_CHAT:
            if not is_correct_chat_room_name(args[len(args) - 1]):
                raise IncorrectChatRoomName(args[len(args) - 1])
            return JIMToServerLeaveChat(*args)

        if json_object_type == JSONObjectType.TO_CLIENT_INFO:
            if str(args[0])[0] not in ['1', '2']:
                raise IncorrectHTTPErrorCode(args[0])
            return JIMToClientAlert(*args)

        if json_object_type == JSONObjectType.TO_CLIENT_ERROR:
            if str(args[0])[0] not in ['4', '5']:
                raise IncorrectHTTPErrorCode(args[0])
            return JIMToClientError(*args)

        if json_object_type == JSONObjectType.TO_SERVER_GET_CONTACTS:
            return JIMToServerGetContacts(*args)

        if json_object_type == JSONObjectType.TO_CLIENT_QUANTITY:
            return JIMToClientQuantity(*args)

        if json_object_type == JSONObjectType.TO_CLIENT_CONTACT_LIST:
            return JIMToClientContactList(*args)

        if json_object_type == JSONObjectType.TO_CLIENT_MSG_LIST:
            pass
            # return JIMToClientMsgList(*args)

        if json_object_type == JSONObjectType.TO_SERVER_ADD_CONTACT:
            return JIMToServerManageContact('add_contact', *args)

        if json_object_type == JSONObjectType.TO_SERVER_DEL_CONTACT:
            return JIMToServerManageContact('del_contact', *args)

        if json_object_type == JSONObjectType.TO_SERVER_GET_MSGS:
            return JIMToServerGetMsgs(*args)

        raise UnknownJSONObjectType(json_object_type)

    @staticmethod
    def determine_jim_msg_type(msg):
        """
        Определяет, к какому типу относится JSON-объект. Если была найдена ошибка в
        формате словаря, то выкидывает исключение.
        @param msg: JSON-объект (словарь).
        @return: тип JSON-объекта.
        """
        if isinstance(msg, dict):
            if len(msg) == 0:
                raise UnknownJSONObjectType(msg)

            if 'action' in msg:
                if msg['action'] == 'authenticate':
                    if JIMToServerAuth.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_AUTH
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'quit':
                    if JIMToServerQuit.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_QUIT
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'presence':
                    if JIMToServerPresence.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_PRESENCE
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'probe':
                    if JIMToClientProbe.is_correct_format(msg):
                        return JSONObjectType.TO_CLIENT_PROBE
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'msg':
                    if 'encoding' in msg and JIMToServerPersonalMsg.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_PERSONAL_MSG
                    if JIMToServerChatMsg.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_CHAT_MSG
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'join':
                    if JIMToServerJoinChat.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_JOIN_CHAT
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'leave':
                    if JIMToServerLeaveChat.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_LEAVE_CHAT
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'get_contacts':
                    if JIMToServerGetContacts.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_GET_CONTACTS
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'add_contact':
                    if JIMToServerManageContact.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_ADD_CONTACT
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'del_contact':
                    if JIMToServerManageContact.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_DEL_CONTACT
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'get_msgs':
                    if JIMToServerGetMsgs.is_correct_format(msg):
                        return JSONObjectType.TO_SERVER_GET_MSGS
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'contact_list':
                    if JIMToClientContactList.is_correct_format(msg):
                        return JSONObjectType.TO_CLIENT_CONTACT_LIST
                    raise UnknownJSONObjectType(msg)

                if msg['action'] == 'msg_list':
                    if JIMToClientMsgList.is_correct_format(msg):
                        return JSONObjectType.TO_CLIENT_MSG_LIST
                    raise UnknownJSONObjectType(msg)

            if 'response' in msg:
                if JIMToClientAlert.is_correct_format(msg):
                    return JSONObjectType.TO_CLIENT_INFO

                if JIMToClientError.is_correct_format(msg):
                    return JSONObjectType.TO_CLIENT_ERROR

                if JIMToClientQuantity.is_correct_format(msg):
                    return JSONObjectType.TO_CLIENT_QUANTITY

                raise UnknownJSONObjectType(msg)
        else:
            raise TypeError('Ошибка некорректный тип входного параметра!' +
                            '\nОжидалось: <class \'dict\'>; ' +
                            '\nПолучено:', type(msg))
