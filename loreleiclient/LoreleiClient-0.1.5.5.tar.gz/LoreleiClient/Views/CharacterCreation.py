from LoreleiClient.Views.Common import UIView
from LoreleiClient.UIObjects.Input import Label, Dropdown, IntValueBox, LabelRightAligned, Box, \
    ObservableValue, ParagraphBox, Button, ConditionalUI, Image
from LoreleiClient.Images.Manager import ImageManager
from LoreleiLib.Packets.CharacterCreation import ClassOptions, RaceOptions, OptionsRequest, RaceSelection, \
    ClassSelection, CharacterSummaryRequest, CharacterSummaryResponse, CharacterSummaryBackRequest, \
    CharacterSummaryBackResponse, ClassEquipment
from LoreleiClient.Settings.Screen import ScreenSettings
from LoreleiClient.Views.Modules.Attributes import AttributeComponent
from LoreleiClient.Views.Modules.Equipment import EquipmentComponent
from LoreleiLib.Character import Character, CharacterClass, CharacterRace
from LoreleiLib.Objects import EquipmentSlot
from LoreleiLib.Packets.View import ViewType


class CharacterCreationView(UIView):

    def __init__(self, character=None, connection=None):
        # Type: () -> None
        self.notification = None
        self.classes = [] # type: list<CharacterClass>
        self.races = [] # type: list<CharacterRace>
        if character is None:
            character = Character('', None, None)
        self.character = character
        self.attributes = AttributeComponent(44, 140, self.character) # 44 + 180 = 224
        self.equipment = EquipmentComponent(630, 70, self.character)
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

            self.makeDropDowns(124, 70)

            self.add_ui_object(ParagraphBox(260, 70, 350, 80, 3, "Race Description", self.raceDescription, fontSize=24)) # 260 + 350 = 610
            self.add_ui_object(ParagraphBox(260, 160, 350, 250, 3, "Class Description", self.classDescription, fontSize=24))

            self.add_ui_object(ConditionalUI(Button(ScreenSettings.SCREEN_WIDTH-90, ScreenSettings.SCREEN_HEIGHT-70, 40, 20, "Continue", self.requestSummary), self.showNextButton))

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
        self.connection.sendLine(RaceSelection(value))

    def setClass(self, value):
        self.character.character_class = value
        self.rebuildCharacter()
        self.connection.sendLine(ClassSelection(value))

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

    def requestSummary(self):
        self.connection.sendLine(CharacterSummaryRequest())

    def getData(self):
        self.connection.sendLine(OptionsRequest())
        self.rebuildCharacter()

    def showNextButton(self):
        return self.character.character_class is not None and self.character.character_race is not None

    def notification_callback(self):
        self.remove_ui_object(self.notification)
        self.notification = None

    def handle_data(self, data):
        if isinstance(data, ClassOptions):
            # print "Got Classes"
            self.classes = data.classes
        elif isinstance(data, RaceOptions):
            # print "Got Races"
            self.races = data.races
        elif isinstance(data, ClassEquipment):
            print "Got Class Equipment"
            self.character.equipment = data.equipment
            self.equipment.update()
        elif isinstance(data, CharacterSummaryResponse):
            return CharacterSummaryView(data.character, self.connection)

        if len(self.races) > 0 and len(self.classes) > 0:
            self.makeView()


class CharacterSummaryView(UIView):

    def __init__(self, character, connection):
        # Type: () -> None
        self.notification = None
        self.equipmentImages = {}
        self.character = character
        self.attributes = AttributeComponent(44, 148, character)
        self.equipment = EquipmentComponent(250, 100, character)
        super(CharacterSummaryView, self).__init__(self.makeView, ViewType.CharacterCreation, connection)

    def makeView(self):
        print "Summary, Make View"
        if self.connection is None:
            return
        else:
            labelX = 50
            intValueX = 138
            statSpacing = 20

            self.add_ui_object(Label(20, 20, "Character Summary", 42))
            self.add_ui_object(LabelRightAligned(labelX, 70, 80, 20, "Name :", fontSize=24))
            self.add_ui_object(Label(intValueX, 70, self.character.name, fontSize=24))
            self.add_ui_object(LabelRightAligned(labelX, 90, 80, 20, "Race :", fontSize=24))
            self.add_ui_object(Label(intValueX, 90, self.character.character_race.name, fontSize=24))
            self.add_ui_object(LabelRightAligned(labelX, 110, 80, 20, "Class :", fontSize=24))
            self.add_ui_object(Label(intValueX, 110, self.character.character_class.name, fontSize=24))

            self.add_ui_object(self.attributes)
            self.add_ui_object(self.equipment)

            self.add_ui_object(Button(50, ScreenSettings.SCREEN_HEIGHT-70, 40, 20, "Back", self.back))
            self.add_ui_object(Button(ScreenSettings.SCREEN_WIDTH-90, ScreenSettings.SCREEN_HEIGHT-70, 40, 20, "Finish", self.finish))

            #self.add_ui_object(Image(600, 400, "sword"))

    def loadImages(self):
        imageManager = ImageManager()
        self.equipmentImages[EquipmentSlot.Main_Hand] = imageManager.Images["sword"]
        self.equipmentImages[EquipmentSlot.Off_Hand] = imageManager.Images["shield"]


    def getData(self):
        self.makeView()

    def handle_data(self, data):
        if isinstance(data, CharacterSummaryBackResponse):
            return CharacterCreationView(data.character, self.connection)

    def back(self):
        self.connection.sendLine(CharacterSummaryBackRequest())

    def finish(self):
        pass