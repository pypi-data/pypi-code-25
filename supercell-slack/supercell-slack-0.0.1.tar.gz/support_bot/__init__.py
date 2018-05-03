#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import json
from botocore.exceptions import ClientError


def run_lambda(channel,message):
    try:
        lambda_session = boto3.session.Session(profile_name='267511835443-GR_GG_COF_AWS_CoreAdmin', region_name='us-east-1')
        lambda_client = lambda_session.client('lambda')

        lambda_function_name = 'supercell_slack_bot'

        print(' -- Lambda function -{0}- invoked, waiting for completion'.format(lambda_function_name))

        payload = json.dumps({
        "channel" : channel,
        "message" : message,
        })

        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType="RequestResponse",
            Payload=payload,
            LogType="Tail"
            )
    except ClientError as tokens:
        print('Looks like either you forgot to run the tokens script or they just expired...Sorry!')
