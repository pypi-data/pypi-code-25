from LoreleiClient.Views.Modules.Common import Component
from LoreleiLib.Packets.Game.Room import RoomDetails, RoomChange
from LoreleiClient.UIObjects.Input import Button, Box, ParagraphBox, ObservableValue
from LoreleiLib.Map import MapExitDescriptions, MapDirection
from LoreleiLib.StringHelpers import wrap_multi_line
import pygame as pg


class MovementButton(Button):

    def __init__(self, x, y, w, h, text, description, callback, fontSize=18, doHoverVisual=None):
        self.description = description
        self.font = pg.font.Font(None, fontSize)
        self.fontSize = fontSize
        self.hover = False
        self.hoverover = None
        self.observable = ObservableValue(description)
        super(MovementButton, self).__init__(x, y, w, h, text, callback, fontSize, doHoverVisual)
        self.setup()

    def setup(self):
        lines = wrap_multi_line(self.description, self.font, 200)
        width = 80
        height = 0
        for line in lines:
            linesize = self.font.size(line)
            if width < linesize[0]:
                width = linesize[0]
            height += self.fontSize

        self.hoverover = ParagraphBox(self.x+20, self.y+20, width, height, 3, "Exit Description", self.observable)

    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            if self.rect is not None:
                if self.rect.collidepoint(event.pos):
                    self.hover = True
                else:
                    self.hover = False

        super(MovementButton, self).handle_event(event)

    def draw(self, screen):
        super(MovementButton, self).draw(screen)

        if self.hover:
            self.hoverover.draw(screen)


class MovementModule(Component):

    def __init__(self, x, y, connection, roomDetails=None):
        self.connection = connection
        self.roomDetails = roomDetails
        super(MovementModule, self).__init__(x, y, self.makeView)

    def makeView(self):
        width = 40
        height = 30
        if self.roomDetails is not None:
            exitDetails = self.roomDetails.exitDetails # type: MapExitDescriptions
            if exitDetails is not None:
                if exitDetails.exits[MapDirection.East] is not None:
                    self.add_ui_object(MovementButton(self.x + width*2, self.y + height, width, height, "E",
                                                      exitDetails.descriptions[MapDirection.East], self.goEast,
                                                      fontSize=28, doHoverVisual=False))
                if exitDetails.exits[MapDirection.South] is not None:
                    self.add_ui_object(MovementButton(self.x + width, self.y + height*2, width, height, "S",
                                                      exitDetails.descriptions[MapDirection.South], self.goSouth,
                                                      fontSize=28, doHoverVisual=False))
                if exitDetails.exits[MapDirection.North] is not None:
                    self.add_ui_object(MovementButton(self.x + width, self.y, width, height, "N",
                                                      exitDetails.descriptions[MapDirection.North], self.goNorth,
                                                      fontSize=28, doHoverVisual=False))
                if exitDetails.exits[MapDirection.West] is not None:
                    self.add_ui_object(MovementButton(self.x + 0, self.y + height, width, height, "W",
                                                      exitDetails.descriptions[MapDirection.West], self.goWest,
                                                      fontSize=28, doHoverVisual=False))

    def goNorth(self):
        self.connection.sendLine(RoomChange(MapDirection.North))

    def goSouth(self):
        self.connection.sendLine(RoomChange(MapDirection.South))

    def goWest(self):
        self.connection.sendLine(RoomChange(MapDirection.West))

    def goEast(self):
        self.connection.sendLine(RoomChange(MapDirection.East))

    def rebuild(self, roomDetails):
        # type: (RoomDetails) -> None
        self.roomDetails = roomDetails

        self.removeAll()
        self.makeView()