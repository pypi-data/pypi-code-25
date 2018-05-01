# -*- coding: utf-8 -*-

"""Sends message to SQS queue"""

import boto3
import datetime

##########################################
##########################################
##########################################
##########################################


def sqs_send(queue_url, message, aws_region_name='us-east-1', aws_access_key_id=None, aws_secret_access_key=None):

    ##########################################
    # connects to SQS

    print(str(datetime.datetime.now())[:19] + ': Connecting to SQS.')

    if aws_access_key_id and aws_secret_access_key:

        sqs = boto3.client('sqs', region_name=aws_region_name, aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key)

    else:

        sqs = boto3.client('sqs', region_name=aws_region_name)

    print(str(datetime.datetime.now())[:19] + ': Connected to SQS.')

    ##########################################
    # sends message to SQS queue

    print(str(datetime.datetime.now())[:19] + ': Sending message to queue with url -> ' + queue_url)

    response = sqs.send_message(QueueUrl=queue_url,
                                MessageBody=message
                                )

    print(str(datetime.datetime.now())[:19] + ': Message sent. The MessageId is ' + response['MessageId'] + '.')

    ##########################################

    return response
