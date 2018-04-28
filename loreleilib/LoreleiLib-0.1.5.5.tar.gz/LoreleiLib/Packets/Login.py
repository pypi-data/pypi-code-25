from LoreleiLib.Packets.Common import Packet, PacketResult


# Server Data
class LoginResult(PacketResult):

    def __init__(self, success, message=None):
        super(LoginResult, self).__init__(success, message)


class AccountCreateResult(PacketResult):
    def __init__(self, success, message=None):
        super(AccountCreateResult, self).__init__(success, message)


# Client Requests
class LoginAttempt(Packet):

    def __init__(self, username, password):
        self.username = username
        self.password = password


class AccountCreateAttempt(Packet):

    def __init__(self, username, password):
        self.username = username
        self.password = password



