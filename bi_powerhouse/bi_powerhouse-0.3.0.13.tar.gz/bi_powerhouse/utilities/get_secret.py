# -*- coding: utf-8 -*-

"""Gets secret from AWS Secrets Manager"""

import boto3
from botocore.exceptions import ClientError
import json

##########################################
##########################################
##########################################
##########################################


def get_secret(secret_name, aws_region_name='us-east-1', aws_access_key_id=None, aws_secret_access_key=None):

    endpoint_url = 'https://secretsmanager.' + aws_region_name + '.amazonaws.com'

    session = boto3.session.Session()

    if aws_access_key_id and aws_secret_access_key:
        client = session.client(service_name='secretsmanager',
                                region_name=aws_region_name,
                                endpoint_url=endpoint_url,
                                aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key
                                )

    else:
        client = session.client(service_name='secretsmanager',
                                region_name=aws_region_name,
                                endpoint_url=endpoint_url
                                )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)

    else:
        # Decrypted secret using the associated KMS CMK
        # Depending on whether the secret was a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)

        else:
            binary_secret_data = get_secret_value_response['SecretBinary']
            return json.loads(binary_secret_data)
