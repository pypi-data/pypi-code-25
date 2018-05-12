"""
Model for Backlog notification
"""


from . import BacklogBase, Issue, IssueComment


class Notification(BacklogBase):
    """
    Representing Project star
    """

    endpoint = 'notifications'

    def __init__(self, client):
        super().__init__(client)
        self._attr = (
            ('id', 'id'),
            ('already_read', 'alreadyRead'),
            ('reason', 'reason'),
            ('resource_already_read', 'resourceAlreadyRead'),
            ('_project', 'project'),
            ('_issue', 'issue'),
            ('_comment', 'comment'),
            ('_pull_request', 'pullRequest'),
            ('_pull_request_comment', 'pull_request_comment'),
            ('_sender', 'sender'),
            ('created', 'created')
        )

    def from_json(self, response):
        from . import User, Project
        res = super().from_json(response)
        setattr(self, 'project', Project(self.client).from_json(res._project))
        setattr(self, 'issue', Issue(self.client).from_json(res._issue))
        setattr(self, 'comment', IssueComment(self.client).from_json(res._comment))
        setattr(self, 'sender', User(self.client).from_json(res._sender))
        return self

    def count(self, **params):
        """
        Get notification numbers
        """
        res = self.client.fetch_json(uri_path=f'{self.endpoint}/count', query_params=params)
        return res['count']

    def reset(self):
        """
        Reset my notification number
        """
        res = self.client.fetch_json(uri_path=f'{self.endpoint}/markAsRead', method='POST')
        return res['count']

    def mark_read(self, notification_id):
        """
        Mark read flag
        """
        if self.id is not None:
            self.client.fetch_json(uri_path=f'{self.endpoint}/{self.id}/markAsRead')
        else:
            self.client.fetch_json(uri_path=f'{self.endpoint}/{notification_id}/markAsRead')
        return None

