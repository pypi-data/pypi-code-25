import pytest
import pickle

from .fixtures import *


@pytest.mark.parametrize('objkey', pickleable)
def test_pickling(objkey, request):
    obj = request.getfixturevalue(objkey)
    for iprotocol in (0,1,2):
        x = pickle.dumps(obj, protocol=iprotocol)
        y = pickle.loads(x)
        assert type(y) == type(obj)
