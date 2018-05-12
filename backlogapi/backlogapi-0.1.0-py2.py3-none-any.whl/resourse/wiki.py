"""
Model for Backlog projects
"""

from .base import BacklogBase
from .user import User
from .star import Star
from .. import utilities


class Wiki(BacklogBase):
    """
    Representing issue
    """

    endpoint = 'wikis'

    def __init__(self, client):
        super().__init__(client)
        self.issue_type = None
        self.created_user = None
        self.updated_user = None
        self._attr = (
            ('id', 'id'),
            ('project_id', 'projectId'),
            ('name', 'name'),
            ('tags', 'tags'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('_updated_user', 'updatedUser'),
            ('updated', 'updated'),
        )

    @property
    def count(self, project_id_or_key=None):
        """
        Get wiki page counts
        :return:
        """
        if hasattr(self, 'project_id'):
            res = self.client.fetch_json(uri_path='wikiss/count', query_params={'projectIdOrKey': self.project_id})
        else:
            res = self.client.fetch_json(uri_path='wikiss/count', query_params={'projectIdOrKey': project_id_or_key})
        return res['count']

    def tags(self, project_id_or_key):
        """
        Get wiki tags  for the project
        """
        if hasattr(self, 'project_id'):
            res = self.client.fetch_json(uri_path=f'wikis/tags', query_params={'projectIdOrKey': self.project_id})
        else:
            res = self.client.fetch_json(uri_path=f'wikis/tags', query_params={'projectIdOrKey': project_id_or_key})
        return [WikiTags(self.client).from_json(i) for i in res]

    @property
    def attachments(self):
        """
        Get issue attachments fields for the project
        """
        res = self.client.fetch_json(uri_path=f'wikis/{self.id}/attachments')
        return [WikiAttachment(self.client).from_json(i) for i in res]

    def link_shared_file(self, file_id):
        """
        Link the issue and shared file
        """
        res = self.client.fetch_json(uri_path=f'wikis/{self.id}/sharedFiles',
                                     method='POST', post_params={'fileId': file_id})
        return WikiSharedFile(self).from_json(res)

    def history(self, wiki_id):
        """
        Get wiki history
        """
        if self.id is not None:
            res = self.client.fetch_json(uri_path=f'wikis/{self.id}/history')
        else:
            res = self.client.fetch_json(uri_path=f'wikis/{wiki_id}/history')
        return res

    def stars(self, wiki_id):
        """
        Get wiki stars
        """
        if self.id is not None:
            res = self.client.fetch_json(uri_path=f'wikis/{self.id}/stars')
        else:
            res = self.client.fetch_json(uri_path=f'wikis/{wiki_id}/stars')
        return [Star(self.client).from_json(r) for r in res]

    def from_json(self, response):
        res = super().from_json(response)
        setattr(self, 'created_user', User(self.client).from_json(res['_created_user']))
        setattr(self, 'updated_user', User(self.client).from_json(res['_updated_user']))
        return self


class WikiTags(BacklogBase):
    """
    Representing wiki tags
    """

    def __init__(self, client):
        super().__init__(client)
        self.issue_id = None
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
        )


class WikiAttachment(BacklogBase):
    """
    Representing wiki attachment
    """

    def __init__(self, client):
        super().__init__(client)
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
            ('size', 'size'),
        )

    def from_json(self, response):
        super().from_json(response)
        setattr(self, 'endpoint', f'wikis/{self.id}/attachments')
        return self


class WikiSharedFile(BacklogBase):
    """
    Representing wiki shared file
    """

    def __init__(self, client):
        super().__init__(client)
        self.wiki_id = None
        self._attr = (
            ('id', 'id'),
            ('type', 'type'),
            ('dir', 'dir'),
            ('name', 'name'),
            ('size', 'size'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('_updated_user', 'updatedUser'),
            ('updated', 'updated'),
            ('wiki_id', 'wiki_id'),
        )

    def from_json(self, response):
        res = super().from_json(response)
        setattr(self, 'endpoint', f'wikis/{self.wiki_id}/sharedFiles')
        setattr(self, 'created_user', User(self.client).from_json(res['_created_user']))
        setattr(self, 'updated_user', User(self.client).from_json(res['_updated_user']))
        return self

    def download(self):
        """
        Download shared file the issue
        """
        self.client.fetch_json(uri_path=f'wikis/{self.wiki_id}/files/{self.id}')
        return self

    def link_issue(self, wiki_id):
        """
        Link issue and the shared file
        """
        res = self.client.fetch_json(uri_path=f'issues/{wiki_id}/sharedFiles',
                                     method='POST', post_params={'fileId': self.id})
        return WikiSharedFile(self.client).from_json(res)
