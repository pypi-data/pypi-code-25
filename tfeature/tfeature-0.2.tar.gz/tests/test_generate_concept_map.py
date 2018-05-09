import pytest
import pandas as pd
from .context import zen
import os
import  zen.cp_map_transform as cmt

hcp_name_map_file = os.path.abspath(os.path.join(os.path.dirname('__file__'), 'tests/const/hcp_name_map.csv'))
hcp_code_map_file = os.path.abspath(os.path.join(os.path.dirname('__file__'), 'tests/const/hcp_code_dict.py'))

@pytest.fixture(scope='module')
def cname_df():
    return pd.read_csv(hcp_name_map_file, index_col=0)

@pytest.fixture(scope='module')
def ccode_dict():
    from .const import hcp_code_dict as hcode
    return hcode.CCODE_MAP

def test_ccode_df(cname_df, ccode_dict):
    ccode_df = cmt.ccode_df(ccode_dict)
    assert len(ccode_df.c_code.unique()) == len(cname_df.c_code)
    # for k in ccode_dict:
        # assert len(ccode_dict[k]) == len(ccode_df[ccode_df['c_code']==k].loc[:, 'code'].values)

def test_concepts_df(cname_df, ccode_dict):
    ccode_df = cmt.ccode_df(ccode_dict)
    concepts_df = cmt.concepts_df(ccode_df, cname_df)
    assert len(ccode_df.c_code.unique()) == len(cname_df.c_code) == len(concepts_df.c_code.unique())
    assert len(ccode_df.code) == len(concepts_df.code)
    # for k in ccode_dict:
        # assert len(ccode_dict[k]) == len(concepts_df[concepts_df['c_code']==k].loc[:, 'code'].values)
