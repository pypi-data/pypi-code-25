# -*- coding: utf-8 -*-

"""Receives messages from SQS queue"""

import boto3
import datetime

##########################################
##########################################
##########################################
##########################################


def sqs_receive(queue_url, max_messages=1, aws_region_name='us-east-1', aws_access_key_id=None,
                aws_secret_access_key=None, delete_from_queue=True):

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
    # receives messages from SQS

    print(str(datetime.datetime.now())[:19] + ': Receiving from queue with url -> ' + queue_url)

    messages = sqs.receive_message(QueueUrl=queue_url,
                                   MaxNumberOfMessages=max_messages)

    print(str(datetime.datetime.now())[:19] + ': Messages received.')

    ##########################################
    # in case the queue is empty

    if 'Messages' not in messages.keys():

        print(str(datetime.datetime.now())[:19] + ': The queue is empty.')

        return {}

    ##########################################
    # if the messages need to be deleted after being received

    if delete_from_queue:

        for message in messages['Messages']:

            print(str(datetime.datetime.now())[:19] + ': Deleting message -> ' + str(message))

            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])

            print(str(datetime.datetime.now())[:19] + ': Message deleted.')

    ##########################################

    return messages
