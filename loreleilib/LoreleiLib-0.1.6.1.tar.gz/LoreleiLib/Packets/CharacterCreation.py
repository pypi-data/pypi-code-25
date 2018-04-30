from LoreleiLib.Packets.Common import Packet, PacketResult


# Server Data
class CreationOptionsResponse(Packet):

    def __init__(self, races, classes):
        self.races = races
        self.classes = classes


class CharacterCheckResponse(Packet):

    def __init__(self, character):
        self.character = character


class CharacterFinishResponse(Packet):
    def __init__(self):
        pass


# Client Requests
class OptionsRequest(Packet):

    # Packet from client to request Race/Class options
    def __init__(self):
        pass


class CharacterSummaryBackRequest(Packet):
    def __init__(self):
        pass


class RaceSelectionRequest(Packet):

    # Packet from client to set Race on the Server
    def __init__(self, characterRace):
        self.characterRace = characterRace


class ClassSelectionRequest(Packet):

    # Packet from client to set Class on the Server
    def __init__(self, characterClass):
        self.characterClass = characterClass


class CharacterCheckRequest(Packet):

    def __init__(self):
        pass


class CharacterFinishRequest(Packet):

    def __init__(self):
        pass