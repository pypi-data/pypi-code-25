"""
Model for Backlog user
"""

from . import BacklogBase


class User(BacklogBase):
    """
    Representing Backlog user
    """
    _endpoint = 'users'
    _crud_func = ('all', 'get', 'create', 'update', 'delete')

    def __init__(self, client):
        super().__init__(client)
        self._attr = (
            ('id', 'id'),
            ('user_id', 'userId'),
            ('name', 'name'),
            ('role_type', 'roleType'),
            ('lang', 'lang'),
            ('mail_address', 'mailAddress')
        )

    def get_watchings(self, id_=None):
        """
        Get user watching issues
        """
        if self.id is not None:
            id_ = self.id
        res = self.client.fetch_json(uri_path=f'users/{id_}/watchings')
        for x in res:
            x['user_id'] = self.id
        return [Watching(self.client).from_json(r) for r in res]

    def get_icon(self, id_=None):
        """
        Get user icon
        """
        if self.id is not None:
            id_ = self.id
        self.client.fetch_json(uri_path=f'users/{id_}/icon')
        return self

    def get_activities(self, id_=None, params=None):
        """
        Get user activities
        """
        if params is None:
            params = {}
        if self.id is not None:
            id_ = self.id
        return self.client.fetch_json(uri_path=f'users/{id_}/activities', query_params=params)

    def get_stars(self, id_=None, params=None):
        """
        Get user stars
        """
        from . import Star
        if params is None:
            params = {}
        if self.id is not None:
            id_ = self.id
        res = self.client.fetch_json(uri_path=f'users/{id_}/stars', query_params=params)
        return [Star(self.client).from_json(r) for r in res]

    def get_starts_count(self, id_=None, params=None):
        """
        Get star number user get
        """
        if params is None:
            params = {}
        if self.id is not None:
            id_ = self.id
        res = self.client.fetch_json(uri_path=f'users/{id_}/stars/count', query_params=params)
        return res['count']


class Watching(BacklogBase):
    """
    Representing Backlog user watching
    """

    def __init__(self, client):
        super().__init__(client)
        self.user_id = None
        self._attr = (
            ('id', 'id'),
            ('resource_already_read', 'resourceAlreadyRead'),
            ('note', 'note'),
            ('type', 'type'),
            ('_issue', 'issue'),
            ('last_content_updated', 'lastContentUpdated'),
            ('created', 'created'),
            ('updated', 'updated'),
            ('user_id', 'user_id'),
        )

    def from_json(self, response):
        from . import Issue
        res = super().from_json(response)
        setattr(self, 'endpoint', f'users/{self.user_id}/watchings')
        setattr(self, 'issue', Issue(self.client).from_json(res['_issue']))
        return self
