from models.interfaces import Interface


class PARTITION (Interface):

    def __init__(self)-> None:
        super().__init__()
        self.name = ''
        self.partition_name = ''
        self.partition_id = ''
        self.cycle_time = ''
        self.duration = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('partition_name')
        self._add_mandatory('partition_id')
        self._add_mandatory('cycle_time')
        self._add_mandatory('duration')
