from LoreleiClient.Views.Common import UIView
from LoreleiLib.Packets.View import ViewType
from LoreleiLib.Packets.Game.Chat import ChatPacket
from LoreleiLib.Packets.Game.Room import RoomPacket, RoomDetails
from LoreleiClient.Views.Modules.Chat import ChatModule
from LoreleiClient.Views.Modules.Room import RoomModule
from LoreleiClient.Views.Modules.Movement import MovementModule
from LoreleiClient.Views.Modules.VitalBars import VitalBarsModule
from LoreleiClient.Settings.Screen import ScreenSettings
import pygame


class GameView(UIView):

    def __init__(self, connection):
        self.vitalsModule = VitalBarsModule(8, 8)
        self.chatModule = ChatModule(0, ScreenSettings.SCREEN_HEIGHT - (ChatModule.Height + ChatModule.ChatHeight), connection)
        self.roomModule = RoomModule(278, 100, connection)
        self.movementModule = MovementModule(467, 420, connection)
        super(GameView, self).__init__(self.makeView, ViewType.Game, connection)

    def makeView(self):
        if self.connection is not None:
            self.add_ui_object(self.vitalsModule)
            self.add_ui_object(self.chatModule)
            self.add_ui_object(self.roomModule)
            self.add_ui_object(self.movementModule)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and self.chatModule.isTyping():
                self.chatModule.handle_event(event)
            else:
                super(GameView, self).handle_events([event])

    def handle_data(self, data):
        if isinstance(data, ChatPacket):
            self.chatModule.handleData(data)
        elif isinstance(data, RoomPacket):
            self.roomModule.handleData(data)
            if isinstance(data, RoomDetails):
                self.movementModule.rebuild(data)