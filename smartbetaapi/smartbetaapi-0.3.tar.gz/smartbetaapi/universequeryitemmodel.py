import datetime


class UniverseQueryItemModel:
    def __init__(self, query_items: []=None, entity_ids: []=None, active_date: datetime = datetime.date(9999, 12, 31)):
        self._entity_ids = []
        self._entity_ids = entity_ids
        self._query_items = query_items
        self._active_date = active_date
