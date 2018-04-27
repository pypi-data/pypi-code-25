from __future__ import unicode_literals

import hashlib
import logging
import time

from mopidy import backend
from mopidy.models import Album, Artist, Ref, Track

logger = logging.getLogger(__name__)


class PlayerFmLibraryProvider(backend.LibraryProvider):
    root_directory = Ref.directory(uri='playerfm:directory', name='Player FM')

    def __init__(self, *args, **kwargs):
        super(PlayerFmLibraryProvider, self).__init__(*args, **kwargs)

        self._root = [
                Ref.directory(uri='playerfm:featured:topics', name='Featured'),
        ]

    def browse(self, uri):
        if not uri:
            return []
        type = uri.split(':')[1]
        if uri == self.root_directory.uri:
            return self._root
        elif type == 'featured':
            if uri.rsplit(':', 1)[-1] == 'all':
                buri = uri.rsplit(':', 1)[0]
                return self.backend.session.get_series_dirs(buri)
            else:
                return self.backend.session.get_topic_dirs(uri)
        elif type == 'series':
            return self.backend.session.get_series_entries(uri)
        else:
            return []

    def lookup(self, uri):
        if uri.startswith('playerfm:episode:'):
            return self._lookup_episode(uri)
        else:
            logger.info("Can't lookup %s", str(uri))
            return []

    def _lookup_episode(self, uri):
        episode = self.backend.session.get_episode_info(uri.split(':')[2])
        if episode is None:
            logger.warning('There is no episode %r', uri)
            return []
        mopidy_track = self._to_mopidy_track(episode)
        return [mopidy_track]

    def _get_images(self, episode):
        if 'imageURL' in episode['series']:
            return [episode['series']['imageURL']]

    def _create_id(self, u):
        return hashlib.md5(u.encode('utf-8')).hexdigest()

    def _to_mopidy_album(self, episode):
        name = episode['series']['title']
        artist = self._to_mopidy_artist(episode)
        date = unicode(time.strftime('%Y-%m-%d %H:%M:%S',
                       time.localtime(
                            episode['series']['stats']['latestPublishedAt'])))
        album_id = episode['series']['id']
        uri = 'playerfm:album:' + str(album_id)
        images = self._get_images(episode)
        return Album(
            uri=uri,
            name=name,
            artists=[artist],
            num_tracks=episode['series']['stats']['numberOfEpisodes'],
            num_discs=None,
            date=date,
            images=images)

    def _to_mopidy_artist(self, episode):
        if 'author' in episode['series']:
            name = episode['series']['author']
        else:
            name = 'Unknown'
        artist_id = self._create_id(name)
        uri = 'playerfm:artist:' + artist_id
        return Artist(uri=uri, name=name)

    def _to_mopidy_track(self, episode):
        episode_id = episode['id']
        if episode_id is None:
            raise ValueError
        if episode['duration'] is None:
            length = None
        else:
            length = episode['duration']*1000
        return Track(
            uri='playerfm:episode:' + str(episode_id),
            name=episode['title'],
            artists=[self._to_mopidy_artist(episode)],
            album=self._to_mopidy_album(episode),
            track_no=None,
            disc_no=None,
            date=unicode(time.strftime('%Y-%m-%d %H:%M:%S',
                         time.localtime(episode['publishedAt']))),
            length=length,
            comment=episode['description'],
            last_modified=None)
