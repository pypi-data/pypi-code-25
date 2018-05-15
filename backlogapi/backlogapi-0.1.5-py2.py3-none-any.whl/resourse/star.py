"""
Model for Backlog star
"""


from . import BacklogBase


class Star(BacklogBase):
    """
    Representing Project star
    """

    endpoint = 'stars'

    def __init__(self, client):
        super().__init__(client)
        self._attr = (
            ('id', 'id'),
            ('comment', 'comment'),
            ('url', 'url'),
            ('_presenter', 'presenter'),
            ('created', 'created'),
        )

    def from_json(self, response):
        """
        Create the webhook object and set endpoint
        """
        from . import User
        res = super().from_json(response=response)
        setattr(self, 'presenter', User(self.client).from_json(res['_presenter']))
        return self
