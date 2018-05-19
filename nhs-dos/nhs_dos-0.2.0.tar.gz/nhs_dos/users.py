class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User {0}>'.format(self.username)

    def __str__(self):
        return '<User {0}>'.format(self.username)
