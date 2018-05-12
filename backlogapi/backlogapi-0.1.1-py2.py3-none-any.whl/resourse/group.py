"""
Model for Backlog group
"""
from typing import List

from . import BacklogBase
from .. import utilities


class Group(BacklogBase):
    """
    Representing Backlog user
    """

    def __init__(self, client):
        super().__init__(client)
        self.members = None
        self.created_user = None
        self.updated_user = None
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
            ('_members', 'members'),
            ('display_order', 'displayOrder'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('_updated_user', 'updatedUser'),
            ('updated', 'updated'),
        )
    
    def from_json(self, response):
        from . import User
        super().from_json(response)
        if hasattr(self, '_members'):
            self.members = [User(self).from_json(u) for u in self._members]
            self.created_user = User(self).from_json(self._created_user)
            self.updated_user = User(self).from_json(self._updated_user)
        return self

