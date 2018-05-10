from django.core.management import BaseCommand
from django.core.management import CommandError
from django.core.management import call_command
from dynamodb_sessions.backends.dynamodb import (
    dynamodb_connection_factory, TABLE_NAME,
    READ_CAPACITY_UNITS, WRITE_CAPACITY_UNITS
)
import time
from botocore.exceptions import ClientError


class Command(BaseCommand):
    help = 'creates session table if does not exist'

    def handle(self, *args, **options):
        connection = dynamodb_connection_factory(low_level=True)

        # check session table exists
        try:
            connection.describe_table(
                TableName=TABLE_NAME
            )
            self.stdout.write("session table already exist\n")
            return
        except ClientError as e:
            if e.response['Error']['Code'] == \
                    'ResourceNotFoundException':
                pass
            else:
                raise e

        table_status = None

        connection.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[
                {
                    'AttributeName': 'session_key',
                    'AttributeType': 'S'
                }
            ],
            KeySchema=[
                {
                    'AttributeName': 'session_key',
                    'KeyType': 'HASH'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': READ_CAPACITY_UNITS,
                'WriteCapacityUnits': WRITE_CAPACITY_UNITS
            },
        )

        # wait for table to be active
        for i in range(20):
            response = connection.describe_table(
                TableName=TABLE_NAME
            )
            if response.get('Table', {}).get('TableStatus') == 'ACTIVE':
                table_status = True
                break
            time.sleep(1)

        if table_status:
            self.stdout.write("session table created\n")
        else:
            self.stdout.write("session table created but not active\n")




