# -*- coding: utf-8 -*-

"""Uploads a file to S3"""

import boto3
import datetime

##########################################
##########################################
##########################################
##########################################


def s3_upload(file_name, aws_bucket_name, aws_file_path, aws_region_name='us-east-1', aws_access_key_id=None,
              aws_secret_access_key=None):

    ##########################################
    # connects to S3

    print(str(datetime.datetime.now())[:19] + ': Connecting to S3.')

    if aws_access_key_id and aws_secret_access_key:

        s3 = boto3.resource(service_name='s3',
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name=aws_region_name)

    else:
        s3 = boto3.resource(service_name='s3',
                            region_name=aws_region_name)

    print(str(datetime.datetime.now())[:19] + ': Connected to S3.')

    ##########################################
    # uploads to S3

    print(str(datetime.datetime.now())[:19] + ': Uploading to S3.')

    with open(file_name, 'rb') as f:
        s3.Bucket(aws_bucket_name).put_object(Key=(aws_file_path + file_name), Body=f)
        f.close()

    print(str(datetime.datetime.now())[:19] + ': Uploaded to S3.')

    ##########################################
