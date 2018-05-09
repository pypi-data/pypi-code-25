from . import DownloadableObj
from urllib import request
import re


class WeSing(DownloadableObj):
    def get_data(self):
        try:
            response = request.urlopen(self.web_url)
            html = response.read().decode()
            content = re.search('{"activity_id.+(?=,"lyric)', html).group()
            song_info = eval(content)
        except TimeoutError:
            raise TimeoutError('Network connection timeout.\nPlease check your network status')

        self.set_data(file_url=song_info['playurl'],
                      title=song_info['song_name'],
                      author=song_info['nick'],
                      format='.m4a')
