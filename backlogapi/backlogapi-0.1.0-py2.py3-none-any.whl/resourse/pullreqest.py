"""
Model for Backlog repository
"""


from . import BacklogBase, Issue


class PullRequest(BacklogBase):
    """
    Representing Project pull request
    """
    def __init__(self, client):
        super().__init__(client)
        self.project_id = None
        self.repository_id = None
        self.number = None
        self.created_user = None
        self.updated_user = None
        self._attr = (
            ('id', 'id'),
            ('project_id', 'projectId'),
            ('repository_id', 'repositoryId'),
            ('number', 'number'),
            ('summary', 'summary'),
            ('description', 'description'),
            ('base', 'base'),
            ('branch', 'branch'),
            ('status', 'status'),
            ('_assignee', 'assignee'),
            ('_issue', 'issue'),
            ('base_commit', 'baseCommit'),
            ('branch_commit', 'branchCommit'),
            ('close_at', 'closeAt'),
            ('merge_at', 'mergeAt'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('_updated_user', 'updatedUser'),
            ('updated', 'updated'),
        )

    def from_json(self, response):
        """
        Create the webhook object and set endpoint
        """
        from . import User
        res = super().from_json(response=response)
        setattr(self, 'endpoint', f'projects/{self.project_id}/git/repositories/{self.id}/pullRequests')
        setattr(self, 'assignee', User(self.client).from_json(res['_assignee']))
        setattr(self, 'issue', Issue(self.client).from_json(res['_issue']))
        setattr(self, 'created_user', User(self.client).from_json(res['_created_user']))
        setattr(self, 'updated_user', User(self.client).from_json(res['_updated_user']))
        return self

    def count(self, **params):
        """
        Count the pull request
        """
        if self.id is None:
            return None
        else:
            res = self.client.fetch_json(uri_path=f'{self.endpoint}/count',
                                         query_params=params)
            return res['count']

    @property
    def comments(self):
        """
        Get pull request comments
        """
        res = self.client.fetch_json(
            uri_path=f'projects/{self.project_id}/git/repositories/'
                     f'{self.repository_id}/pullRequests/{self.id}/comments'
        )
        for x in res:
            x['project_id'] = self.project_id
            x['repository_id'] = self.repository_id
            x['number'] = self.number
        return [PullRequestComment(r) for r in res]

    @property
    def attachments(self):
        """
        Get pull request comments
        """
        res = self.client.fetch_json(
            uri_path=f'projects/{self.project_id}/git/repositories/'
                     f'{self.repository_id}/pullRequests/{self.id}/attachments'
        )
        for x in res:
            x['project_id'] = self.project_id
            x['repository_id'] = self.repository_id
            x['number'] = self.number
        return [PullRequestComment(r) for r in res]


class PullRequestComment(BacklogBase):
    """
    Representing Project pull request comment
    """
    def __init__(self, client):
        super().__init__(client)
        self.project_id = None
        self.repository_id = None
        self.number = None
        self.created_user = None
        self._attr = (
            ('id', 'id'),
            ('content', 'content'),
            ('change_log', 'changeLog'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('updated', 'updated'),
            ('stars', 'stars'),
            ('notifications', 'notifications'),
            ('project_id', 'project_id'),
            ('repository_id', 'repository_id'),
            ('number', 'number'),
        )

    def from_json(self, response):
        """
        Create the pull request comment object and set endpoint
        """
        from . import User
        res = super().from_json(response=response)
        setattr(self, 'endpoint',
                f'projects/{self.project_id}/git/repositories/{self.repository_id}/pullRequests/{self.number}/comments')
        setattr(self, 'created_user', User(self.client).from_json(res['_created_user']))
        return self

    def count(self, **params):
        """
        Count the pull request comment
        """
        if self.id is None:
            return None
        else:
            res = self.client.fetch_json(uri_path=f'{self.endpoint}/count',
                                         query_params=params)
            return res['count']


class PullRequestAttachment(BacklogBase):
    """
    Representing Project pull request attachment
    """
    def __init__(self, client):
        super().__init__(client)
        self.project_id = None
        self.repository_id = None
        self.number = None
        self.created_user = None
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
            ('size', 'size'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('project_id', 'project_id'),
            ('repository_id', 'repository_id'),
            ('number', 'number'),
        )

    def from_json(self, response):
        """
        Create the pull request attachment object and set endpoint
        """
        from . import User
        res = super().from_json(response=response)
        setattr(
            self,
            'endpoint',
            f'projects/{self.project_id}/git/repositories/{self.repository_id}/pullRequests/{self.number}/attachments'
        )
        setattr(self, 'created_user', User(self.client).from_json(res['_created_user']))
        return self

    def count(self):
        """
        Count the pull request attachment
        """
        if self.id is None:
            return None
        else:
            res = self.client.fetch_json(uri_path=f'{self.endpoint}/count')
            return res['count']

    def download(self, id_=None):
        """
        Download pull request attachment file
        """
        if self.id is not None:
            self.client.fetch_json(uri_path=f'{self.endpoint}/{self.id}')
        else:
            self.client.fetch_json(uri_path=f'{self.endpoint}/{id_}')
        return self
