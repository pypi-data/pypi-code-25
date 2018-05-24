import json


class Message:
    def __init__(self, command, data):
        self.command = command
        self.data = data

    def json(self):
        return json.dumps({
            'message': {
                'command': self.command,
                'data': self.data
            }
        })

    def encoded(self):
        return bytes(self.json(), 'ascii')

    @staticmethod
    def from_json(data):
        d = json.loads(data)['message']
        return Message(d['command'], d['data'])
