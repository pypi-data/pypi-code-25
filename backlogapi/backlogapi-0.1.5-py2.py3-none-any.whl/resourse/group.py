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

    def __init__(self, client, id_=None):
        super().__init__(client, id_)
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
        res = super().from_json(response)
        setattr(self, 'members', [User(self.client).from_json(u) for u in res._members])
        setattr(self, 'created_user', [User(self.client).from_json(u) for u in res._created_user])
        setattr(self, 'updated_user', [User(self.client).from_json(u) for u in res._updated_user])
        return self

