"""
Base class for Backlog all object
"""

from .. import exceptions


class BacklogBase:
    """
    Base class is identified by id and class name
    """
    _endpoint = None
    _crud_func = ('all', 'get', 'filter', 'create', 'update', 'delete')

    def __init__(self, client, id_=None):
        self.client = client
        self.id = id_
        self.name = None
        self._attr = None
        if self._crud_func is not None:
            for func_name in self._crud_func:
                setattr(self, func_name, getattr(self, '_' + func_name))

    def __repr__(self):
        return f'<{self.__class__.__name__}:{self.name}>'

    def __hash__(self):
        return hash(type(self).__name__) ^ hash(self.id)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return hash(self) == hash(other)
        raise NotImplementedError

    @property
    def url(self):
        if self.id:
            return f'{self.client.model_endpoint}{self._endpoint}/{self.id}'
        return f'{self.client.model_endpoint}{self._endpoint}'

    def from_json(self, response):
        """
        Create the Object by json response
        :param dict response: dict type object
        :return Space space: self
        """
        if not isinstance(response, dict):
            return None
        for key, res in self._attr:
            setattr(self, key, response.get(res, None))
        return self

    def _all(self):
        """
        Get all object
        """
        res = self.client.fetch_json(self._endpoint, method='GET')
        return [self.__class__(self.client).from_json(x) for x in res]

    def _get(self, id_=None):
        """
        Get one object
        """
        if self.id is not None:
            id_ = self.id
        res = self.client.fetch_json(f'{self._endpoint}/{id_}', method='GET')
        return self.__class__(self.client).from_json(res)

    def _filter(self, **params):
        """
        Get filtering object
        :return:
        """
        res = self.client.fetch_json(self._endpoint, method='GET', query_params=params)
        return [self.__class__(self.client).from_json(x) for x in res]

    def _create(self, **params):
        """
        Create new object
        """
        res = self.client.fetch_json(self._endpoint, method='POST', post_params=params)
        return self.__class__(self.client).from_json(res)

    def _update(self, id_=None, **params):
        """
        Update the object
        """
        if self.id is not None:
            id_ = self.id
        res = self.client.fetch_json(f'{self._endpoint}/{id_}', method='POST', post_params=params)
        return self.__class__(self.client).from_json(res)

    def _delete(self, id_=None):
        if self.id is not None:
            id_ = self.id
        res = self.client.fetch_json(f'{self._endpoint}/{id_}', method='DELETE')
        return self.__class__(self.client).from_json(res)

