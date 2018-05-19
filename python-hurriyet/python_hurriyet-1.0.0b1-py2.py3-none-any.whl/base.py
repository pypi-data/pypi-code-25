from datetime import datetime

from hurriyet.client import Client
from hurriyet.models import Column as ColumnModel


class BaseClient(Client):

    def __init__(self, **kwargs):
        super(BaseClient, self).__init__(**kwargs)
        self.model_class = None
        self.base_url = None

    def all(self, item_id=None, modified_date=None, path=None, top=None, skip=None, **kwargs):
        filter_data = None
        if item_id:
            filter_data = "Id eq '%s'" % item_id

        if modified_date:
            modified_date = datetime.strftime(modified_date, "%Y-%m-%dT%H:%M:%SZ")
            data = "ModifiedDate ge Datetime'%s'" % modified_date
            if filter_data:
                filter_data += ' and %s' % data
            else:
                filter_data = data

        if path:
            data = "Path eq '%s'" % path
            if filter_data:
                filter_data += ' and %s' % data
            else:
                filter_data = data

        params = {"$filter": filter_data, "$top": top, "$skip": skip}
        url = self.base_url
        result = self._get(url, params=params)
        return self.model_class.parse_list(result)

    def get(self, item_id):
        url = "%s/%s" % (self.base_url, item_id)
        result = self._get(url)
        return self.model_class.parse(result)
