
import logging
import time
from threading import Lock

from mopidy import backend

import pykka

from .library import PlayerFmLibraryProvider
from .playback import PlayerFmPlaybackProvider
from .playlists import PlayerFmPlaylistsProvider
from .repeating_timer import RepeatingTimer
from .session import PlayerFmSession

logger = logging.getLogger(__name__)


class PlayerFmBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(PlayerFmBackend, self).__init__()

        self.audio = audio
        self.config = config

        self.auth = False

        self._refresh_playlists_rate = \
            config['playerfm']['refresh_playlists'] * 60.0
        self._refresh_playlists_timer = None
        self._playlist_lock = Lock()

        self.library = PlayerFmLibraryProvider(backend=self)
        self.playback = PlayerFmPlaybackProvider(audio=audio, backend=self)
        self.playlists = PlayerFmPlaylistsProvider(backend=self)
        self.session = PlayerFmSession()

        self.uri_schemes = ['playerfm']

    def on_start(self):
        self.auth = self.session.login(self.config['playerfm']['username'],
                                       self.config['playerfm']['password'])

        if self.auth and self._refresh_playlists_rate > 0:
            self._refresh_playlists_timer = RepeatingTimer(
                    self._refresh_playlists,
                    self._refresh_playlists_rate)
            self._refresh_playlists_timer.start()

    def on_stop(self):
        if self.auth and self._refresh_playlists_timer:
            self._refresh_playlists_timer.cancel()
            self._refresh_playlists_timer = None

    def _refresh_playlists(self):
        with self._playlist_lock:
            t0 = round(time.time())
            logger.info('Start refreshing PlayerFM playlists')
            self.playlists.refresh()
            t = round(time.time()) - t0
            logger.info('Finished refreshing PlayerFM playlists in %ds', t)
