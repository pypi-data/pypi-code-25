import hashlib
import json
import os
from collections import OrderedDict
from typing import Dict

from rinzler import Rinzler
from rinzler.exceptions.invalid_input_exception import InvalidInputException
from onyxerp.core.services.generator import simpleflake


class BaseService(object):
    """
    BaseService
    """
    __app: Rinzler = None
    __payload = dict()
    __jwt_data = dict()
    __jwt = str()
    uupfid = object()

    def __init__(self, app: Rinzler, param=None):
        self.__app = app

    def set_payload(self, payload: str(), headers: Dict[str, str]=None):
        """
        Decodifica o body payload recebida e se for um JSON válido seta na variável self.__payload, senão:
        :raises: InvalidInputException Caso o payload não seja um JSON válido.
        :param payload: str Request body JSON
        :param headers: Dict[str, str] Headers da requisição, informado deve conter a posição HTTP_CONTENT_CHECKSUM para
        verificação de checksum.
        :return: self
        """
        try:
            if headers:
                self.valida_payload_checksum(payload, headers)
            self.set_payload_obj(json.loads(payload, object_pairs_hook=OrderedDict))
        except Exception:
            raise InvalidInputException("JSON inválido ou mal-formatado.")
        return self

    def valida_payload_checksum(self, payload_raw: bytes, headers: Dict[str, str]):
        """
        Verifica se o conteúdo recebido está de acordo com o checksum calculado na hora do envio, senão:
        :raises: InvalidInputException Se os checksums não baterem
        :param payload_raw: bytes
        :param headers: Dict[str, str]
        :return: self
        """
        if 'HTTP_CONTENT_CHECKSUM' not in headers:
            raise InvalidInputException("Header Content-Checksum omitido: %s" % str(headers))

        client_checksum = headers['HTTP_CONTENT_CHECKSUM']
        actual_checksum = hashlib.sha1(payload_raw).hexdigest()

        if client_checksum != actual_checksum:
            raise InvalidInputException("Checksum failed")

        return self

    def set_payload_obj(self, payload: dict()):
        """
        Seta um payload já decodificado na variável self.__payload, sem nenhuma validação adicional.
        :param payload: dict
        :return: self
        """
        self.__payload = payload
        return self

    def get_payload(self):
        """
        Retorna o valor da variável self.__payload
        :return: dict
        """
        return self.__payload

    def set_jwt_data(self, jwt_data: dict()):
        """
        Set os dados da variável self.__jwt_data.
        :param jwt_data: dict
        :return: self
        """
        self.__jwt_data = jwt_data
        return self

    def get_jwt_data(self):
        """
        Retorna os dados da variável self.__jwt_data
        :return: dict
        """
        return self.__jwt_data

    def set_jwt(self, token: str()):
        """
        Seta o valor da variável self.__jwt
        :param token: str
        :return: self
        """
        self.__jwt = token
        self.set_jwt_data(self.__app.auth_data['data']['data'])
        return self

    def get_jwt(self):
        """

        :return:
        """
        return self.__jwt

    def set_uupfid(self, uupfid: object):
        """
        Seta o valor da variável self.__uupfid
        :param uupfid: objct
        :return: self
        """
        self.uupfid = uupfid
        return self

    @staticmethod
    def get_uniqid(bytes=15) -> str:
        """
        Gera e retorna uma snowflake id
        :param bytes: int
        :return: str
        """
        return str(simpleflake(int(os.urandom(4).hex().upper(), 16)))
