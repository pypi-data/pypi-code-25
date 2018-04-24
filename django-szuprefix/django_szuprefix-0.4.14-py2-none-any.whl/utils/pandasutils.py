# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
import pandas as pd
from .dbutils import db_sqlalchemy_str


def get_select_sql(sql):
    return ' from ' in sql.lower() and sql or (u'select * from %s' % sql)


def get_dataframe_from_table(table_name_or_sql, connection="default"):
    return pd.read_sql(get_select_sql(table_name_or_sql), db_sqlalchemy_str(connection))


def write_dataframe_to_table(df, **kwargs):
    kwargs['con'] = db_sqlalchemy_str(kwargs['con'])
    return df.to_sql(**kwargs)
