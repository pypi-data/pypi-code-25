"""
Model for Backlog webhook
"""


from . import BacklogBase, User


class Webhook(BacklogBase):
    """
    Representing Project Webhook
    """
    def __init__(self, client):
        super().__init__(client)
        self.project_id = None
        self.created_user = None
        self.updated_user = None
        self._attr = (
            ('id', 'id'),
            ('name', 'name'),
            ('description', 'description'),
            ('hook_url', 'hookUrl'),
            ('all_event', 'allEvent'),
            ('activity_type_ids', 'activityTypeIds'),
            ('_created_user', 'createdUser'),
            ('created', 'created'),
            ('_updated_user', 'updatedUser'),
            ('updated', 'updated'),
            ('project_id', 'project_id'),
        )

    def from_json(self, response):
        """
        Create the webhook object and set endpoint
        """
        super().from_json(response=response)
        setattr(self, 'endpoint', f'projects/{self.project_id}/versions')
        if hasattr(self, '_created_user') or hasattr(self, '_updated_user'):
            self.created_user = User(self).from_json(self._created_user)
            self.updated_user = User(self).from_json(self._updated_user)
        return self
