from github_status import util


class TestBuildIsTriggered(object):

    def setup(self):
        self.ghprb_env_vars = [
            'ghprbActualCommit', 'ghprbTriggerAuthor', 'ghprbTargetBranch',
            'ghprbTriggerAuthorLogin', 'ghprbCredentialsId', 'ghprbGhRepository',
        ]

    def test_is_triggered(self, p_env):
        p_env(dict((k, '1') for k in self.ghprb_env_vars))
        assert util.build_is_triggered() is True

    def test_is_not_triggered(self, p_env):
        assert util.build_is_triggered() is False


class TestConstructURl(object):

    def test_repo_gets_stripped(self, p_env):
        p_env({'GITHUB_REPOSITORY': 'ceph/ceph/', 'GITHUB_SHA': 'asdf'})
        assert util.construct_url() == 'https://api.github.com/repos/ceph/ceph/statuses/asdf'

    def test_repo_removes_quotes(self, p_env):
        p_env({'GITHUB_REPOSITORY': '"ceph/ceph/"', 'GITHUB_SHA': 'asdf'})
        assert util.construct_url() == 'https://api.github.com/repos/ceph/ceph/statuses/asdf'

