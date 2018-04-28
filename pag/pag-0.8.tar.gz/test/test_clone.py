import unittest
import mock

from click.testing import CliRunner

from pag.commands.clone import clone

EMPTY_RESPONSE = mock.Mock(json=lambda : {
    'total_projects': 0,
    'projects': [],
})

RESPONSE_WITH_REPO = mock.Mock(json=lambda: {
    'total_projects': 0,
    'projects': [{'name': 'fedmod', 'namespace': 'modularity'}],
})


class CloneTest(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.maxDiff = None
        self.patcher = mock.patch('requests.get')
        self.mock_get = self.patcher.start()
        self.mock_get.return_value = EMPTY_RESPONSE

    def tearDown(self):
        self.patcher.stop()

    @mock.patch('pag.commands.clone.run')
    def test_clone(self, run):
        result = self.runner.invoke(clone, ['pag'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            run.call_args_list,
            [mock.call(['git', 'clone', 'ssh://git@pagure.io/pag.git', 'pag'])]
        )
        self.assertEqual(self.mock_get.call_args_list, [])

    @mock.patch('pag.commands.clone.run')
    def test_clone_anonymous(self, run):
        result = self.runner.invoke(clone, ['-a', 'pag'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            run.call_args_list,
            [mock.call(['git', 'clone', 'https://pagure.io/pag.git', 'pag'])]
        )
        self.assertEqual(self.mock_get.call_args_list, [])

    @mock.patch('pag.commands.clone.run')
    def test_clone_fork(self, run):
        result = self.runner.invoke(clone, ['ralph/pag'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            run.call_args_list,
            [mock.call(['git', 'clone', 'ssh://git@pagure.io/forks/ralph/pag.git', 'pag'])]
        )
        self.assertEqual(self.mock_get.call_args_list,
                         [mock.call(mock.ANY, {'namespace': 'ralph', 'name': 'pag'})])

    @mock.patch('pag.commands.clone.run')
    def test_clone_fork_anonymous(self, run):
        result = self.runner.invoke(clone, ['-a', 'ralph/pag'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            run.call_args_list,
            [mock.call(['git', 'clone', 'https://pagure.io/forks/ralph/pag.git', 'pag'])]
        )
        self.assertEqual(self.mock_get.call_args_list,
                         [mock.call(mock.ANY, {'namespace': 'ralph', 'name': 'pag'})])

    @mock.patch('pag.commands.clone.run')
    def test_clone_namespace(self, run):
        self.mock_get.return_value = RESPONSE_WITH_REPO

        result = self.runner.invoke(clone, ['modularity/fedmod'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            run.call_args_list,
            [mock.call(['git', 'clone', 'ssh://git@pagure.io/modularity/fedmod.git', 'fedmod'])]
        )
        self.assertEqual(self.mock_get.call_args_list,
                         [mock.call(mock.ANY, {'namespace': 'modularity', 'name': 'fedmod'})])

    @mock.patch('pag.commands.clone.run')
    def test_clone_namespace_anonymous(self, run):
        self.mock_get.return_value = RESPONSE_WITH_REPO

        result = self.runner.invoke(clone, ['-a', 'modularity/fedmod'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            run.call_args_list,
            [mock.call(['git', 'clone', 'https://pagure.io/modularity/fedmod.git', 'fedmod'])]
        )
        self.assertEqual(self.mock_get.call_args_list,
                         [mock.call(mock.ANY, {'namespace': 'modularity', 'name': 'fedmod'})])
