from LoreleiClient.Views.Modules.Common import Component


class VitalBarsModule(Component):

    def __init__(self, x, y):
        super(VitalBarsModule, self).__init__(x, y, self.makeView)

    def makeView(self):
        pass