from github_status import main, conf


class TestEnvVars(object):

    def test_env_vars_are_emtpy(self, p_env):
        main.Status(argv=[], parse=False)
        assert conf['env'] == {}

    def test_env_var_is_set(self, p_env):
        p_env({'GITHUB_SHA': 'asdf'})
        main.Status(argv=[], parse=False)
        assert conf['env']['GITHUB_SHA'] == 'asdf'

    def test_double_quotes_are_removed(self, p_env):
        p_env({'GITHUB_SHA': '"asdf"'})
        main.Status(argv=[], parse=False)
        assert conf['env']['GITHUB_SHA'] == 'asdf'

    def test_single_quotes_are_removed(self, p_env):
        p_env({'GITHUB_SHA': "'asdf'"})
        main.Status(argv=[], parse=False)
        assert conf['env']['GITHUB_SHA'] == 'asdf'

    def test_combined_quotes_are_removed(self, p_env):
        p_env({'GITHUB_SHA': """'"asdf"'"""})
        main.Status(argv=[], parse=False)
        assert conf['env']['GITHUB_SHA'] == 'asdf'

