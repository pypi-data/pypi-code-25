from models.interfaces import OutputSignal, InputSignal


class RAM_OUTPUT_MESSAGE(OutputSignal):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.ram_port_id = ''
        self.port_type = ''
        self.port_length = ''
        self.port_transmission_rate = ''
        self.fds_name = ''
        self.fs_address_in_the_message = ''
        self.parameter_type = ''
        self.parameter_local_name = ''
        self.local_name_description = ''
        self.signal_name = ''
        self.signal_nb_of_bit = ''
        self.signal_address = ''
        self.signal_position = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('application_name')
        self._add_mandatory('ram_port_id')
        self._add_mandatory('port_type')
        self._add_mandatory('port_length')
        self._add_mandatory('port_transmission_rate')
        self._add_mandatory('fds_name')
        self._add_mandatory('fs_address_in_the_message')
        self._add_mandatory('parameter_type')
        # self._add_mandatory('parameter_local_name')
        # self._add_mandatory('local_name_description')
        # self._add_mandatory('signal_name')
        self._add_mandatory('signal_nb_of_bit')
        self._add_mandatory('signal_address')
        self._add_mandatory('signal_position')


class RAM_INPUT_MESSAGE(InputSignal):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.ram_port_id = ''
        self.port_type = ''
        self.port_length = ''
        self.port_refresh_rate = ''
        self.fds_name = ''
        self.fs_address_in_the_message = ''
        self.parameter_type = ''
        self.parameter_local_name = ''
        self.local_name_description = ''
        self.signal_name = ''
        self.signal_nb_of_bit = ''
        self.signal_address = ''
        self.signal_position = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('application_name')
        self._add_mandatory('ram_port_id')
        self._add_mandatory('port_type')
        self._add_mandatory('port_length')
        self._add_mandatory('fds_name')
        self._add_mandatory('fs_address_in_the_message')
        self._add_mandatory('parameter_type')
        # self._add_mandatory('parameter_local_name')
        # self._add_mandatory('local_name_description')
        # self._add_mandatory('signal_name')
        self._add_mandatory('signal_nb_of_bit')
        self._add_mandatory('signal_address')
        self._add_mandatory('signal_position')
        self._add_mandatory('port_transmission_rate')
