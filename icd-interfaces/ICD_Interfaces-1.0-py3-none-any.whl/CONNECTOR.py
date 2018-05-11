from models.interfaces import Interface


class CONNECTOR (Interface):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.connector_type = ''
        self.connector_name = ''
        self.connector_pin = ''
        self.connector_pin_role = ''
        self.connection_name = ''
        self.line_type = ''

    def _set_mandatory(self)->None:
        pass
