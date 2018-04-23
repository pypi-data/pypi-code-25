class TelegramUser:
    '''
    Telegram User reference
    https://core.telegram.org/bots/api#user
    '''

    platform = 'telegram'

    def __init__(self, sender):
        self.id = sender['id']
        self.first_name = sender['first_name']
        self.last_name = sender.get('last_name')
        self.username = sender.get('username')
        self.language = sender.get('language_code')

    def __str__(self):
        s = '{u.first_name}'
        if self.last_name:
            s += ' {u.last_name}'

        s += ' ({u.id})'

        return s.format(u=self)


class TelegramChat:
    '''
    Telegram Chat reference
    https://core.telegram.org/bots/api#chat
    '''
    def __init__(self, chat):
        self.id = chat['id']
        self.type = chat['type']
        self.title = chat.get('title')
        self.username = chat.get('username')

    def __str__(self):
        s = '{u.id}'
        if self.title:
            s += ' {u.title}'
        if self.username:
            s += ' {u.username}'

        return s.format(u=self)

