from models.interfaces import Interface, OutputLine, OutputSignal, InputLine, InputSignal
import math
from typing import List, Type, Any


class Group(Interface):
    def _set_mandatory(self)->None:
        pass

    def __init__(self, name: str)->None:
        super().__init__()
        self.items: List[Any] = []
        self.group_name = name
        self.payload_size = 0

    def add_item(self, item :str)->None:
        self.items.append(item)

    def get_payload_size(self)-> int:
        if self.payload_size == 0:
            for item in self.items:
                if item.signal_type == 'Boolean':
                    size = int(item.signal_position)
                else:
                    size = int(item.signal_nb_of_bit)

                tmp_payload = int(item.signal_address) * 8 + size
                self.payload_size = max(self.payload_size, tmp_payload)
        return self.payload_size

    def get_payload_size_byte(self)-> int:
        return math.ceil(self.get_payload_size() / 8)


class MEM_INPUT_GROUP(Group):
    def __init__(self, name)->None:
        super().__init__(name)
        self.name = 'MEM_INPUT_GROUP'


class MEM_OUTPUT_GROUP(Group):
    def __init__(self, name:str)->None:
        super().__init__(name)
        self.name = 'MEM_OUTPUT_GROUP'


class MEM_OUTPUT_PORT(OutputLine):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.mem_port_id = ''
        self.mem_port_name = ''
        self.mem_port_type = ''
        self.max_port_size = ''
        self.port_characteristic = ''
        self.buffer_size = ''
        self.queue_size = ''

    def _set_mandatory(self)->None:
        pass

    def get_name(self)-> str:
        return self.mem_port_id


class MEM_OUTPUT_MESSAGE(OutputSignal):

    def __init__(self)->None:
        super().__init__()

        self.name = ''
        self.application_name = ''
        self.associated_mem_port_id = ''
        self.message_name = ''
        self.message_length = ''
        self.message_transmission_rate = ''
        self.fds_name = ''
        self.fs_address_in_the_message = ''
        self.parameter_type = ''
        self.parameter_local_name = ''
        self.local_name_description = ''
        self.signal_name = ''
        self.signal_nb_of_bit = ''
        self.signal_address = ''
        self.signal_position = ''
        self.float_operational_unit = ''
        self.integer_operational_unit = ''

    def _set_mandatory(self)-> None:
        self._add_mandatory('application_name')


    def get_refresh_period(self)-> int:
        return 0#self.port_refresh_rate

    def get_message_length(self)-> Any:
        return self.message_length

    def get_associated_name(self):
        return self.associated_mem_port_id

    def has_parent(self):
        return 'MEM_OUTPUT_PORT'

    def can_group(self):
        return MEM_OUTPUT_GROUP

    def get_group_parameter(self)-> str:
        return self.message_name


class MEM_INPUT_PORT(InputLine):

    def __init__(self)-> None:
        super().__init__()
        self.name = ''
        self.mem_port_id = ''
        self.mem_port_name = ''
        self.mem_port_type = ''
        self.max_port_size = ''
        self.port_characteristic = ''
        self.buffer_size = ''
        self.queue_size = ''

    def _set_mandatory(self)-> None:
        pass

    def get_name(self)-> str:
        return self.mem_port_id


class MEM_INPUT_MESSAGE(InputSignal):

    def __init__(self)-> None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.associated_mem_port_id = ''
        self.message_name = ''
        self.message_length = ''
        self.message_refresh_rate = ''
        self.fds_name = ''
        self.fs_address_in_the_message = ''
        self.parameter_type = ''
        self.parameter_local_name = ''
        self.local_name_description = ''
        self.signal_name = ''
        self.signal_nb_of_bit = ''
        self.signal_address = ''
        self.signal_position = ''
        self.float_operational_unit = ''
        self.integer_operational_unit = ''

    def _set_mandatory(self)-> None:
        self._add_mandatory('application_name')

    def get_refresh_period(self):
        return self.message_refresh_rate

    def get_message_length(self):
        return self.message_length

    def get_associated_name(self):
        return self.associated_mem_port_id

    def has_parent(self):
        return 'MEM_INPUT_PORT'

    def can_group(self):
        return MEM_INPUT_GROUP

    def get_group_parameter(self)->str:
        return self.message_name

