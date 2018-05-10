""""Test cases for proxy objects."""
from jsonpointer import resolve_pointer
import pytest
from ymlref.proxies import MappingProxy, SequenceProxy


INNER_REF_DICT = {
    'components': {
        'person': {'name': 'string', 'age': 'number'},
        'pet': {'petId': 'number', 'name': 'string'}
    },
    'foo': {'$ref': '#/components/pet'},
    'bar': {'$ref': '#/components/person/age'},
    'baz': [0, 1, {'$ref': '#/components/person'}]
}

FLATTENED_INNER_REF_DICT = {
    'components': {
        'person': {'name': 'string', 'age': 'number'},
        'pet': {'petId': 'number', 'name': 'string'}
    },
    'foo': {'petId': 'number', 'name': 'string'},
    'bar': 'number',
    'baz': [0, 1, {'name': 'string', 'age': 'number'}]
}

REMOTE_REF_DICT = {
    'content': {
        'points': {
            '$ref': 'http://example.org/points.yml'
        }
    },
    'collection': {
        '$ref': 'mypets.yml'
    }
}

# In some of the following we are disabling pylint unsubscriptable-object error.
# This is because in those cases they clearly fire false positives, but this
# prevents pytest-pylint from passing
def test_plain_dict_access(ref_loader):
    """MappingProxy should allow accessing objects in wrapped plain dictionary using __getitem__."""
    data = {'foo': 'bar', 'baz': {'type': 'object', 'number': 200, 'list': [0, 1, 2, 3]}}
    proxy = MappingProxy(data, ref_loader=ref_loader)
    assert proxy['foo'] == 'bar'
    assert proxy['baz']['type'] == 'object' # pylint: disable=unsubscriptable-object
    assert proxy['baz']['number'] == 200 # pylint: disable=unsubscriptable-object

def test_plain_list_access(ref_loader):
    """SequenceProxy should allow accessing elements using __getitem__."""
    proxy = SequenceProxy([0, 1.0, 'foobar'], ref_loader=ref_loader)
    assert proxy[0] == 0
    assert proxy[1] == 1.0
    assert proxy[2] == 'foobar'

def test_correct_len(ref_loader):
    """MappingProxy should have the same length as the wrapped dict."""
    data = {'foo': 'bar', 'baz': {'type': 'object', 'number': 200, 'list': [0, 1, 2, 3]}}
    proxy = MappingProxy(data, ref_loader=ref_loader)
    assert len(proxy) == 2, 'Should have length equal to length of wrapped dict.'

def test_equals_plain_dict(ref_loader):
    """MappingProxy should compare as equal to the wrapped plain dictionary."""
    data = {'foo': 'bar', 'baz': {'type': 'object', 'number': 200, 'list': [0, 1, 2, 3]}}
    proxy = MappingProxy(data, ref_loader=ref_loader)
    assert proxy == data, 'Should compare as equal to wrapped plain dict.'

@pytest.mark.parametrize('other',
                         [{'a': 2, 'b': 3}, [1, 3], {'a': 'b'}, {'foo': 'baz', 'baz': 100}])
def test_notequals_to_other_dict(other, ref_loader):
    """MappingProxy should not compare as equal to different dict than the wrapped one."""
    data = {'foo': 'bar', 'baz': {'type': 'object', 'number': 200, 'list': [0, 1, 2, 3]}}
    proxy = MappingProxy(data, ref_loader=ref_loader)
    assert proxy != other, 'Should compare as not equal.'

def test_equals_plain_list(ref_loader):
    """SequenceProxy should compare as equal to the wrapped plain list."""
    proxy = SequenceProxy([0, 1.0, 'foobar'], ref_loader=ref_loader)
    assert proxy == [0, 1.0, 'foobar'], 'Should compare as equal to wrapped plain list.'

@pytest.mark.parametrize('other', [[1, 3, 'xyz'], 100, [1, 'a', 'b', 'c']])
def test_notequals_to_other_list(other, ref_loader):
    """SequenceProxy should not compare as equal to different object than the wrapped one."""
    proxy = SequenceProxy([0, 1.0, 'foobar'], ref_loader=ref_loader)
    assert proxy != other, 'Should compare as not equal.'

def test_jsonpointer(ref_loader):
    """Proxies should be compatible with jsonpointer's resolve_pointer."""
    proxy = MappingProxy(INNER_REF_DICT, ref_loader=ref_loader)
    expected = {'name': 'string', 'age': 'number'}
    actual = resolve_pointer(proxy, '/components/person')
    assert expected == actual
    assert isinstance(actual, MappingProxy)

def test_ref_access(ref_loader):
    """Proxies should allow accessing objects via reference to local document."""
    proxy = MappingProxy(INNER_REF_DICT, ref_loader=ref_loader)
    assert proxy['bar'] == 'number', 'Should be able to extract single field.'
    exp_foo = {'petId': 'number', 'name': 'string'}
    assert proxy['foo'] == exp_foo, 'Should be able to extract whole dict object.'
    exp_baz = {'name': 'string', 'age': 'number'}
    # pylint: disable=unsubscriptable-object
    assert proxy['baz'][2] == exp_baz, 'Should be able to extract object from list.'

def test_get_existing(ref_loader):
    """MappingProxy should support get method for existing elements."""
    proxy = MappingProxy(INNER_REF_DICT, ref_loader=ref_loader)
    expected = FLATTENED_INNER_REF_DICT['components']
    assert expected == proxy.get('components'), 'Should get element.'

def test_get_with_ref(ref_loader):
    """The get method should also work for references."""
    proxy = MappingProxy(INNER_REF_DICT, ref_loader=ref_loader)
    pet = FLATTENED_INNER_REF_DICT['components']['pet']
    assert pet == proxy.get('foo'), 'Should get referenced object.'
    assert proxy.get('bar') == 'number', 'Should get referenced primitive value.'

def test_get_with_default(ref_loader):
    """MappingProxy should support getting default value if key is not present."""
    proxy = MappingProxy(INNER_REF_DICT, ref_loader=ref_loader)
    assert proxy.get('test123') is None, 'Default value should be None.'
    assert proxy.get('test321', 'ddd') == 'ddd', 'Should use provided default value.'

def test_access_remote_resource(ref_loader):
    """Proxy should use its ref_loader to get remote content."""
    proxy = MappingProxy(REMOTE_REF_DICT, ref_loader)
    result = proxy['content']['points']
    ref_loader.load_ref.assert_called_once_with(proxy, 'http://example.org/points.yml')
    assert result == {'points': [{'x': 21, 'y': 37}, {'x': 4, 'y': 20}]}

def test_access_local_file(ref_loader):
    """Proxy should use its ref_loader to get local file's content."""
    proxy = MappingProxy(REMOTE_REF_DICT, ref_loader)
    result = proxy['collection']
    ref_loader.load_ref.assert_called_once_with(proxy, 'mypets.yml')
    assert result == [{'type': 'dog', 'name': 'Lessie'}, {'type': 'starfish', 'name': 'Patrick'}]
