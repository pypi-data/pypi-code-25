from models.interfaces import Interface, OutputLine, OutputSignal, InputLine, InputSignal, APEX_INTEGER_LENGTH


class A429_OUTPUT_BUS(OutputLine):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.line_name = ''
        self.bus_description = ''
        self.bus_emc_protection = ''
        self.bus_speed = ''
        self.bus_parity_type = ''
        self.bus_transmission_rate = ''
        self.connector_type_pin_name = ''
        self.pin_role = ''
        self.connector_name = ''
        self.connection_name = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('bus_name')
        self._add_mandatory('connector_type_pin_name')
        self._add_mandatory('connector_name')


class A429_OUTPUT_LABEL(OutputSignal):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.line_name = ''
        self.label_name = ''
        self.label_number = ''
        self.port_refresh_rate = ''
        self.frame_frequency = ''
        self.cycle_frequency = ''
        self.label_description = ''
        self.label_type = ''
        self.sdi = ''
        self.val00sdi = ''
        self.val01sdi = ''
        self.val10sdi = ''
        self.val11sdi = ''
        self.ssm_length = ''
        self.ssm_value_state_00 = ''
        self.ssm_value_state_01 = ''
        self.ssm_value_state_10 = ''
        self.ssm_value_state_11 = ''
        self.protocol_name = ''
        self.protocol_position = ''
        self.bit29_sign_id_for_value_0 = ''
        self.bit29_sign_id_for_value_1 = ''
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
        self._add_mandatory('label_name')
        self._add_mandatory('label_number')
        self._add_mandatory('cycle_frequency')
        self._add_mandatory('label_type')
        self._add_mandatory('sdi')
        self._add_mandatory('ssm_length')
        self._add_mandatory('parameter_type')
        # self._add_mandatory('parameter_local_name')
        # self._add_mandatory('local_name_description')
        self._add_mandatory('signal_name')
        self._add_mandatory('signal_lsb')
        self._add_mandatory('signal_msb')
        # self._add_mandatory('float_operational_unit')
        # self._add_mandatory('float_coding_type')
        # self._add_mandatory('float_resolution')
        # self._add_mandatory('float_signed')
        # self._add_mandatory('integer_operational_unit')
        # self._add_mandatory('integer_coding_type')
        # self._add_mandatory('integer_resolution')
        # self._add_mandatory('integer_signed')

    def get_refresh_period(self)->int:
        return 0

    def get_message_length(self)->int:
        if self.parameter_type == 'Integer':
            return APEX_INTEGER_LENGTH
        elif self.parameter_type == 'String':
            return self.string_length
        elif self.parameter_type == 'Opaque':
            return self.opaque_length
        else:
            return 4


class A429_INPUT_BUS(InputLine):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.line_name = ''
        self.bus_description = ''
        self.bus_emc_protection = ''
        self.bus_speed = ''
        self.bus_parity_type = ''
        self.bus_transmission_rate = ''
        self.connector_type_pin_name = ''
        self.pin_role = ''
        self.connector_name = ''
        self.connexion_name = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('bus_name')
        self._add_mandatory('connector_type_pin_name')
        self._add_mandatory('connector_name')


class A429_INPUT_LABEL(InputSignal):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.line_name = ''
        self.label_name = ''
        self.label_number = ''
        self.port_refresh_rate = ''
        self.label_refresh_default = ''
        self.frame_frequency = ''
        self.cycle_frequency = ''
        self.label_description = ''
        self.label_type = ''
        self.sdi = ''
        self.val00sdi = ''
        self.val01sdi = ''
        self.val10sdi = ''
        self.val11sdi = ''
        self.ssm_length = ''
        self.ssm_value_state_00 = ''
        self.ssm_value_state_01 = ''
        self.ssm_value_state_10 = ''
        self.ssm_value_state_11 = ''
        self.protocol_name = ''
        self.protocol_position = ''
        self.bit29_sign_id_for_value_0 = ''
        self.bit29_sign_id_for_value_1 = ''
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
        self._add_mandatory('label_name')
        self._add_mandatory('label_number')
        self._add_mandatory('label_type')
        self._add_mandatory('sdi')
        self._add_mandatory('ssm_length')
        self._add_mandatory('parameter_type')
        # self._add_mandatory('parameter_local_name')
        # self._add_mandatory('local_name_description')
        self._add_mandatory('signal_name')
        self._add_mandatory('signal_lsb')
        self._add_mandatory('signal_msb')
        # self._add_mandatory('float_coding_type')
        # self._add_mandatory('float_resolution')
        # self._add_mandatory('float_signed')
        # self._add_mandatory('integer_coding_type')
        # self._add_mandatory('integer_resolution')
        # self._add_mandatory('integer_signed')

    def get_refresh_period(self)->str:
        return self.label_refresh_default

    def get_message_length(self)->int:
        if self.parameter_type == 'Integer':
            return APEX_INTEGER_LENGTH
        elif self.parameter_type == 'String':
            return self.string_length
        elif self.parameter_type == 'Opaque':
            return self.opaque_length
        else:
            return 1