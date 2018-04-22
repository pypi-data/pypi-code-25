import re

from mindscli.utils import get_terminal_size


class Text:
    sep = '―'
    sepl = '―' * 3
    tsize = get_terminal_size()
    tsize_h, tsize_v = tsize
    row_sep = '■' * tsize_h


class Comment(Text):
    """container class for minds comment"""

    def __init__(self, body, guid, username, up, down):
        self.body = body
        self.guid = guid
        self.username = username
        self.up = up
        self.down = down

    def get_footer(self):
        footer = f"{self.sepl}{self.username}{self.sepl}{self.up}/{self.down}{{}}{self.guid}{self.sepl}"
        footer = footer.format(self.sep * (self.tsize_h - len(footer) + 2))
        return f'{footer}\n{self.row_sep}'

    def __str__(self):
        return f'{self.body}\n{self.get_footer()}'

    @classmethod
    def from_api_data(cls, data):
        return cls(
            body=data['description'],
            guid=data['guid'],
            username=data['ownerObj']['username'],
            up=data['thumbs:up:count'],
            down=data['thumbs:down:count'],
        )


class Notification(Text):
    """container class for minds notification"""
    urlf = 'https://minds.com/newsfeed/{}'.format
    event_map = {
        'like': 'liked',
        'comment': 'commented on',
    }

    def __init__(self, type, guid, description, event, from_name, from_guid, timestamp):
        self.type = type
        self.guid = guid
        self.description = description
        self.event = event
        self.event_human = self.event_map.get(self.event, self.event)
        self.from_name = from_name
        self.from_guid = from_guid
        self.timestamp = timestamp
        self.url = self.urlf(guid)

    def __str__(self):
        row_len = self.tsize[0]
        header_prefix = f'@{self.from_name}: {self.event_human} {self.type}'
        header_sep = ((row_len - len(header_prefix) - len(self.url)) * self.sep)
        header = f'{header_prefix}{header_sep}{self.url}'
        body = self.description
        footer = '■' * row_len
        return '\n'.join(text.strip() for text in [header, body, footer] if text.strip()).strip()

    @classmethod
    def from_api_data(cls, data):
        kwargs = {
            'type': data['type'],
            'guid': data['guid'],
            'description': data['description'],
            'event': data['notification_view'],
            'from_name': data['from']['username'],
            'from_guid': data['from_guid'],
            'timestamp': data['time_created'],
        }
        return cls(**kwargs)


class Post(Text):
    """
    Container class for Minds post object:
    """
    body_limit = 300

    def __init__(self, title, body, username, up, down, comments, reminds, guid, custom_data):
        self.title = title
        self.body = body
        self.body_short = body[:self.body_limit - 3] + '...' if len(body) > self.body_limit else body
        self.username = username
        self.up = up
        self.down = down
        self.comments = comments
        self.reminds = reminds
        self.guid = guid
        self.url = f'https://minds.com/newsfeed/{guid}'
        self.custom_data = custom_data or []

    def get_footer(self):
        row_len = self.tsize[0]
        _footer_len = len(self.username) + len(str(self.up) + str(self.down) + str(self.comments) + str(self.reminds))
        _footer_len += 3 + 3 + 3 + 3 + 5
        _footer_mid = f'{self.url:{self.sep}^{row_len - _footer_len}}'
        footer = f"{self.sepl}{self.username}{self.sepl}{self.up}/{self.down}{_footer_mid}C:{self.comments}{self.sepl}R:{self.reminds}{self.sepl}"
        footer += '\n' + '■' * row_len
        return footer

    def __str__(self):
        row_len = self.tsize[0]
        footer = self.get_footer()
        # body
        custom_data = '\n'.join([d['src'] for d in self.custom_data])
        body = f'{self.body_short}\n{custom_data}'.strip()
        # header
        header = f'{self.title.strip()}\n{self.sep * row_len}' if self.title.strip() else ''

        text = f'{header}\n{body}\n{footer}'
        return re.sub('\n{3,}', '\n', text.strip())

    @classmethod
    def from_api_data(cls, data):
        body = '\n'.join(
            [(data['blurb'] or ''),
             (data['message'] or '')]
        )
        kwargs = {
            'username': data['ownerObj']['username'],
            'title': data['title'] or '',
            'body': body,
            'up': data['thumbs:up:count'],
            'down': data['thumbs:down:count'],
            'comments': data['comments:count'],
            'reminds': data['reminds'],
            'guid': data['guid'],
            'custom_data': data.get('custom_data', [])
        }
        return cls(**kwargs)
