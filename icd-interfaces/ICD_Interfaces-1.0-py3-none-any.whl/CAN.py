from models.interfaces import Interface, OutputLine, OutputSignal, InputLine, InputSignal


class CAN_OUTPUT_BUS(OutputLine):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.line_name = ''
        self.bus_description = ''
        self.bus_emc_protection = ''
        self.bus_max_update_rate = ''
        self.bus_transmission_rate = ''
        self.connector_type_pin_name = ''
        self.pin_role = ''
        self.connector_name = ''
        self.connexion_name = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('bus_name')
        self._add_mandatory('connector_type_pin_name')
        self._add_mandatory('connector_name')


class CAN_OUTPUT_FRAME(Interface):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.associated_bus_name = ''
        self.frame_name = ''
        self.frame_description = ''
        self.frame_ref_doc = ''
        self.frame_frequency = ''
        self.t_timer = ''
        self.tp = ''
        self.ti = ''
        self.tr = ''
        self.min_load = ''
        self.max_load = ''


class CAN_OUTPUT_MESSAGE(OutputSignal):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.associated_bus = ''
        self.can_message_name = ''
        self.msg_description = ''
        self.msg_ref_doc = ''
        self.msg_protocol_type = ''
        self.msg_identifier = ''
        self.msg_update_rate = ''
        self.event_message = ''
        self.msg_payload_length = ''
        self.group_name = ''
        self.group_position = ''
        self.msg_size = ''
        self.port_refresh_rate = ''
        self.parameter_type = ''
        self.parameter_local_name = ''
        self.local_name_not_produced = ''
        self.local_name_refresh_period = ''
        self.event_signal = ''
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
        self.signal_lsb = ''
        self.signal_msb = ''
        self.signal_transmit_order = ''
        self.signal_start_bit = ''
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
        self.float_resolution = ''
        self.float_scale_factor = ''
        self.float_offset = ''
        self.float_signed = ''
        self.float_function_non_linear_scale = ''
        self.integer_operational_min = ''
        self.integer_operational_max = ''
        self.integer_operational_unit = ''
        self.integer_operational_accuracy = ''
        self.integer_coding_type = ''
        self.integer_resolution = ''
        self.integer_scale_factor = ''
        self.integer_offset = ''
        self.integer_signed = ''
        self.integer_function_non_linear_scale = ''
        self.opaque_max_size = ''
        self.opaque_length = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('application_name')
        self._add_mandatory('associated_bus')
        self._add_mandatory('can_message_name')
        self._add_mandatory('msg_identifier')
        self._add_mandatory('msg_update_rate')
        self._add_mandatory('msg_payload_length')
        # self._add_mandatory('parameter_type')
        # self._add_mandatory('parameter_local_name')
        # self._add_mandatory('local_name_description')
        self._add_mandatory('signal_name')
        # self._add_mandatory('signal_lsb')
        # self._add_mandatory('signal_msb')
        # self._add_mandatory('float_operational_unit')
        # self._add_mandatory('integer_operational_unit')
        # self._add_mandatory('integer_coding_type')

    def get_refresh_period(self)->int:
        return 0 #self.msg_update_rate

    def get_message_length(self)->Type[msg_payload_length]:
        return self.msg_payload_length

class CAN_INPUT_BUS(InputLine):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.line_name = ''
        self.bus_description = ''
        self.bus_emc_protection = ''
        self.bus_max_update_rate = ''
        self.bus_transmission_rate = ''
        self.connector_type_pin_name = ''
        self.pin_role = ''
        self.connector_name = ''
        self.connexion_name = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('bus_name')
        self._add_mandatory('connector_type_pin_name')
        self._add_mandatory('connector_name')


class CAN_INPUT_FRAME(Interface):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.associated_bus_name = ''
        self.frame_name = ''
        self.frame_description = ''
        self.frame_ref_doc = ''
        self.frame_frequency = ''
        self.t_timer = ''
        self.tp = ''
        self.ti = ''
        self.tr = ''
        self.min_load = ''
        self.max_load = ''


class CAN_INPUT_MESSAGE(InputSignal):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.associated_bus = ''
        self.can_message_name = ''
        self.msg_description = ''
        self.msg_ref_doc = ''
        self.msg_protocol_type = ''
        self.msg_identifier = ''
        self.msg_update_rate = ''
        self.event_message = ''
        self.msg_payload_length = ''
        self.group_name = ''
        self.group_position = ''
        self.msg_size = ''
        self.port_refresh_rate = ''
        self.msg_refresh_default = ''
        self.parameter_type = ''
        self.parameter_local_name = ''
        self.local_name_not_produced = ''
        self.local_name_refresh_period = ''
        self.event_signal = ''
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
        self.signal_lsb = ''
        self.signal_msb = ''
        self.signal_transmit_order = ''
        self.signal_start_bit = ''
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
        self.float_resolution = ''
        self.float_scale_factor = ''
        self.float_offset = ''
        self.float_signed = ''
        self.float_function_non_linear_scale = ''
        self.integer_operational_min = ''
        self.integer_operational_max = ''
        self.integer_operational_unit = ''
        self.integer_operational_accuracy = ''
        self.integer_coding_type = ''
        self.integer_resolution = ''
        self.integer_scale_factor = ''
        self.integer_offset = ''
        self.integer_signed = ''
        self.integer_function_non_linear_scale = ''
        self.opaque_max_size = ''
        self.opaque_length = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('application_name')
        self._add_mandatory('associated_bus')
        self._add_mandatory('can_message_name')
        self._add_mandatory('msg_identifier')
        self._add_mandatory('msg_payload_length')
        # self._add_mandatory('parameter_type')
        # self._add_mandatory('parameter_local_name')
        # self._add_mandatory('local_name_description')
        self._add_mandatory('signal_name')
        # self._add_mandatory('signal_lsb')
        # self._add_mandatory('signal_msb')
        # self._add_mandatory('float_coding_type')
        # self._add_mandatory('integer_coding_type')

    def get_refresh_period(self)->str:
        return self.msg_refresh_default

    def get_message_length(self)->str:
        return self.msg_payload_length
