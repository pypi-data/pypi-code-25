from collections import OrderedDict

from rinzler import Rinzler


class OnyxErpService(object):
    """
    OnyxErpService
    """
    __api_root = str()
    __app: Rinzler = None

    def get_api_root(self):
        """

        :return: str
        """
        return self.__api_root

    def set_api_root(self, api_root):
        """

        :param api_root:
        :return:
        """
        self.__api_root = api_root
        return self

    def get_app(self) -> Rinzler:
        """
        Retorna o valor da propriedade __app
        :return: Rinzler
        """
        return self.__app

    def set_app(self, app: Rinzler):
        """
        Seta o valor da propriedade __app
        :param app:
        :return: OnyxErpService
        """
        self.__app = app
        return self

    def deserialize_cached_model(self, key: str(), cached_data: str()) -> object:
        """
        Desserializa o cached model
        :param key: str
        :param cached_data: str
        :return: object
        """
        try:
            for model in cached_data:
                retorno = OrderedDict()
                retorno[key] = model['pk']
                retorno.update(model['fields'])
                return retorno
        except Exception:
            self.__app.log.warning(
                "Falha ao deserializar arquivo de cache em model. Data: %s" % str(cached_data),
                exc_info=True
            )
            return False
