"""Test cases for Resolvers."""
from io import StringIO, BytesIO
import jsonpointer
import pytest
import yaml
from ymlref.proxies import MappingProxy
from ymlref.ref_loaders import ReferenceLoader, ReferenceType


DOCUMENT = """
foo:
   bar: baz
   test: 2
   x: [0, 1, 2]
"""

REMOTE_DOCUMENT = """
foo: baz
bar:
  - a: 100
    b: 200
  - x: 5
    y: -10
"""

@pytest.fixture(name='load_yaml')
def load_yaml_factory(mocker):
    """Fixture providing mock wrapping yaml.load function."""
    return mocker.Mock(wraps=yaml.load)

@pytest.fixture(name='resolve_pointer')
def resolve_pointer_factory(mocker):
    """Fixture mock patching resolve_pointer function used by ReferenceLoader."""
    return mocker.patch('ymlref.ref_loaders.resolve_pointer',
                        mocker.Mock(wraps=jsonpointer.resolve_pointer))

@pytest.fixture(name='stringio', scope='function')
def stringio_factory(mocker):
    """Fixture providing stringio with YML content for mocking local files."""
    stringio = StringIO(DOCUMENT)
    mocker.spy(stringio, 'read')
    return stringio

@pytest.fixture(name='remote_bytesio', scope='function')
def remote_bytesio_factory(mocker):
    """Fixture providing bytesio with YML content for mocking remote files."""
    bytesio = BytesIO(REMOTE_DOCUMENT.encode('utf-8'))
    mocker.spy(bytesio, 'read')
    return bytesio

@pytest.fixture(name='open_local')
def open_local_factory(mocker, stringio):
    """Fixture providing mock used as local opener (like the open function)."""
    opener = mocker.Mock(return_value=stringio)
    return opener

@pytest.fixture(name='open_remote')
def open_remote_factory(mocker, remote_bytesio):
    """Fixture providing mock used as remote file opener (like urlopen)."""
    opener = mocker.Mock()
    opener.return_value = remote_bytesio
    return opener

@pytest.fixture(name='ref_loader')
def resolver_factory(open_local, open_remote, load_yaml):
    """Fixture providing ReferenceLoader instance."""
    return ReferenceLoader(open_local=open_local, open_remote=open_remote,
                           load_yaml=load_yaml)

@pytest.fixture(name='root_doc')
def root_doc_factory(ref_loader):
    """Fixture providing root document's mock."""
    root = MappingProxy(yaml.load(StringIO(DOCUMENT)), ref_loader=ref_loader)
    return root

def test_classifies_reference(ref_loader):
    """ReferenceLoader should correctly classify internal, local and remote references."""
    assert ReferenceType.INTERNAL == ref_loader.classify_ref('#/components/pet')
    assert ReferenceType.LOCAL == ref_loader.classify_ref('components.yml')
    assert ReferenceType.REMOTE == ref_loader.classify_ref('file://definitions.yml')
    assert ReferenceType.REMOTE == ref_loader.classify_ref('https://definitions.yml')

@pytest.mark.parametrize('path', ['components.yml', './definitions.yml'])
def test_call_chain_local_files(ref_loader, root_doc, path):
    """ReferenceLoader should use its open_local and load_yaml for accessing relative paths."""
    content = ref_loader.load_ref(root_doc, path)
    ref_loader.open_local.assert_called_once_with(path)
    ref_loader.open_remote.assert_not_called()
    ref_loader.load_yaml.assert_called_once_with(DOCUMENT)
    assert yaml.load(DOCUMENT) == content

@pytest.mark.parametrize('ref', ['file:///some/path/todocument.yml', 'http://doc.yml'])
def test_call_chain_remote_refs(ref_loader, root_doc, ref):
    """ReferenceLoader should use its open_remote and load_yaml to access remote references."""
    content = ref_loader.load_ref(root_doc, ref)
    ref_loader.open_remote.assert_called_once_with(ref)
    ref_loader.open_local.assert_not_called()
    ref_loader.load_yaml.assert_called_once_with(REMOTE_DOCUMENT.encode('utf-8'))
    assert yaml.load(REMOTE_DOCUMENT) == content

@pytest.mark.parametrize('pointer,arg', [('#/foo', '/foo'), ('/foo', '/foo')])
def test_uses_resolve_pointer(ref_loader, root_doc, pointer, arg, resolve_pointer):
    """ReferenceLoader should use resolve pointer and load_yaml to access internal references."""
    content = ref_loader.load_ref(root_doc, pointer)
    resolve_pointer.assert_called_once_with(root_doc, arg)
    expected = {'bar': 'baz', 'test': 2, 'x': [0, 1, 2]}
    assert expected == content
