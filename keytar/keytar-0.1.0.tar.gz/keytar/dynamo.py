"""Interface for AWS DynamoDb

https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Python.html
"""

class Dynamo:
    """This wraps a provided boto3 dyanamo db object for internal use"""
    database = False
    def __init__(self, db):
        """Provide a valid dynamo boto3 dynamo db object"""
        self.database = db

    def get(self, table, key):
        """Keys can be dictionaires"""
        table = self.__get_table(table)
        return table.get_item(Key=make_key(key))['Item']

    def set(self, table, key, item):
        """Set an item in a table, key values override item"""
        key = make_key(key)
        item = {**item, **key}
        table = self.__get_table(table)
        return table.put_item(Item=item)

    def __get_table(self, table):
        return self.database.Table(table)

def make_key(key):
    """Wrapper around getting keys"""
    name = key.get_primary_key_name()
    value = key.get_primary_key_value()
    return {name: value}
