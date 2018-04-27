import logging

from mopidy import backend

logger = logging.getLogger(__name__)


class PlayerFmPlaybackProvider(backend.PlaybackProvider):
    def translate_uri(self, uri):
        episode_id = uri.rsplit(':')[-1]
        stream_uri = self.backend.session.get_stream_url(episode_id)
        logger.debug('Translated: %s -> %s', uri, stream_uri)

        return stream_uri
