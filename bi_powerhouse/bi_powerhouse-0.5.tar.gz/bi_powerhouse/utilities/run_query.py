# -*- coding: utf-8 -*-

"""Runs a query"""

from bi_powerhouse.utilities.db_connections import cursor_creator as cc
from bi_powerhouse.utilities.db_connections import individual_query_runner as iq
from bi_powerhouse.utilities.write_to_csv import write_to_csv
from bi_powerhouse.utilities.s3_upload import s3_upload as s3_upload
import pandas as pd
import os
import datetime

##########################################
##########################################
##########################################
##########################################


def run_query(engine, query_file, host, port, username, password, database, autocommit=False, return_as='nested_list',
              include_headers=True, file_name=None, returns_rows=True, aws_access_key_id=None,
              aws_secret_access_key=None, aws_region_name='us-east-1', aws_bucket_name=None, aws_file_path='',
              text_to_replace=None, replace_text_with=None):

    results = []

    ##########################################
    # gets the queries in the file

    print(str(datetime.datetime.now())[:19] + ': Reading query file.')

    with open(query_file) as f:
        query = f.read()
        f.close()

    ##########################################
    # replaces the text in the queries if needed

    if text_to_replace and replace_text_with:

        print(str(datetime.datetime.now())[:19] + ': Replacing text in the queries.')

        query = query.replace(text_to_replace, replace_text_with)

    ##########################################
    # splits the queries into a list

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

        s3_upload(file_name, aws_bucket_name, aws_file_path, aws_region_name=aws_region_name,
                  aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        print(str(datetime.datetime.now())[:19] + ': Deleting local remaining file.')

        os.remove(file_name)

        print(str(datetime.datetime.now())[:19] + ': Deleted local remaining file.')

        return None

    ##########################################
    # for results that need to be returned as a dict

    elif return_as == 'dict':

        keys = results[0]
        values = results[1:]
        output = []

        for row in values:
            output.append(dict(zip(keys, row)))

        output = {'data': output}

        return output
