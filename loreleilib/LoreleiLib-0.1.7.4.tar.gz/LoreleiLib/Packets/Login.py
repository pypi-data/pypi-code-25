from LoreleiLib.Packets.Common import Packet, PacketResult


# Server Data
class LoginAttemptResponse(PacketResult):

    def __init__(self, success, message=None):
        super(LoginAttemptResponse, self).__init__(success, message)


class AccountCreateResponse(PacketResult):
    def __init__(self, success, message=None):
        super(AccountCreateResponse, self).__init__(success, message)


# Client Requests
class LoginAttemptRequest(Packet):

    def __init__(self, username, password):
        self.username = username
        self.password = password


class AccountCreateRequest(Packet):

    def __init__(self, username, password):
        self.username = username
        self.password = password



