import unittest
import mock

from click.testing import CliRunner

from pag.commands.review import review


# This is an abbreviated response from list pull request API that contains
# minimal amount of data needed.
LIST_RESPONSE = {
    "requests": [
        {
            "id": 2344,
            "title": "Fix the API docs",
            "user": {"name": "mprahl"}
        },
        {
            "id": 2343,
            "title": ("Add ways to customize the gitolite configuration file "
                      "with snippets, and some extra details"),
            "user": {"name": "pingou"}
        }
    ],
    "total_requests": 2
}

# This is expected output when listing pull requests returns the data above.
LIST_OUTPUT = """
 2344 mprahl  Fix the API docs
 2343 pingou  Add ways to customize the gitolite configuration file with
              snippets, and some extra details
""".lstrip('\n')

# Abbreviated response for listing details about a pull request.
GET_RESPONSE = {
  "branch_from": "fix-api-docs",
  "commit_stop": "a08f507b99afeda8b9d1f5cf2024eb723726924b",
  "id": 2344,
  "remote_git": None,
  "repo_from": {
    "fullname": "forks/mprahl/pagure",
  },
}


class ReviewTest(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.maxDiff = None

    @mock.patch('pag.commands.review.run')
    @mock.patch('pag.commands.review.in_git_repo', new=lambda: 'my-project')
    def test_open_web(self, run):
        run.side_effect = [
            (0, 'review/12/3\n'),
            (0, ''),
        ]

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(review, ['--open'])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            run.call_args_list,
            [mock.call(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], echo=False),
             mock.call(
                ['xdg-open', 'https://pagure.io/my-project/pull-request/12'])]
        )

    @mock.patch('pag.commands.review.run')
    def test_open_web_on_bad_branch(self, run):
        run.return_value = (0, 'master\n')

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(review, ['--open'])

        self.assertEqual(result.exit_code, 1)
        self.assertIn('Not on a review branch', result.output)

    @mock.patch('pag.commands.review.list_pull_requests')
    @mock.patch('pag.commands.review.in_git_repo', new=lambda: 'pagure')
    def test_list(self, list_pull_requests):
        list_pull_requests.return_value = LIST_RESPONSE['requests']

        result = self.runner.invoke(review, ['--list'])

        self.assertEqual(
            list_pull_requests.call_args_list,
            [mock.call('pagure')])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, LIST_OUTPUT)

    @mock.patch('requests.get')
    @mock.patch('pag.commands.review.run')
    @mock.patch('pag.commands.review.in_git_repo', new=lambda: 'pagure')
    def test_checkout_new(self, run, get):
        get.return_value = mock.Mock(
            json=mock.Mock(return_value=GET_RESPONSE)
        )
        run.side_effect = [
            (1, ''),
            (0, ''),
            (0, 'review/2344/1\n'),
            (0, ''),
        ]

        result = self.runner.invoke(review, ['2344'])

        self.assertEqual(
            get.call_args_list,
            [mock.call('https://pagure.io/api/0/pagure/pull-request/2344')])
        self.assertEqual(
            run.call_args_list,
            [mock.call(['git', 'branch', '--contains',
                        'a08f507b99afeda8b9d1f5cf2024eb723726924b',
                        'review/2344/*'], echo=False),
             mock.call(
                ['git', 'fetch', 'https://pagure.io/forks/mprahl/pagure.git',
                 'fix-api-docs'], graceful=False),
             mock.call(['git', 'branch', '--list', 'review/2344/*'],
                       echo=False, graceful=False),
             mock.call(['git', 'checkout', '-b', 'review/2344/2',
                        'FETCH_HEAD'], graceful=False),
             ])
        self.assertEqual(result.exit_code, 0)

    @mock.patch('requests.get')
    @mock.patch('pag.commands.review.run')
    @mock.patch('pag.commands.review.in_git_repo', new=lambda: 'pagure')
    def test_checkout_existing(self, run, get):
        get.return_value = mock.Mock(
            json=mock.Mock(return_value=GET_RESPONSE)
        )
        run.side_effect = [
            (0, 'review/2344/1\n'),
            (0, ''),
        ]

        result = self.runner.invoke(review, ['2344'])

        self.assertEqual(
            get.call_args_list,
            [mock.call('https://pagure.io/api/0/pagure/pull-request/2344')])
        self.assertEqual(
            run.call_args_list,
            [
             mock.call(['git', 'branch', '--contains',
                        'a08f507b99afeda8b9d1f5cf2024eb723726924b',
                        'review/2344/*'], echo=False),
             mock.call(['git', 'checkout', 'review/2344/1'], graceful=False),
             ])
        self.assertEqual(result.exit_code, 0)

    @mock.patch('pag.commands.review.run')
    @mock.patch('pag.commands.review.list_pull_requests', new=lambda _: LIST_RESPONSE['requests'])
    @mock.patch('pag.commands.review.in_git_repo', new=lambda: 'pagure')
    def test_cleanup_merged_branches(self, run):
        run.return_value = (0, 'review/1/1\nreview/1/2\n')

        result = self.runner.invoke(review, ['--cleanup'])

        self.assertEqual(result.exit_code, 0)

        self.assertEqual(
            run.call_args_list,
            [
                mock.call(['git', 'branch', '--list', 'review/*'], echo=False),
                mock.call(['git', 'branch', '-D', 'review/1/1', 'review/1/2']),
            ])

    @mock.patch('pag.commands.review.run')
    @mock.patch('pag.commands.review.list_pull_requests', new=lambda _: LIST_RESPONSE['requests'])
    @mock.patch('pag.commands.review.in_git_repo', new=lambda: 'pagure')
    def test_keep_branch_for_opened_pr(self, run):
        run.return_value = (0, 'review/2344/1\nreview/2344/2\n')

        result = self.runner.invoke(review, ['--cleanup'])

        self.assertEqual(result.exit_code, 0)

        self.assertEqual(
            run.call_args_list,
            [
                mock.call(['git', 'branch', '--list', 'review/*'], echo=False),
            ])
