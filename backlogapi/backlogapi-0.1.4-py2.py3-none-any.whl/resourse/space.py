"""
Model for Backlog Space
"""

from .base import BacklogBase
from .. import utilities


class Space(BacklogBase):
    """
    Representing a Backlog space.
    """

    _endpoint = 'space'
    _crud_func = None

    def __init__(self, client):
        super().__init__(client)
        self._attr = (
            ('id', 'spaceKey'),
            ('space_key', 'spaceKey'),
            ('name', 'name'),
            ('owner_id', 'ownerId'),
            ('lang', 'lang'),
            ('timezone', 'timezone'),
            ('report_send_time', 'reportSendTime'),
            ('text_formatting_rule', 'textFormattingRule'),
            ('created', 'created'),
            ('updated', 'updated'),
        )

    def get_activities(self, params=None):
        """
        Get Backlog activities
        :param dict params: Optional parameters used for getting activities
        """
        if params is None:
            params = {}
        return self.client.fetch_json(uri_path='space/activities', query_params=params)

    def get_icon(self):
        """
        Get space icon image file
        """
        self.client.fetch_json(uri_path=f'{self._endpoint}/image')
        return self

    def get_notification(self):
        """
        Get space notification
        """
        return self.client.fetch_json(uri_path=f'{self._endpoint}/notification')

    @utilities.protect((1,))
    def update_notification(self):
        """
        Update space notification
        """
        return self.client.fetch_json(uri_path=f'{self._endpoint}/notification', method='PUT')

    @utilities.protect((1,))
    def get_disk_usage(self):
        """
        Representing Backlog disk usage for space
        """
        return self.client.fetch_json(uri_path='space/diskUsage')

    @utilities.protect((1, 2, 3, 4))
    def create_attachment(self, files):
        """
        Update attachment file to space
        :param file files: file objects
        """
        return self.client.fetch_json(uri_path='space/attachment', method='POST', files=files)

    def get(self):
        """
        Get one object
        """
        res = self.client.fetch_json(self._endpoint, method='GET')
        return Space(self.client).from_json(res)
