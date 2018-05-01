# -*- coding: utf-8 -*-

"""Runs a query"""

import datetime

##########################################
##########################################
##########################################
##########################################


def run_single_query(cur, query, engine, close_cursor, returns_rows):

    query_results = []
    column_names = []

    ##########################################
    # runs the query

    print(str(datetime.datetime.now())[:19] + ': Running query: ' + query)

    cur.execute(query)

    print(str(datetime.datetime.now())[:19] + ': Query was executed.')

    ##########################################
    # if the query doesn't return any rows (non-select statements)

    if returns_rows:

        print(str(datetime.datetime.now())[:19] + ': Getting rows.')

        ##########################################
        # adds the column names as the first item of the nested list

        for col in cur.description:

            if engine in ('mysql', 'sqlserver'):
                column_names.append(col[0])

            elif engine in ('redshift', 'postgresql'):
                column_names.append(col[0].decode("utf-8"))

        query_results.append(column_names)

        ##########################################
        # puts the results in a nested list

        for row in cur:
            row = [str(n) for n in row]
            query_results.append(list(row))

        print(str(datetime.datetime.now())[:19] + ': Rows extracted.')

    else:
        return None

    ##########################################
    # closes the connection if needed

    if close_cursor:

        print(str(datetime.datetime.now())[:19] + ': Closing cursor.')

        cur.close()

        print(str(datetime.datetime.now())[:19] + ': Cursor closed')

    ##########################################
    # returns the nested list with the results and the headers

    return query_results
