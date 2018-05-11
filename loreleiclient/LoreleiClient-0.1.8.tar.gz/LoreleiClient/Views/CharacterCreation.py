from LoreleiClient.Views.Common import UIView
from LoreleiClient.UIObjects.Input import Label, Dropdown, IntValueBox, LabelRightAligned, Box, \
    ObservableValue, ParagraphBox, Button, ConditionalUI, Image, Notification
from LoreleiClient.Images.Manager import ImageManager
from LoreleiLib.Packets.CharacterCreation import OptionsRequest, RaceSelectionRequest, \
    ClassSelectionRequest, CharacterCheckResponse, CreationOptionsResponse, CharacterFinishRequest, \
    CharacterFinishResponse
from LoreleiClient.Settings.Screen import ScreenSettings
from LoreleiClient.Views.Modules.Attributes import AttributeComponent
from LoreleiClient.Views.Modules.Equipment import EquipmentComponent
from LoreleiClient.Views.Modules.Statistics import StatisticsComponent
from LoreleiClient.Views.Game import GameView
from LoreleiLib.Character import Character, CharacterClass, CharacterRace
from LoreleiLib.Packets.View import ViewType


class CharacterCreationView(UIView):

    def __init__(self, connection=None, character=None):
        # Type: () -> None
        self.notification = None
        self.classes = [] # type: list<CharacterClass>
        self.races = [] # type: list<CharacterRace>
        if character is None:
            character = Character('', None, None)
        self.character = character
        self.attributes = AttributeComponent(54, 204, self.character) # 224 - 140 = 64
        self.equipment = EquipmentComponent(640, 70, self.character) # 444 bot, 940 right
        self.statistics = StatisticsComponent(54, 464, self.character) # 940-54 = 886, 464-240 = 224
        self.strength = ObservableValue(self.character.attributes.strength)
        self.constitution = ObservableValue(self.character.attributes.constitution)
        self.dexterity = ObservableValue(self.character.attributes.dexterity)
        self.agility = ObservableValue(self.character.attributes.agility)
        self.wisdom = ObservableValue(self.character.attributes.wisdom)
        self.intelligence = ObservableValue(self.character.attributes.intelligence)
        self.charisma = ObservableValue(self.character.attributes.charisma)
        self.raceDescription = ObservableValue('Select a Race to see its description')
        self.classDescription = ObservableValue('Select a Class to see its description')

        if self.character.character_race is not None:
            self.raceDescription.setValue(self.character.character_race.description)
        if self.character.character_class is not None:
            self.classDescription.setValue(self.character.character_class.description)

        super(CharacterCreationView, self).__init__(self.makeView, ViewType.CharacterCreation, connection)

    def makeView(self):
        if self.connection is not None:
            self.add_ui_object(Label(20, 20, "Character Creation", 42))
            self.add_ui_object(self.attributes)
            self.add_ui_object(self.equipment)
            self.add_ui_object(self.statistics)

            self.makeDropDowns(124, 102)

            self.add_ui_object(ParagraphBox(260, 70, 350, 120, 3, "Race Description", self.raceDescription, fontSize=24)) # 260 + 350 = 610
            self.add_ui_object(ParagraphBox(260, 200, 350, 244, 3, "Class Description", self.classDescription, fontSize=24))

            self.add_ui_object(ConditionalUI(Button(ScreenSettings.SCREEN_WIDTH-90, ScreenSettings.SCREEN_HEIGHT-50, 40, 24, "Finish", self.finish, fontSize=24), self.showNextButton))

    def makeDropDowns(self, x, y):
        self.add_ui_object(LabelRightAligned(x-88, y, 80, 20, "Race :", fontSize=24))
        self.add_ui_object(LabelRightAligned(x-88, y+30, 80, 20, "Class :", fontSize=24))
        classDropdown = Dropdown(x, y+30, "Select", self.classes, 'name', self.setClass, minWidth=100, fontSize=24)
        classDropdown.option = self.character.character_class

        raceDropdown = Dropdown(x, y, "Select", self.races, 'name', self.setRace, minWidth=100, fontSize=24)
        raceDropdown.option = self.character.character_race
        self.add_ui_object(classDropdown)
        self.add_ui_object(raceDropdown)

    def setRace(self, value):
        self.character.changeRace(value)
        self.rebuildCharacter()
        self.connection.sendLine(RaceSelectionRequest(value))

    def setClass(self, value):
        self.character.character_class = value
        self.rebuildCharacter()
        self.connection.sendLine(ClassSelectionRequest(value))

    def rebuildCharacter(self):
        self.character.buildStats()
        self.strength.setValue(self.character.attributes.strength)
        self.constitution.setValue(self.character.attributes.constitution)
        self.dexterity.setValue(self.character.attributes.dexterity)
        self.agility.setValue(self.character.attributes.agility)
        self.wisdom.setValue(self.character.attributes.wisdom)
        self.intelligence.setValue(self.character.attributes.intelligence)
        self.charisma.setValue(self.character.attributes.charisma)

        if self.character.character_race is not None:
            self.raceDescription.setValue(
                self.character.character_race.description)
        if self.character.character_class is not None:
            self.classDescription.setValue(self.character.character_class.getFullDescription())

    def getData(self):
        self.connection.sendLine(OptionsRequest())
        self.rebuildCharacter()

    def showNextButton(self):
        return self.character.character_class is not None and self.character.character_race is not None

    def notification_callback(self):
        self.remove_ui_object(self.notification)
        self.notification = None

    def handle_data(self, data):
        if isinstance(data, CreationOptionsResponse):
            self.races = data.races
            self.classes = data.classes
        elif isinstance(data, CharacterCheckResponse):
            self.removeAll()
            self.character = data.character
            self.attributes = AttributeComponent(54, 204, self.character)  # 224 - 140 = 64
            self.equipment = EquipmentComponent(640, 70, self.character)  # 444 bot, 940 right
            self.statistics = StatisticsComponent(54, 464, self.character)  # 940-54 = 886, 464-240 = 224
            self.makeView()
        elif isinstance(data, CharacterFinishResponse):
            if data.success:
                return GameView(self.connection)
            else:
                self.add_ui_object(Notification(data.message, self.notification_callback))

        if len(self.races) > 0 and len(self.classes) > 0:
            self.makeView()

    def finish(self):
        self.connection.sendLine(CharacterFinishRequest())