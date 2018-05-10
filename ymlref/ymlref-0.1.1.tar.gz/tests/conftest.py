"""Common tests configuration for ymlref."""
from io import StringIO
import pytest
import yaml
from ymlref.ref_loaders import ReferenceLoader

REMOTE_CONTENT = """
points:
  - x: 21
    y: 37
  - x: 4
    y: 20
"""

LOCAL_CONTENT = """
- type: dog
  name: Lessie
- type: starfish
  name: Patrick
"""

@pytest.fixture(name='open_local')
def open_local_factory(mocker):
    """Fixture providing open_local function for ReferenceLoader construction."""
    return mocker.Mock(return_value=StringIO(LOCAL_CONTENT))

@pytest.fixture(name='open_remote')
def open_remote_factory(mocker):
    """Fixture providing open_remote function for ReferenceLoader construction."""
    return mocker.Mock(return_value=StringIO(REMOTE_CONTENT))

@pytest.fixture(name='load_yaml')
def load_yaml_factory(mocker):
    """Fixture providing load_yaml function for ReferenceLoader construction."""
    return mocker.Mock(wraps=yaml.load)

@pytest.fixture(name='ref_loader')
def ref_loader_factory(mocker, open_local, open_remote, load_yaml):
    """Fixture providing ReferenceLoader instance with some mocked openers."""
    loader = ReferenceLoader(load_yaml, open_local, open_remote)
    return mocker.Mock(wraps=loader)
