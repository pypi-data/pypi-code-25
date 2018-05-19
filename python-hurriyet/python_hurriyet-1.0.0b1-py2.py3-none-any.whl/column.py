from hurriyet.base import BaseClient
from hurriyet.models import Column as ColumnModel


class Column(BaseClient):
    """Hurriyet column operations."""

    def __init__(self, **kwargs):
        super(Column, self).__init__(**kwargs)
        self.model_class = ColumnModel
        self.base_url = "/columns"

    def all(self, column_id=None, modified_date=None, path=None, top=None, skip=None, **kwargs):
        """
        Get list of columns.

        :return [Columns]: The Hurriyet Columns.
        """
        filter_data = None
        if column_id:
            filter_data = "Id eq '%s'" % column_id

        writer_id = kwargs.get("writer_id")
        if writer_id:
            data = "WriterId eq '%s'" % writer_id
            if filter_data:
                filter_data += ' and %s' % data
            else:
                filter_data = data

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
