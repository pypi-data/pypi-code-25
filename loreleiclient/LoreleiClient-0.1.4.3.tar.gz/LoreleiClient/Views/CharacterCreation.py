from Common import UIView
from LoreleiClient.UIObjects.Input import Label, Dropdown, IntObservable, IntValueBox, LabelRightAligned, Box
from LoreleiLib.Packets.CharacterCreation import ClassOptions, RaceOptions, OptionsRequest
from LoreleiLib.Character import Character, CharacterClass, CharacterRace


class CharacterCreationView(UIView):

    def __init__(self):
        # Type: () -> None
        self.notification = None
        self.classes = [] # type: list<CharacterClass>
        self.races = [] # type: list<CharacterRace>
        self.character = Character('', None, None)
        self.strength = IntObservable(self.character.attributes.strength)
        self.constitution = IntObservable(self.character.attributes.constitution)
        self.dexterity = IntObservable(self.character.attributes.dexterity)
        self.agility = IntObservable(self.character.attributes.agility)
        self.wisdom = IntObservable(self.character.attributes.wisdom)
        self.intelligence = IntObservable(self.character.attributes.intelligence)
        self.charisma = IntObservable(self.character.attributes.charisma)

        super(CharacterCreationView, self).__init__(self.make_view)

    def make_view(self):
        if self.connection is None:
            return
        else:
            self.add_ui_object(Label(20, 20, "Character Creation", 36))
            self.add_ui_object(LabelRightAligned(20, 70, 80, 20, "Race :", ))
            self.add_ui_object(LabelRightAligned(20, 100, 80, 20, "Class :", ))

            self.add_ui_object(Box(14, 138, 150, 200, 3, "Attributes"))

            self.add_ui_object(LabelRightAligned(20, 150, 80, 20, "Strength :"))
            self.add_ui_object(IntValueBox(108, 150, 30, 20, self.strength))
            self.add_ui_object(LabelRightAligned(20, 174, 80, 20, "Constitution :"))
            self.add_ui_object(IntValueBox(108, 174, 30, 20, self.constitution))
            self.add_ui_object(LabelRightAligned(20, 198, 80, 20, "Dexterity :"))
            self.add_ui_object(IntValueBox(108, 198, 30, 20, self.dexterity))
            self.add_ui_object(LabelRightAligned(20, 222, 80, 20, "Agility :"))
            self.add_ui_object(IntValueBox(108, 222, 30, 20, self.agility))
            self.add_ui_object(LabelRightAligned(20, 246, 80, 20, "Wisdom :"))
            self.add_ui_object(IntValueBox(108, 246, 30, 20, self.wisdom))
            self.add_ui_object(LabelRightAligned(20, 270, 80, 20, "Intelligence :"))
            self.add_ui_object(IntValueBox(108, 270, 30, 20, self.intelligence))
            self.add_ui_object(LabelRightAligned(20, 294, 80, 20, "Charisma :"))
            self.add_ui_object(IntValueBox(108, 294, 30, 20, self.charisma))
            self.add_ui_object(Dropdown(108, 100, "Select", self.classes, 'name', self.setClass))
            self.add_ui_object(Dropdown(108, 70, "Select", self.races, 'name', self.setRace))



    def setRace(self, value):
        self.character.character_race = value
        self.rebuildCharacter()

    def setClass(self, value):
        self.character.character_class = value
        self.rebuildCharacter()

    def rebuildCharacter(self):
        self.character.buildStats()
        self.strength.setValue(self.character.attributes.strength)
        self.constitution.setValue(self.character.attributes.constitution)
        self.dexterity.setValue(self.character.attributes.dexterity)
        self.agility.setValue(self.character.attributes.agility)
        self.wisdom.setValue(self.character.attributes.wisdom)
        self.intelligence.setValue(self.character.attributes.intelligence)
        self.charisma.setValue(self.character.attributes.charisma)

    def getData(self):
        self.connection.sendLine(OptionsRequest())
        self.rebuildCharacter()

    def notification_callback(self):
        self.remove_ui_object(self.notification)
        self.notification = None

    def handle_data(self, data):
        if isinstance(data, ClassOptions):
            self.classes = data.classes
        elif isinstance(data, RaceOptions):
            self.races = data.races

        if len(self.races) > 0 and len(self.classes) > 0:
            self.make_view()