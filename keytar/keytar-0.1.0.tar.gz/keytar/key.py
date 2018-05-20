"""Key class"""

class Key:
    """Wrapper around keys, let's us be have a more predictable input"""
    __primary_key = False
    __primary_value = False

    def __init__(self, value, key_name="primary"):
        """Init with most primary key, provide a name if planning
        to use DynamoDb or MongoDb.

        @TODO add support for multiple keys"""
        self.__primary_key = key_name
        self.__primary_value = value

    def get_primary_key_name(self):
        return self.__primary_key

    def get_primary_key_value(self):
        return self.__primary_value
