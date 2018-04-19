# -*- coding: utf-8 -*-
"""
Модуль для тестирования модуля jim.py
"""
import pytest
import datetime

from Solution.NCryptoTools.JIM.jim_base import UnknownJSONObjectType, JSONObjectType
from Solution.NCryptoTools.JIM.jim import JIMManager


@pytest.fixture(scope='function', params=[
    ({'action': 'authenticate',
      'time': datetime.time(),
      'user': {'login': 'Dreqn1te',
               'password': 'abcd1234'
               }
      }, JSONObjectType.TO_SERVER_AUTH),

    ({'action': 'quit'}, JSONObjectType.TO_SERVER_QUIT),

    ({'action': 'presence',
      'time': datetime.time(),
      'type': 'status',
      'user': {'login': 'Dreqn1te',
               'status': 'Greetings!'
               }
      }, JSONObjectType.TO_SERVER_PRESENCE),

    ({'action': 'probe',
      'time': datetime.time()
      }, JSONObjectType.TO_CLIENT_PROBE),

    ({'action': 'msg',
      'time': datetime.time(),
      'to': 'Ivan Ivanov',
      'from': 'Dreqn1te',
      'encoding': 'utf-8',
      'message': 'Hi!'
      }, JSONObjectType.TO_SERVER_PERSONAL_MSG),

    ({'action': 'msg',
      'time': datetime.time(),
      'to': '#GeekBrains',
      'from': 'Dreqn1te',
      'message': 'Hi!'
      }, JSONObjectType.TO_SERVER_CHAT_MSG),

    ({'action': 'join',
      'time': datetime.time(),
      'login': 'Dreqn1te',
      'room': '#GeekBrains'
      }, JSONObjectType.TO_SERVER_JOIN_CHAT),

    ({'action': 'leave',
      'time': datetime.time(),
      'login': 'Dreqn1te',
      'room': '#GeekBrains'
      }, JSONObjectType.TO_SERVER_LEAVE_CHAT),

    ({'action': 'get_contacts',
      'time': datetime.time()
      }, JSONObjectType.TO_SERVER_GET_CONTACTS),

    ({'action': 'add_contact',
      'time': datetime.time(),
      'login': 'Dreqn1te'
      }, JSONObjectType.TO_SERVER_ADD_CONTACT),

    ({'action': 'del_contact',
      'time': datetime.time(),
      'login': 'Dreqn1te'
      }, JSONObjectType.TO_SERVER_DEL_CONTACT),

    ({'action': 'get_msgs',
      'time': datetime.time(),
      'chat_name': 'Dreqn1te'
      }, JSONObjectType.TO_SERVER_GET_MSGS),

    ({'action': 'contact_list',
      'login': 'Vasya'
      }, JSONObjectType.TO_CLIENT_CONTACT_LIST),

    ({'response': '200',
      'alert': 'OK'
      }, JSONObjectType.TO_CLIENT_INFO),

    ({'response': '404',
      'error': 'Not Found!'
      }, JSONObjectType.TO_CLIENT_ERROR),

    ({'response': '200',
      'quantity': '5'
      }, JSONObjectType.TO_CLIENT_QUANTITY),

    ({'action': 'presence'}, JSONObjectType.UNKNOWN_JSON_OBJECT_TYPE),

    ({}, JSONObjectType.UNKNOWN_JSON_OBJECT_TYPE)
])
def param_test_determine_jim_msg_type(request):
    """
    Фикстура для функции test_determine_jim_msg_type.
    @param request: request-объект.
    @return: пара (входное значение (List[String]); ожидаемый результат (Boolean)).
    """
    return request.param


def test_determine_jim_msg_type(param_test_determine_jim_msg_type):
    """
    Тест-функция для determine_jim_msg_type функции.
    @param param_test_determine_jim_msg_type: ссылка на фикстуру с данными для тестирования.
    @return: -
    """
    input_list, expected_output = param_test_determine_jim_msg_type

    try:
        result = JIMManager.determine_jim_msg_type(input_list)
    except UnknownJSONObjectType:
        result = JSONObjectType.UNKNOWN_JSON_OBJECT_TYPE

    # print()
    # print('-' * 79)
    # print('На входе: {0}\nНа выходе: {1}\nОжидалось: {2}'.format(' '.join(input_list),
    #                                                              result, expected_output))
    # print('-' * 79)
    assert expected_output == result


