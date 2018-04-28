from LoreleiLib.Packets.Common import Packet, PacketResult


# Server Data
class RaceSelectionResult(PacketResult):

    def __init__(self, success, message=None):
        super(RaceSelectionResult, self).__init__(success, message)


class ClassSelectionResult(PacketResult):
    # Packet from server which contains Race Options for the player
    def __init__(self, success, message=None):
        super(ClassSelectionResult, self).__init__(success, message)


class RaceOptions(Packet):
    # Packet from server which contains Race Options for the player
    def __init__(self, races):
        self.races = races


class ClassOptions(Packet):
    # Packet from server which contains Class Option for the player
    def __init__(self, classes):
        self.classes = classes


class CharacterSummaryResponse(Packet):
    # Packet from server which provides a fully fleshed out character to view
    def __init__(self, character):
        self.character = character


class CharacterSummaryBackResponse(Packet):
    def __init__(self, character):
        self.character = character


class ClassEquipment(Packet):
    def __init__(self, equipment):
        self.equipment = equipment

# Client Requests
class OptionsRequest(Packet):

    # Packet from client to request Race/Class options
    def __init__(self):
        pass


class CharacterSummaryRequest(Packet):

    # Packet from client to request Character Summary View
    def __init__(self):
        pass


class CharacterSummaryBackRequest(Packet):
    def __init__(self):
        pass


class RaceSelection(Packet):

    # Packet from client to set Race on the Server
    def __init__(self, characterRace):
        self.characterRace = characterRace


class ClassSelection(Packet):

    # Packet from client to set Class on the Server
    def __init__(self, characterClass):
        self.characterClass = characterClass
