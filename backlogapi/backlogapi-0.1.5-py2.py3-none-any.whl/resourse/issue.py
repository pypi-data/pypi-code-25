"""
Model for Backlog projects
"""

from .base import BacklogBase
from .project import IssueType, Version, Category
from .shared_file import SharedFile
from .star import Star
from .. import utilities


class Issue(BacklogBase):
    """
    Representing issue
    """

    _endpoint = 'issues'

    def __init__(self, client, id_=None):
        super().__init__(client, id_)
        self.issue_type = None
        self.created_user = None
        self.updated_user = None
        self._attr = (
            ('id', 'id'),
            ('project_id', 'projectId'),
            ('issue_key', 'issueKey'),
            ('key_id', 'keyId'),
            ('_issue_type', 'issueType'),
            ('summary', 'summary'),
            ('description', 'description'),
            ('resolutions', 'resolutions'),
            ('_priority', 'priority'),
            ('_status', 'status'),
            ('_assignee', 'assignee'),
            ('_category', 'category'),
            ('_versions', 'versions'),
            ('_milestone', 'milestone'),
            ('start_date', 'startDate'),
            ('due_date', 'dueDate'),
            ('estimated_hours', 'estimatedHours'),
            ('actual_hours', 'actualHours'),
            ('parent_issue_id', 'parentIssueId'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('_updated_user', 'updatedUser'),
            ('updated', 'updated'),
            ('custom_fields', 'customFields'),
            ('_attachments', 'attachments'),
            ('_shared_files', 'sharedFiles'),
            ('_stars', 'stars'),
        )

    def get_count(self, **params):
        """
        Get issue counts
        :return:
        """
        res = self.client.fetch_json(uri_path='issues/count', query_params=params)
        return res['count']

    def get_comments(self, id_=None):
        """
        Get issue comments  for the project
        """
        if self.id is not None:
            res = self.client.fetch_json(uri_path=f'issues/{self.id}/comments')
        else:
            res = self.client.fetch_json(uri_path=f'issues/{id_}/comments')
        for x in res:
            x['issue_id'] = self.id
        return [IssueComment(self.client).from_json(i) for i in res]

    def get_attachments(self, id_=None):
        """
        Get issue attachments fields for the project
        """
        if self.id is not None:
            res = self.client.fetch_json(uri_path=f'issues/{self.id}/attachments')
        else:
            res = self.client.fetch_json(uri_path=f'issues/{id_}/attachments')
        for x in res:
            x['issue_id'] = self.id
        return [IssueAttachment(self.client).from_json(i) for i in res]

    def get_shared_files(self, id_=None):
        """
        Get issue shared fields for the project
        """
        if self.id is not None:
            res = self.client.fetch_json(uri_path=f'issues/{self.id}/sharedFiles')
        else:
            res = self.client.fetch_json(uri_path=f'issues/{id_}/sharedFiles')
        for x in res:
            x['issue_id'] = self.id
        return [IssueAttachment(self.client).from_json(i) for i in res]

    def link_shared_file(self, file_id):
        """
        Link the issue and shared file
        """
        res = self.client.fetch_json(uri_path=f'issues/{self.id}/sharedFiles',
                                     method='POST', post_params={'fileId': file_id})
        return IssueSharedFile(self).from_json(res)

    def from_json(self, response):
        from . import User
        res = super().from_json(response)
        self.name = res.issue_key
        private_attr = [attrs[0] for attrs in self._attr if attrs[0].startswith('_')]
        objs = [IssueType, Priority, Status, User, Category, Version,
                Version, User, User, IssueAttachment, SharedFile, Star]
        for attr, obj in zip(private_attr, objs):
            api_values = getattr(res, attr)
            if isinstance(api_values, list):
                setattr(self, attr[1:], [obj(self.client).from_json(value) for value in api_values])
            else:
                setattr(self, attr[1:], obj(self.client).from_json(api_values))
        return self


class Status(BacklogBase):
    """
    Representing issue status
    """
    _endpoint = 'statuses'

    def __init__(self, client):
        super().__init__(client)
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
        )


class Resolution(BacklogBase):
    """
    Representing issue resolution
    """
    _endpoint = 'resolutions'

    def __init__(self, client):
        super().__init__(client)
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
        )


class Priority(BacklogBase):
    """
    Representing issue priority
    """
    _endpoint = 'resolutions'

    def __init__(self, client):
        super().__init__(client)
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
        )


class IssueComment(BacklogBase):
    """
    Representing issue comment
    """

    def __init__(self, client):
        super().__init__(client)
        self.issue_id = None
        self._attr = (
            ('id', 'id'),
            ('content', 'content'),
            ('change_log', 'changeLog'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('updated', 'updated'),
            ('stars', 'stars'),
            ('notifications', 'notifications'),
            ('issue_id', 'issue_id'),
            ('name', 'id'),
        )

    def from_json(self, response):
        from . import User
        res = super().from_json(response)
        setattr(self, '_endpoint', f'issues/{self.issue_id}/comments')
        setattr(self, 'created_user', User(self.client).from_json(res._created_user))
        return self

    @property
    def count(self, **params):
        """
        Get issue comments counts
        :return:
        """
        res = self.client.fetch_json(uri_path=f'issues/{self.id}/comments/count', query_params=params)
        return res['count']


class IssueAttachment(BacklogBase):
    """
    Representing issue attachment
    """

    def __init__(self, client):
        super().__init__(client)
        self.issue_id = None
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
            ('size', 'size'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('issue_id', 'issue_id'),
        )

    def from_json(self, response):
        from . import User
        res = super().from_json(response)
        setattr(self, '_endpoint', f'issues/{self.issue_id}/attachments')
        if hasattr(res, '_created_user'):
            setattr(self, 'created_user', User(self.client).from_json(res._created_user))
        return self


class IssueSharedFile(BacklogBase):
    """
    Representing issue shared file
    """

    def __init__(self, client):
        super().__init__(client)
        self.issue_id = None
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
            ('issue_id', 'issue_id'),
        )

    def from_json(self, response):
        from . import User
        res = super().from_json(response)
        setattr(self, '_endpoint', f'issues/{self.issue_id}/sharedFiles')
        setattr(self, 'created_user', User(self.client).from_json(res._created_user))
        setattr(self, 'updated_user', User(self.client).from_json(res._updated_user))
        return self

    def download(self):
        """
        Download shared file the issue
        """
        self.client.fetch_json(uri_path=f'projects/{self.issue_id}/files/{self.id}')
        return self

    def link_issue(self, issue_id):
        """
        Link issue and the shared file
        """
        res = self.client.fetch_json(uri_path=f'issues/{issue_id}/sharedFiles',
                                     method='POST', post_params={'fileId': self.id})
        return IssueSharedFile(self.client).from_json(res)
