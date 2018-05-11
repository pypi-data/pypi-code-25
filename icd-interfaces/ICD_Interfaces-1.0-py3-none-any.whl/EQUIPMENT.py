from models.interfaces import Interface


class EQUIPMENT(Interface):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.equipment_name = ''
        self.description = ''
        self.type = ''
        self.emc_protection = ''
        self.zone = ''
        self.fin = ''

    def _set_mandatory(self)->None:
        pass
