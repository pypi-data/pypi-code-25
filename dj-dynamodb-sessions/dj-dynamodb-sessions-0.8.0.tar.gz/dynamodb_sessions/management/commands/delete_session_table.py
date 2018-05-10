from django.core.management import BaseCommand
from dynamodb_sessions.backends.dynamodb import (
    dynamodb_connection_factory, TABLE_NAME
)
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'delete session table if does not exist'

    def handle(self, *args, **options):
        connection = dynamodb_connection_factory(low_level=True)
        try:
            connection.delete_table(
                TableName=TABLE_NAME
            )
        except ClientError as e:
            if e.response['Error']['Code'] != \
                    'ResourceNotFoundException':
                raise e
        self.stdout.write("{0} dynamble table  deleted".format(TABLE_NAME))



