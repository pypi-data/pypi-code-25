from models.interfaces import Interface, OutputLine, OutputSignal, InputLine, InputSignal, APEX_FLOAT_LENGTH, APEX_DEFAULT_REFRESH
from typing import Type

class ANALOGUE_OUTPUT_LINE(OutputLine):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.line_name = ''
        self.line_description = ''
        self.line_emc_protection = ''
        self.connector_type_pin_name = ''
        self.pin_role = ''
        self.connector_name = ''
        self.connection_name = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('analog_line_name')
        self._add_mandatory('connector_type_pin_name')
        self._add_mandatory('connector_name')


class ANALOGUE_OUTPUT_SIGNAL(OutputSignal):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.line_name = ''
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
        self.keyword = ''
        self.operational_min = ''
        self.operational_max = ''
        self.operational_unit = ''
        self.operational_accuracy = ''
        self.signal_name = ''
        self.signal_description = ''
        self.io_type = ''
        self.electrical_accuracy = ''
        self.scale_factor = ''
        self.offset = ''
        self.engineering_coding_min = ''
        self.engineering_coding_max = ''
        self.engineering_coding_range_unit = ''
        self.electrical_coding_min = ''
        self.electrical_coding_max = ''
        self.electrical_coding_range_unit = ''
        self.excitation_frequency = ''
        self.i_rating_min = ''
        self.i_rating_max = ''
        self.i_rating_unit = ''
        self.v_rating_min = ''
        self.v_rating_max = ''
        self.v_rating_unit = ''
        self.function = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('application_name')
        self._add_mandatory('associated_line_name')
        # self._add_mandatory('parameter_local_name')
        self._add_mandatory('local_name_refresh_period')
        # self._add_mandatory('local_name_description')
        # self._add_mandatory('operational_min')
        # self._add_mandatory('operational_max')
        self._add_mandatory('signal_name')
        # self._add_mandatory('signal_description')
        # self._add_mandatory('scale_factor')
        # self._add_mandatory('offset')
        # self._add_mandatory('i_rating_min')
        # self._add_mandatory('i_rating_max')

    def get_refresh_period(self)->int:
        return 0

    def get_message_length(self)-> Type[APEX_FLOAT_LENGTH]:
        return APEX_FLOAT_LENGTH

class ANALOGUE_INPUT_LINE(InputLine):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.line_name = ''
        self.line_description = ''
        self.line_emc_protection = ''
        self.connector_type_pin_name = ''
        self.pin_role = ''
        self.connector_name = ''
        self.connection_name = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('analog_line_name')
        self._add_mandatory('connector_type_pin_name')
        self._add_mandatory('connector_name')


class ANALOGUE_INPUT_SIGNAL(InputSignal):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.line_name = ''
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
        self.keyword = ''
        self.operational_min = ''
        self.operational_max = ''
        self.operational_unit = ''
        self.operational_accuracy = ''
        self.signal_name = ''
        self.signal_description = ''
        self.io_type = ''
        self.electrical_accuracy = ''
        self.scale_factor = ''
        self.offset = ''
        self.engineering_coding_min = ''
        self.engineering_coding_max = ''
        self.engineering_coding_range_unit = ''
        self.electrical_coding_min = ''
        self.electrical_coding_max = ''
        self.electrical_coding_range_unit = ''
        self.excitation_frequency = ''
        self.i_rating_min = ''
        self.i_rating_max = ''
        self.i_rating_unit = ''
        self.v_rating_min = ''
        self.v_rating_max = ''
        self.v_rating_unit = ''
        self.function = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('application_name')
        self._add_mandatory('associated_line_name')
        # self._add_mandatory('parameter_local_name')
        # self._add_mandatory('local_name_description')
        # self._add_mandatory('operational_min')
        # self._add_mandatory('operational_max')
        self._add_mandatory('signal_name')
        # self._add_mandatory('scale_factor')
        # self._add_mandatory('offset')
        # self._add_mandatory('i_rating_min')
        # self._add_mandatory('i_rating_max')

    def get_refresh_period(self)->Type[APEX_DEFAULT_REFRESH]:
        return APEX_DEFAULT_REFRESH

    def get_message_length(self)->Type[APEX_FLOAT_LENGTH]:
        return APEX_FLOAT_LENGTH
