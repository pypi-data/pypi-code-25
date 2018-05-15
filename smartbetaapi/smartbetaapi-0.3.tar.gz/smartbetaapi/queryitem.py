from .enums import QueryItemType


class QueryItem:
    def __init__(self, 
                item_type: QueryItemType, 
            query_item_key, 
            data_provider_name, 
            data_feed_name):
        self.item_type = item_type.name
        self.query_item_key = query_item_key
        self.data_provider_name = data_provider_name
        self.data_feed_name = data_feed_name


