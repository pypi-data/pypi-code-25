"""
Model for Backlog repository
"""


from . import BacklogBase


class Repository(BacklogBase):
    """
    Representing Project Repository
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
            ('hook_url', 'hookUrl'),
            ('ssh_url', 'sshUrl'),
            ('display_order', 'displayOrder'),
            ('pushed_at', 'pushedAt'),
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
        setattr(self, 'endpoint', f'projects/{self.project_id}/git/repositories')
        setattr(self, 'created_user', User(self.client).from_json(res['_created_user']))
        setattr(self, 'updated_user', User(self.client).from_json(res['_updated_user']))
        return self
