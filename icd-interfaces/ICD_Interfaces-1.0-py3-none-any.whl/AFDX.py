from models.interfaces import Interface, OutputLine, OutputSignal, InputLine, InputSignal
import math
from typing import Any


class Group(Interface):
    def _set_mandatory(self) -> None:
        pass

    def __init__(self, name: str) -> None:
        super().__init__()
        self.items = []
        self.group_name = name
        self.payload_size = 0

    def add_item(self, item: str) -> None:
        self.items.append(item)

    def get_payload_size(self) -> float:
        if self.payload_size == 0:
            for item in self.items:
                if item.signal_type == 'Boolean':
                    size = int(item.signal_position)
                else:
                    size = int(item.signal_nb_of_bit)

                tmp_payload = int(item.signal_address) * 8 + size
                self.payload_size = max(self.payload_size, tmp_payload)
        return self.payload_size

    def get_payload_size_byte(self) -> float:
        return math.ceil(self.get_payload_size() / 8)


class AFDX_INPUT_GROUP(Group):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = 'AFDX_INPUT_GROUP'


class AFDX_OUTPUT_GROUP(Group):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.name = 'AFDX_OUTPUT_GROUP'


class AFDX_OUTPUT_VL(OutputLine):

    def __init__(self) -> None:
        super().__init__()
        self.name = ''
        self.physical_port_id = ''
        self.physical_port_speed = ''
        self.pin_name = ''
        self.afdx_line_emc_protection = ''
        self.network_id = ''
        self.connector_name = ''
        self.vl_identifier = ''
        self.vl_name = ''
        self.network_select = ''
        self.bag = ''
        self.max_frame_size = ''
        self.number_of_sub_vl = ''
        self.sub_vl_identifier = ''
        self.afdx_port_identifier = ''
        self.afdx_port_master_name = ''
        self.afdx_port_type = ''
        self.port_characteristic = ''
        self.ip_frag_allowed = ''
        self.afdx_port_transmission_type = ''
        self.src_ip_address = ''
        self.dest_ip_address = ''
        self.src_udp_address = ''
        self.dest_udp_address = ''
        self.buffer_size = ''

    def get_name(self) -> str:
        return self.vl_name

    def _set_mandatory(self) -> None:
        self._add_mandatory('network_id')
        self._add_mandatory('vl_identifier')
        self._add_mandatory('vl_name')
        self._add_mandatory('network_select')
        self._add_mandatory('bag')
        self._add_mandatory('max_frame_size')
        self._add_mandatory('number_of_sub_vl')
        self._add_mandatory('sub_vl_identifier')
        self._add_mandatory('tx_afdx_port_identifier')
        self._add_mandatory('afdx_port_master_name')
        self._add_mandatory('afdx_port_type')
        self._add_mandatory('port_characteristic')
        self._add_mandatory('ip_frag_allowed')
        self._add_mandatory('src_ip_address')
        self._add_mandatory('dest_ip_address')
        self._add_mandatory('src_udp_address')
        self._add_mandatory('dest_udp_address')
        self._add_mandatory('buffer_size')


class AFDX_OUTPUT_MESSAGE(OutputSignal):

    def __init__(self) -> None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.associated_vl = ''
        self.associated_afdx_port = ''
        self.message_name = ''
        self.message_description = ''
        self.message_ref_doc = ''
        self.message_type = ''
        self.message_protocol_type = ''
        self.message_length = ''
        self.global_spare_length = ''
        self.message_transmission_rate = ''
        self.port_refresh_rate = ''
        self.fds_name = ''
        self.fds_description = ''
        self.fds_length = ''
        self.fds_spare_length = ''
        self.fds_address_in_the_message = ''
        self.functional_status_name = ''
        self.fs_description = ''
        self.fs_address_in_the_message = ''
        self.parameter_type = ''
        self.parameter_local_name = ''
        self.local_name_not_produced = ''
        self.local_name_refresh_period = ''
        self.local_name_functional_attribute = ''
        self.local_name_description = ''
        self.parameter_name = ''
        self.parameter_keyword = ''
        self.parameter_description = ''
        self.parameter_ref_doc = ''
        self.signal_name = ''
        self.signal_type = ''
        self.signal_description = ''
        self.signal_ref_doc = ''
        self.signal_nb_of_bit = ''
        self.signal_address = ''
        self.signal_position = ''
        self.bool_true_definition = ''
        self.bool_false_definition = ''
        self.bool_true_state = ''
        self.bool_false_state = ''
        self.bool_logic = ''
        self.string_length = ''
        self.string_format = ''
        self.enumerate_associated_value = ''
        self.float_operational_min = ''
        self.float_operational_max = ''
        self.float_operational_unit = ''
        self.float_operational_accuracy = ''
        self.float_coding_type = ''
        self.integer_operational_min = ''
        self.integer_operational_max = ''
        self.integer_operational_unit = ''
        self.integer_operational_accuracy = ''
        self.integer_coding_type = ''
        self.opaque_size = ''
        self.opaque_length = ''
        self.opaque_iom_corresponding_label = ''
        self.enumerate_state = ''

    def _set_mandatory(self) -> None:
        self._add_mandatory('application_name')
        self._add_mandatory('associated_tx_afdx_port')
        self._add_mandatory('message_name')
        self._add_mandatory('message_length')
        self._add_mandatory('message_transmission_rate')
        self._add_mandatory('fds_name')
        self._add_mandatory('fs_address_in_the_message')
        self._add_mandatory('parameter_type')
        # self._add_mandatory('parameter_local_name')
        # self._add_mandatory('local_name_description')
        self._add_mandatory('signal_name')
        self._add_mandatory('signal_nb_of_bit')
        self._add_mandatory('signal_address')
        # self._add_mandatory('signal_position')
        # self._add_mandatory('float_operational_unit')
        # self._add_mandatory('integer_operational_unit')

    def get_refresh_period(self) -> int:
        return 0  # self.port_refresh_rate

    def get_message_length(self) -> float:
        return self.message_length

    def get_associated_name(self) -> str:
        return self.associated_vl

    def has_parent(self) -> str:
        return 'AFDX_OUTPUT_VL'

    def can_group(self) -> str:
        return AFDX_OUTPUT_GROUP

    def get_group_parameter(self) -> str:
        return self.message_name


