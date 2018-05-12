"""
Model for Backlog projects
"""

from . import BacklogBase
from .. import utilities


class Project(BacklogBase):
    """
    Representing Backlog user
    """
    _endpoint = 'projects'

    def __init__(self, client):
        super().__init__(client)
        self._attr = (
            ('id', 'id'),
            ('project_key', 'projectKey'),
            ('name', 'name'),
            ('chart_enabled', 'chartEnabled'),
            ('subtasking_enabled', 'subtaskingEnabled'),
            ('project_leader_can_edit_project_leader', 'projectLeaderCanEditProjectLeader'),
            ('text_formatting_rule', 'textFormattingRule'),
            ('archived', 'archived')
        )

    def activities(self, **params):
        """
        Get the project activities
        """
        if self.id is None:
            return None
        return self.client.fetch_json(uri_path=f'projects/{self.id}/activities',
                                      query_params=params)

    def get_issues(self, params=None):
        """
        Get issue the project
        """
        if params is None:
            params = {'projectId[]': self.id}
        from . import Issue
        res = self.client.fetch_json(uri_path=f'issues', query_params=params)
        return [Issue(self.client).from_json(u) for u in res]

    @property
    def users(self):
        """
        Get user the project
        """
        from . import User
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/users')
        return [User(self.client).from_json(u) for u in res]

    def add_user(self, user_id):
        """
        Add user the project
        :param user_id:
        """
        self.client.fetch_json(uri_path=f'projects/{self.id}/users',
                               method='POST',
                               post_params={'userId': user_id})

    @utilities.protect((1,))
    def delete_user(self, user_id):
        """
        Delete user the project
        :param user_id:
        """
        self.client.fetch_json(uri_path=f'projects/{self.id}/users',
                               method='DELETE',
                               post_params={'userId': user_id})

    @property
    @utilities.protect((1,))
    def admins(self):
        """
        Get admin user the project
        """
        from . import User
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/administrator')
        return [User(self.client).from_json(u) for u in res]

    @utilities.protect((1,))
    def add_admin(self, user_id):
        """
        Add admin user the project
        :param user_id:
        """
        from . import User
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/administrator',
                                     method='POST',
                                     post_params={'userId': user_id})
        return User(self.client).from_json(res)

    @utilities.protect((1,))
    def delete_admin(self, user_id):
        """
        Delete admin user the project
        :param user_id:
        """
        from . import User
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/administrator',
                                     method='DELETE',
                                     post_params={'userId': user_id})
        return User(self.client).from_json(res)

    @property
    def issue_types(self):
        """
        Get issue type for the project
        """
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/issueTypes')
        return [IssueType(self.client).from_json(i) for i in res]

    @property
    def categories(self):
        """
        Get categories for the project
        """
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/categories')
        for x in res:
            x['project_id'] = self.id
        return [Category(self.client).from_json(i) for i in res]

    @property
    def versions(self):
        """
        Get versions for the project
        """
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/versions')
        return [Version(self.client).from_json(i) for i in res]

    @property
    def custom_fields(self):
        """
        Get custom fields for the project
        """
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/customFields')
        for x in res:
            x['project_id'] = self.id
        return [CustomField(self.client).from_json(i) for i in res]

    @property
    def shared_files(self, path='/', **params):
        """
        Get shared files for the project
        """
        from . import SharedFile
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/files/metadata/{path}',
                                     query_params=params)
        for x in res:
            x['project_id'] = self.id
        return [SharedFile(self.client).from_json(i) for i in res]

    @property
    def webhooks(self):
        """
        Get webhook for the project
        """
        from . import Webhook
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/webhooks')
        for x in res:
            x['project_id'] = self.id
        return [Webhook(self.client).from_json(i) for i in res]

    @property
    def project_group(self):
        """
        Get project group
        """
        res = self.client.fetch_json(uri_path=f'projects/{self.id}/groups')
        for x in res:
            x['project_id'] = self.id
        return [ProjectGroup(self.client).from_json(i) for i in res]


class IssueType(BacklogBase):
    """
    Representing Project Issue type
    """

    def __init__(self, client):
        super().__init__(client)
        self.project_id = None
        self._attr = (
            ('id', 'id'),
            ('project_id', 'projectId'),
            ('name', 'name'),
            ('color', 'color'),
            ('display_order', 'displayOrder'),
        )

    def from_json(self, response):
        """
        Create the issue type and set _endpoint
        """
        super().from_json(response=response)
        setattr(self, '_endpoint', f'projects/{self.project_id}/issueTypes')
        return self


class Category(BacklogBase):
    """
    Representing Project Categories
    """
    def __init__(self, client):
        super().__init__(client)
        self.project_id = None
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
            ('display_order', 'displayOrder'),
            ('project_id', 'project_id'),
        )

    def from_json(self, response):
        """
        Create the issue type and set _endpoint
        """
        super().from_json(response=response)
        setattr(self, '_endpoint', f'projects/{self.project_id}/categories')
        return self


class Version(BacklogBase):
    """
    Representing Project Version
    """
    def __init__(self, client):
        super().__init__(client)
        self.project_id = None
        self.created_user = None
        self.updated_user = None
        self._attr = (
            ('id', 'id'),
            ('project_id', 'projectId'),
            ('name', 'name'),
            ('description', 'description'),
            ('start_date', 'startDate'),
            ('release_due_date', 'releaseDueDate'),
            ('archived', 'archived'),
            ('display_order', 'displayOrder'),
        )

    def from_json(self, response):
        """
        Create the issue type and set _endpoint
        """
        super().from_json(response=response)
        setattr(self, '_endpoint', f'projects/{self.project_id}/versions')
        return self


class CustomField(BacklogBase):
    """
    Representing Project Version
    """
    def __init__(self, client):
        super().__init__(client)
        self.project_id = None
        self._attr = (
            ('id', 'id'),
            ('type_id', 'typeId'),
            ('name', 'name'),
            ('description', 'description'),
            ('required', 'required'),
            ('applicable_issue_types', 'applicableIssueTypes'),
            ('allow_add_item', 'allowAddItem'),
            ('items', 'items'),
            ('project_id', 'projectId'),
        )

    def from_json(self, response):
        """
        Create the issue type and set _endpoint
        """
        super().from_json(response=response)
        setattr(self, '_endpoint', f'projects/{self.project_id}/versions')
        return self


class ProjectGroup(BacklogBase):
    """
    Representing project group
    """
    def __init__(self, client):
        super().__init__(client)
        self.project_id = None
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
            ('_members', 'members'),
            ('display_order', 'displayOrder'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('_updated_user', 'updatedUser'),
            ('updated', 'updated'),
            ('project_id', 'projectId'),
        )

    def from_json(self, response):
        from . import User
        res = super().from_json(response)
        setattr(self, 'members', [User(self.client).from_json(member) for member in res['_members']])
        setattr(self, 'created_user', User(self.client).from_json(res['_created_user']))
        setattr(self, 'updated_user', User(self.client).from_json(res['_updated_user']))
        return self
