from Common import Packet, PacketResult


# Server Data
class RaceSelectResult(PacketResult):

    def __init__(self, success, message=None):
        super(RaceSelectResult, self).__init__(success, message)


class ClassSelectionResult(PacketResult):
    def __init__(self, success, message=None):
        super(ClassSelectionResult, self).__init__(success, message)


class RaceOptions(Packet):

    def __init__(self, races):
        self.races = races


class ClassOptions(Packet):

    def __init__(self, classes):
        self.classes = classes


# Client Requests
class OptionsRequest(Packet):

    def __init__(self):
        pass


class RaceSelection(Packet):

    def __init__(self, username, password):
        self.username = username
        self.password = password


class ClassSelection(Packet):

    def __init__(self, username, password):
        self.username = username
        self.password = password