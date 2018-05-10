"""Test cases for publicly exposed API."""
from io import StringIO
import pytest
from ymlref import load, loads
from ymlref.proxies import MappingProxy


FLATTENED_DICT = {
    'components': {
        'pet': {'petId': 'integer', 'petName': 'string'},
        'person': {'name': 'string', 'age': 'integer'}
    },
    'foo': {'petId': 'integer', 'petName': 'string'},
    'bar': 'integer',
    'baz': [0, 1, {'name': 'string', 'age': 'integer'}]
}

YML = """bar:
  $ref: '#/components/person/age'
baz:
- 0
- 1
- $ref: '#/components/person'
components:
  person:
    age: integer
    name: string
  pet:
    petId: integer
    petName: string
foo:
  $ref: '#/components/pet'
"""

@pytest.fixture(name='stream')
def stream_factory():
    """Factory providing stream to read YML from."""
    stream = StringIO(YML)
    return stream

def test_load_yml(stream, ref_loader):
    """The load function should read data from stream and construct correct proxy."""
    doc = load(stream, ref_loader)
    assert doc == MappingProxy(FLATTENED_DICT, ref_loader=ref_loader)

def test_loads_yml(ref_loader):
    """The loads function should  construct correct proxy."""
    doc = loads(YML, ref_loader)
    assert doc == MappingProxy(FLATTENED_DICT, ref_loader=ref_loader)