@pytest.fixture(scope='function', params=[
    ([JSONObjectType.TO_SERVER_AUTH, datetime.time(), 'Dreqn1te', 'abcd1234'],
     JSONObjectType.TO_SERVER_AUTH),

    ([JSONObjectType.TO_SERVER_QUIT],
     JSONObjectType.TO_SERVER_QUIT),

    ([JSONObjectType.TO_SERVER_PRESENCE, datetime.time(), 'Dreqn1te', 'Greetings!'],
     JSONObjectType.TO_SERVER_PRESENCE),

    ([JSONObjectType.TO_CLIENT_PROBE, datetime.time()],
     JSONObjectType.TO_CLIENT_PROBE),

    ([JSONObjectType.TO_SERVER_PERSONAL_MSG, datetime.time(), 'John546', 'Dreqn1te', 'utf-8', 'Hi!'],
     JSONObjectType.TO_SERVER_PERSONAL_MSG),

    ([JSONObjectType.TO_SERVER_CHAT_MSG, datetime.time(), '#GeekBrains', 'Dreqn1te', 'Hi!'],
     JSONObjectType.TO_SERVER_CHAT_MSG),

    ([JSONObjectType.TO_SERVER_JOIN_CHAT, datetime.time(), 'Dreqn1te', '#GeekBrains'],
     JSONObjectType.TO_SERVER_JOIN_CHAT),

    ([JSONObjectType.TO_SERVER_LEAVE_CHAT, datetime.time(), 'Dreqn1te', '#GeekBrains'],
     JSONObjectType.TO_SERVER_LEAVE_CHAT),

    ([JSONObjectType.TO_SERVER_GET_CONTACTS, datetime.time()],
     JSONObjectType.TO_SERVER_GET_CONTACTS),

    ([JSONObjectType.TO_CLIENT_CONTACT_LIST, 'Vasya'],
     JSONObjectType.TO_CLIENT_CONTACT_LIST),

    ([JSONObjectType.TO_SERVER_ADD_CONTACT, 'add_contact', datetime.time(), 'Vasya'],
     JSONObjectType.TO_SERVER_ADD_CONTACT),

    ([JSONObjectType.TO_SERVER_DEL_CONTACT, 'del_contact', datetime.time(), 'Vasya'],
     JSONObjectType.TO_SERVER_DEL_CONTACT),

    ([JSONObjectType.TO_CLIENT_INFO, '200', 'OK'],
     JSONObjectType.TO_CLIENT_INFO),

    ([JSONObjectType.TO_CLIENT_ERROR, '404', 'Not Found!'],
     JSONObjectType.TO_CLIENT_ERROR),

    ([JSONObjectType.TO_CLIENT_QUANTITY, '200', '5'],
     JSONObjectType.TO_CLIENT_QUANTITY),

    ([JSONObjectType.TO_SERVER_GET_MSGS, datetime.time(), 'Dreqn1te'],
     JSONObjectType.TO_SERVER_GET_MSGS)
])
def param_test_create_jim_object(request):
    """
    Фикстура для функции test_create_jim_object.
    @param request: request-объект.
    @return: пара (входное значение (List[String]); ожидаемый результат (Boolean)).
    """
    return request.param


def test_create_jim_object(param_test_create_jim_object):
    """
    Тест-функция для create_jim_object функции.
    @param param_test_create_jim_object: ссылка на фикстуру с данными для тестирования.
    @return: -
    """
    input_list, expected_output = param_test_create_jim_object

    try:
        jim_object = JIMManager.create_jim_object(*input_list)
    except UnknownJSONObjectType:
        result = JSONObjectType.UNKNOWN_JSON_OBJECT_TYPE
    else:
        jim_dict = jim_object.to_dict()
        result = JIMManager.determine_jim_msg_type(jim_dict)

    # print()
    # print('-' * 79)
    # input_list_str = ' '.join([str(item) for item in input_list])
    # print('На входе: {0}\nНа выходе: {1}\nОжидалось: {2}'.format(input_list_str, result, expected_output))
    # print('-' * 79)
    assert expected_output == result
