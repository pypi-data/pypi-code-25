from Common import UIView
from LoreleiClient.UIObjects.Input import Label, Dropdown, IntValueBox, LabelRightAligned, Box, \
    ObservableValue, ParagraphBox, Button, ConditionalUI
from LoreleiLib.Packets.CharacterCreation import ClassOptions, RaceOptions, OptionsRequest, RaceSelection, \
    ClassSelection, CharacterSummaryRequest, CharacterSummaryResponse, CharacterSummaryBackRequest, \
    CharacterSummaryBackResponse
from LoreleiLib.Character import Character, CharacterClass, CharacterRace


class CharacterCreationView(UIView):

    def __init__(self, character=None):
        # Type: () -> None
        self.notification = None
        self.classes = [] # type: list<CharacterClass>
        self.races = [] # type: list<CharacterRace>
        if character is None:
            character = Character('', None, None)
        self.character = character
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

        super(CharacterCreationView, self).__init__(self.makeView)

    def makeView(self):
        if self.connection is None:
            return
        else:
            labelX = 50
            intValueX = 138
            statSpacing = 24

            self.add_ui_object(Label(20, 20, "Character Creation", 42))
            self.add_ui_object(LabelRightAligned(labelX, 70, 80, 20, "Race :", ))
            self.add_ui_object(LabelRightAligned(labelX, 100, 80, 20, "Class :", ))

            y = 140

            self.add_ui_object(Box(labelX-6, y, 140, 200, 3, "Attributes"))
            y += 10
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Strength :"))
            self.add_ui_object(IntValueBox(intValueX, y, 30, 20, self.strength))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Constitution :"))
            self.add_ui_object(IntValueBox(intValueX, y, 30, 20, self.constitution))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Dexterity :"))
            self.add_ui_object(IntValueBox(intValueX, y, 30, 20, self.dexterity))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Agility :"))
            self.add_ui_object(IntValueBox(intValueX, y, 30, 20, self.agility))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Wisdom :"))
            self.add_ui_object(IntValueBox(intValueX, y, 30, 20, self.wisdom))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Intelligence :"))
            self.add_ui_object(IntValueBox(intValueX, y, 30, 20, self.intelligence))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Charisma :"))
            self.add_ui_object(IntValueBox(intValueX, y, 30, 20, self.charisma))

            self.makeDropDowns(intValueX)

            self.add_ui_object(ParagraphBox(300, 50, 250, 80, 3, "Race Description", self.raceDescription))
            self.add_ui_object(ParagraphBox(300, 140, 250, 200, 3, "Class Description", self.classDescription))

            self.add_ui_object(ConditionalUI(Button(600-90, 360, 40, 20, "Continue", self.requestSummary), self.showNextButton))

    def makeDropDowns(self, x):
        classDropdown = Dropdown(x, 100, "Select", self.classes, 'name', self.setClass, minWidth=100)
        classDropdown.option = self.character.character_class

        raceDropdown = Dropdown(x, 70, "Select", self.races, 'name', self.setRace, minWidth=100)
        raceDropdown.option = self.character.character_race
        self.add_ui_object(classDropdown)
        self.add_ui_object(raceDropdown)

    def setRace(self, value):
        self.character.character_race = value
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
            self.raceDescription.setValue(self.character.character_race.description)
        if self.character.character_class is not None:
            self.classDescription.setValue(self.character.character_class.description)

    def requestSummary(self):
        self.connection.sendLine(CharacterSummaryRequest())

    def getData(self):
        self.connection.sendLine(OptionsRequest())
        self.rebuildCharacter()
        self.makeView()

    def showNextButton(self):
        return self.character.character_class is not None and self.character.character_race is not None

    def notification_callback(self):
        self.remove_ui_object(self.notification)
        self.notification = None

    def handle_data(self, data):
        if isinstance(data, ClassOptions):
            self.classes = data.classes
        elif isinstance(data, RaceOptions):
            self.races = data.races
        elif isinstance(data, CharacterSummaryResponse):
            return CharacterSummaryView(data.character)

        if len(self.races) > 0 and len(self.classes) > 0:
            self.makeView()


class CharacterSummaryView(UIView):

    def __init__(self, character):
        # Type: () -> None
        self.notification = None
        self.character = character
        super(CharacterSummaryView, self).__init__(self.makeView)

    def makeView(self):
        if self.connection is None:
            return
        else:
            labelX = 50
            intValueX = 138
            statSpacing = 20

            self.add_ui_object(Label(20, 20, "Character Summary", 42))
            self.add_ui_object(LabelRightAligned(labelX, 70, 80, 20, "Name :", ))
            self.add_ui_object(Label(intValueX, 70, self.character.name))
            self.add_ui_object(LabelRightAligned(labelX, 90, 80, 20, "Race :", ))
            self.add_ui_object(Label(intValueX, 90, self.character.character_race.name))
            self.add_ui_object(LabelRightAligned(labelX, 110, 80, 20, "Class :", ))
            self.add_ui_object(Label(intValueX, 110, self.character.character_class.name))

            y = 140
            self.add_ui_object(Box(labelX - 6, y, 140, 160, 3, "Attributes"))
            y += 10
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Strength :"))
            self.add_ui_object(Label(intValueX, y, self.character.attributes.strength))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Constitution :"))
            self.add_ui_object(Label(intValueX, y, self.character.attributes.constitution))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Dexterity :"))
            self.add_ui_object(Label(intValueX, y, self.character.attributes.dexterity))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Agility :"))
            self.add_ui_object(Label(intValueX, y, self.character.attributes.agility))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Wisdom :"))
            self.add_ui_object(Label(intValueX, y, self.character.attributes.wisdom))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Intelligence :"))
            self.add_ui_object(Label(intValueX, y, self.character.attributes.intelligence))
            y += statSpacing
            self.add_ui_object(LabelRightAligned(labelX, y, 80, 20, "Charisma :"))
            self.add_ui_object(Label(intValueX, y, self.character.attributes.charisma))

            self.add_ui_object(Button(50, 360, 40, 20, "Back", self.back))
            self.add_ui_object(Button(600-90, 360, 40, 20, "Finish", self.finish))

    def getData(self):
        self.makeView()

    def handle_data(self, data):
        if isinstance(data, CharacterSummaryBackResponse):
            return CharacterCreationView(data.character)

    def back(self):
        self.connection.sendLine(CharacterSummaryBackRequest())

    def finish(self):
        pass