import logging

from bs4 import BeautifulSoup

from mopidy.models import Ref

import requests

logger = logging.getLogger(__name__)


class PlayerFmSession(object):
    def login(self, username, password):
        self.s = requests.Session()

        if username is None or password is None:
            logger.info('PlayerFM not logged in (no username/password)')
            return False

        # Authenticate with player.fm
        r = self.s.post("https://player.fm/users/sign_in.json",
                        json={"user": {"login": username,
                                       "password": password,
                                       "remember_me": "true", }})

        if r.status_code == 200:
            logger.info('Logged in to PlayerFM')
            authenticated = True
        else:
            logger.info('Failed to login to PlayerFM as "%s"', username)
            authenticated = False

        return authenticated

    def get_topic_dirs(self, uri):
        dirs = [Ref.directory(uri=uri + ':all', name='All')]
        r = self.s.get("https://player.fm/featured/" + uri.rsplit(':', 1)[-1])
        soup = BeautifulSoup(r.text, "html.parser")
        for topic in soup.find_all("a", "sub-channel-link has-children"):
            suri = 'playerfm:featured:' + topic["href"].rsplit("/", 1)[-1]
            dirs.append(Ref.directory(uri=suri, name=topic.text))
        return dirs

    def get_series_dirs(self, uri):
        dirs = []
        r = self.s.get("https://player.fm/featured/" + uri.rsplit(':', 1)[-1])
        soup = BeautifulSoup(r.text, "html.parser")
        for entry in soup.find_all(
                    "section", "records-list records-list series-list"):
            for title in entry.find_all("div", "title"):
                for series in title.find_all("a"):
                    sid = series["href"].rsplit("/", 1)[-1]
                    suri = 'playerfm:series:' + sid
                    dirs.append(Ref.directory(uri=suri, name=series.text))
        return dirs

    def get_series_entries(self, uri):
        episodes = []
        r = self.s.get("https://player.fm/series/" + uri.rsplit(':', 1)[-1])
        soup = BeautifulSoup(r.text, "html.parser")

        for episode in soup.find_all(
                    "div", "active episode micro paused record"):
            euri = 'playerfm:episode:' + episode["data-id"]
            episodes.append(Ref.track(uri=euri, name=episode["data-title"]))
        return episodes

    def get_subscribed_podcasts(self):
        r = self.s.get("https://player.fm/ohporter/subs")

        soup = BeautifulSoup(r.text, "html.parser")

        subscribed = []
        for episode in soup.find_all(
                "div", "active episode micro paused record"):
            subscribed.append(self.get_episode_info(episode["data-id"]))
        return subscribed

    def get_episode_info(self, episode_id):
        r = self.s.get(url="https://player.fm/episodes/" +
                       episode_id + ".json")
        return r.json()

    def get_stream_url(self, episode_id):
        episode = self.get_episode_info(episode_id)
        return episode["url"]