class AFDX_INPUT_VL(InputLine):

    def __init__(self) -> None:
        super().__init__()
        self.name = ''
        self.physical_port_id = ''
        self.physical_port_speed = ''
        self.pin_name = ''
        self.afdx_line_emc_protection = ''
        self.network_id = ''
        self.connector_name = ''
        self.vl_identifier = ''
        self.vl_name = ''
        self.network_select = ''
        self.bag = ''
        self.max_frame_size = ''
        self.rma = ''
        self.ic_active = ''
        self.skew_max = ''
        self.afdx_port_identifier = ''
        self.afdx_port_master_name = ''
        self.afdx_port_type = ''
        self.port_characteristic = ''
        self.ip_frag_allowed = ''
        self.dest_ip_address = ''
        self.dest_udp_address = ''
        self.buffer_size = ''

    def _set_mandatory(self) -> None:
        self._add_mandatory('network_id')
        self._add_mandatory('vl_identifier')
        self._add_mandatory('vl_name')
        self._add_mandatory('network_select')
        self._add_mandatory('rma')
        self._add_mandatory('ic_active')
        self._add_mandatory('skew_max')
        self._add_mandatory('rx_afdx_port_identifier')
        self._add_mandatory('afdx_port_master_name')
        self._add_mandatory('afdx_port_type')
        self._add_mandatory('port_characteristic')
        # self._add_mandatory('ip_frag_allowed')
        self._add_mandatory('dest_ip_address')
        self._add_mandatory('dest_udp_address')
        self._add_mandatory('buffer_size')

    def get_name(self) -> str:
        return self.vl_name


class AFDX_INPUT_MESSAGE(InputSignal):

    def __init__(self) -> None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.associated_vl = ''
        self.associated_afdx_port = ''
        self.message_name = ''
        self.message_description = ''
        self.message_ref_doc = ''
        self.message_type = ''
        self.message_protocol_type = ''
        self.message_length = ''
        self.global_spare_length = ''
        self.message_transmission_rate = ''
        self.port_refresh_rate = ''
        self.fds_name = ''
        self.fds_description = ''
        self.fds_length = ''
        self.fds_spare_length = ''
        self.fds_address_in_the_message = ''
        self.functional_status_name = ''
        self.fs_description = ''
        self.fs_address_in_the_message = ''
        self.parameter_type = ''
        self.parameter_local_name = ''
        self.local_name_not_produced = ''
        self.local_name_refresh_period = ''
        self.local_name_functional_attribute = ''
        self.local_name_description = ''
        self.parameter_name = ''
        self.parameter_keyword = ''
        self.parameter_description = ''
        self.parameter_ref_doc = ''
        self.signal_name = ''
        self.signal_type = ''
        self.signal_description = ''
        self.signal_ref_doc = ''
        self.signal_nb_of_bit = ''
        self.signal_address = ''
        self.signal_position = ''
        self.bool_true_definition = ''
        self.bool_false_definition = ''
        self.bool_true_state = ''
        self.bool_false_state = ''
        self.bool_logic = ''
        self.string_length = ''
        self.string_format = ''
        self.enumerate_state = ''
        self.enumerate_associated_value = ''
        self.float_operational_min = ''
        self.float_operational_max = ''
        self.float_operational_unit = ''
        self.float_operational_accuracy = ''
        self.float_coding_type = ''
        self.integer_operational_min = ''
        self.integer_operational_max = ''
        self.integer_operational_unit = ''
        self.integer_operational_accuracy = ''
        self.integer_coding_type = ''
        self.opaque_size = ''
        self.opaque_length = ''
        self.opaque_iom_corresponding_label = ''
        self.message_refresh_default = ''

    def _set_mandatory(self) -> None:
        self._add_mandatory('application_name')
        self._add_mandatory('associated_rx_afdx_port')
        self._add_mandatory('message_name')
        self._add_mandatory('message_length')
        self._add_mandatory('fds_name')
        self._add_mandatory('fs_address_in_the_message')
        self._add_mandatory('parameter_type')
        # self._add_mandatory('parameter_local_name')
        # self._add_mandatory('local_name_description')
        self._add_mandatory('signal_name')
        self._add_mandatory('signal_nb_of_bit')
        self._add_mandatory('signal_address')
        # self._add_mandatory('signal_position')
        self._add_mandatory('message_refresh_default')

    def get_refresh_period(self) -> str:
        return self.port_refresh_rate

    def get_message_length(self) -> float:
        return self.message_length

    def get_associated_name(self) -> str:
        return self.associated_vl

    def has_parent(self) -> str:
        return 'AFDX_INPUT_VL'

    def can_group(self) -> str:
        return AFDX_INPUT_GROUP

    def get_group_parameter(self) -> str:
        return self.message_name
