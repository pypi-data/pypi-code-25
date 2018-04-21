# -*- coding: utf-8 -*-

"""Runs a query"""

from bi_powerhouse.utilities.db_connections import cursor_creator as cc
from bi_powerhouse.utilities.db_connections import individual_query_runner as iq
from bi_powerhouse.utilities.write_to_csv import write_to_csv
import pandas as pd
import boto3
import os
import datetime

##########################################
##########################################
##########################################
##########################################


def run_query(engine, query_file, host, port, username, password, database, autocommit=False, return_as='nested_list',
              include_headers=True, file_name=None, returns_rows=True, aws_access_key_id=None,
              aws_secret_access_key=None, aws_region_name=None, aws_bucket_name=None, aws_file_path=''):

    results = []

    ##########################################
    # gets the queries in the file

    print(str(datetime.datetime.now())[:19] + ': Reading query file.')

    with open(query_file) as f:
        query = f.read()
        f.close()

    print(str(datetime.datetime.now())[:19] + ': Splitting queries.')

    queries = query.split(';')

    queries = filter(None, queries)

    ##########################################
    # runs the queries

    cur = cc.create_cursor(engine, host, port, username, password, database, autocommit=autocommit)

    for query in queries:
        results = iq.run_single_query(cur, query, engine, False, returns_rows)

    ##########################################
    # closes the cursor

    print(str(datetime.datetime.now())[:19] + ': Closing cursor.')

    cur.close()

    print(str(datetime.datetime.now())[:19] + ': Cursor closed.')

    ##########################################
    # for results that need to be returned on a nested list

    if return_as == 'nested_list':

        print(str(datetime.datetime.now())[:19] + ': Returning results as nested list.')

        if include_headers:
            return results

        else:
            return results[1:]

    ##########################################
    # for results that need to be returned on a pandas data frame

    elif return_as == 'pd_dataframe':

        print(str(datetime.datetime.now())[:19] + ': Returning results as dataframe.')

        results = pd.DataFrame(results[1:], columns=results[0])

        return results

    ##########################################
    # for results that need to be returned in a csv file

    elif return_as == 'csv_file':

        print(str(datetime.datetime.now())[:19] + ': Returning results as csv under filename -> ' + file_name)

        if include_headers:
            write_to_csv(file_name, results)

        else:
            write_to_csv(file_name, results[1:])

        return None

    ##########################################
    # for results that need to be uploaded as CSV to S3

    elif return_as == 's3_csv_file':

        print(str(datetime.datetime.now())[:19] + ': Putting as csv under filename -> ' + file_name)

        if include_headers:
            write_to_csv(file_name, results)

        else:
            write_to_csv(file_name, results[1:])

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

        print(str(datetime.datetime.now())[:19] + ': Uploading to S3.')

        with open(file_name, 'rb') as f:
            s3.Bucket(aws_bucket_name).put_object(Key=(aws_file_path + file_name), Body=f)
            f.close()

        print(str(datetime.datetime.now())[:19] + ': Uploaded to S3.')

        print(str(datetime.datetime.now())[:19] + ': Deleting local remaining file.')

        os.remove(file_name)

        print(str(datetime.datetime.now())[:19] + ': Deleted local remaining file.')

        return None
