from LoreleiClient.Views.Common import UIView
from LoreleiLib.Packets.View import ViewType
from LoreleiClient.UIObjects.Input import Label
from LoreleiClient.Views.Modules.Chat import ChatModule
from LoreleiClient.Settings.Screen import ScreenSettings
import pygame


class GameView(UIView):

    def __init__(self, connection):
        self.chatModule = ChatModule(0, ScreenSettings.SCREEN_HEIGHT-330, connection)
        super(GameView, self).__init__(self.makeView, ViewType.Game, connection)

    def makeView(self):
        if self.connection is not None:
            self.add_ui_object(self.chatModule)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and self.chatModule.isTyping():
                self.chatModule.handle_event(event)
            else:
                super(GameView, self).handle_events([event])

    def handle_data(self, data):
        self.chatModule.handleData(data)