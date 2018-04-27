import unittest

import mock

from mopidy_playerfm import PlayerFmExtension, backend as backend_lib


class ExtensionTest(unittest.TestCase):

    @staticmethod
    def get_config():
        config = {}
        config['username'] = 'test@test.com'
        config['password'] = 'secret_password'
        config['refresh_playlists'] = 60
        return {'playerfm': config}

    def test_get_default_config(self):
        ext = PlayerFmExtension()

        config = ext.get_default_config()

        assert '[playerfm]' in config
        assert 'enabled = true' in config
        assert 'refresh_playlists = 60' in config

    def test_get_config_schema(self):
        ext = PlayerFmExtension()

        schema = ext.get_config_schema()

        assert 'username' in schema
        assert 'password' in schema
        assert 'refresh_playlists' in schema

    def test_get_backend_classes(self):
        registry = mock.Mock()

        ext = PlayerFmExtension()
        ext.setup(registry)

        self.assertIn(
            mock.call('backend', backend_lib.PlayerFmBackend),
            registry.add.mock_calls)

    def test_init_backend(self):
        backend = backend_lib.PlayerFmBackend(
            ExtensionTest.get_config(), None)
        self.assertIsNotNone(backend)
        backend.on_start()
        backend.on_stop()
