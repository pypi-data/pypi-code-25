import pytest

from .notebook import Notebook
from clusterone.mocks import NOTEBOOK_JOB_CONFIGURATION, NOTEBOOK_API_RESPONSE


@pytest.mark.skip()
def test_existing(mocker):
    raise NotImplementedError()


def test_new(mocker):
    mock_client = mocker.Mock()
    mock_client.client_action.return_value = NOTEBOOK_API_RESPONSE

    target = Notebook.__new__(Notebook)
    target._initialize(NOTEBOOK_API_RESPONSE)

    assert Notebook(mock_client, NOTEBOOK_JOB_CONFIGURATION) == target

    args, kwargs = mock_client.client_action.call_args
    assert args[0] == ['notebooks', 'create']
    assert kwargs['params'] == {
        'repository': None,
        'display_name': 'snowy-surf-115',
        'description': '',
        'parameters': NOTEBOOK_JOB_CONFIGURATION,
        'datasets_set': [],
        'git_commit_hash': 'latest',
    }


def test_params(mocker):
    test_notebook = Notebook.__new__(Notebook)
    test_notebook._initialize(NOTEBOOK_API_RESPONSE)

    assert test_notebook.id == "853b9f10-36ce-4de4-b2f8-108d69733b42"
    assert test_notebook.url == "http://853b9f10-36ce-4de4-b2f8-108d69733b42.jupyter.v2.clusterone.com"
