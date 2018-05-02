from LoreleiClient.Views.Common import UIView
from LoreleiLib.Packets.View import ViewType
from LoreleiClient.UIObjects.Input import Label


class GameView(UIView):

    def __init__(self, connection):
        super(GameView, self).__init__(self.makeView, ViewType.Game, connection)

    def makeView(self):
        if self.connection is not None:
            self.add_ui_object(Label(20, 20, "GAME MODE", 42))