"""
Model for shared file in the projects
"""

from .base import BacklogBase
from .user import User
from .. import utilities


class SharedFile(BacklogBase):
    """
    Representing Backlog shared file
    """

    def __init__(self, client):
        super().__init__(client)
        self.project_id = None
        self.path = None
        self.created_user = None
        self.updated_user = None
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
            ('project_id', 'project_id'),
        )

    def from_json(self, response):
        """
        Create the issue type and set endpoint
        """
        super().from_json(response=response)
        setattr(self, 'endpoint', f'projects/{self.project_id}/files/metadata/{self.path}')
        if hasattr(self, '_created_user') or hasattr(self, '_updated_user'):
            self.created_user = User(self).from_json(self._created_user)
            self.updated_user = User(self).from_json(self._updated_user)
        return self

    def download(self):
        """
        Download shared file the project
        """
        self.client.fetch_json(uri_path=f'projects/{self.project_id}/files/{self.id}')
        return self
