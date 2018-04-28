import re

from .cgit import CGit


class KDEGit(CGit):
    name = 'kdegit'

    def first_request(self, data):
        if not any(data[k] is not None for k in ('commit', 'tag')):
            data['tag'] = '^(?:v|{}-)?(\\d+(?:\\.\\d+)*' \
                          '(?:\\.(?:\\d|[0-8]\\d+)))$'.format(
                                re.escape(data['id']))
        return 'https://cgit.kde.org/' + data['id'] + '.git' + (
            '/log/' if data.get('commit', None) else '/refs/tags')
