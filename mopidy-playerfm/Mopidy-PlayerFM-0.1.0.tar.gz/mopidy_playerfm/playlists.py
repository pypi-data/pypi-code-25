import logging
import operator

from mopidy import backend
from mopidy.models import Playlist, Ref

logger = logging.getLogger(__name__)


class PlayerFmPlaylistsProvider(backend.LibraryProvider):

    def __init__(self, *args, **kwargs):
        super(PlayerFmPlaylistsProvider, self).__init__(*args, **kwargs)
        self._playlists = {}

    def as_list(self):
        refs = [
            Ref.playlist(uri=pl.uri, name=pl.name)
            for pl in self._playlists.values()]
        return sorted(refs, key=operator.attrgetter('name'))

    def get_items(self, uri):
        playlist = self._playlists.get(uri)
        if playlist is None:
            return None
        return [Ref.track(uri=t.uri, name=t.name) for t in playlist.tracks]

    def lookup(self, uri):
        return self._playlists.get(uri)

    def refresh(self):
        playlists = {}

        episodes = []
        for episode in self.backend.session.get_subscribed_podcasts():
            episodes.append(self.backend.library._to_mopidy_track(episode))

        if len(episodes) > 0:
            uri = 'playerfm:playlist:subscribed'
            playlists[uri] = Playlist(uri=uri,
                                      name='PlayerFM - Subscribed Podcasts',
                                      tracks=episodes)

        self._playlists = playlists
        backend.BackendListener.send('playlists_loaded')

    def create(self, name):
        raise NotImplementedError

    def delete(self, uri):
        raise NotImplementedError

    def save(self, playlist):
        raise NotImplementedError
