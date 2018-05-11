from models.interfaces import Interface, OutputLine, OutputSignal, InputLine, InputSignal, APEX_DISCRETE_LENGTH, APEX_DEFAULT_REFRESH
from typing import Type

class DISCRETE_OUTPUT_LINE(OutputLine):

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
        self._add_mandatory('discrete_line_name')
        self._add_mandatory('connector_type_pin_name')
        self._add_mandatory('connector_name')


class DISCRETE_OUTPUT_SIGNAL(OutputSignal):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.line_name = ''
        self.parameter_local_name = ''
        self.local_name_not_produced = ''
        self.local_name_refresh_period = ''
        self.local_name_functional_attribute = ''
        self.local_name_description = ''
        self.parameter_name = ''
        self.parameter_description = ''
        self.parameter_ref_doc = ''
        self.keyword = ''
        self.true_definition = ''
        self.false_definition = ''
        self.signal_name = ''
        self.signal_description = ''
        self.io_type = ''
        self.true_state = ''
        self.false_state = ''
        self.unit = ''
        self.logic = ''
        self.stabilization_time = ''
        self.default_value = ''
        self.min_current_range = ''
        self.max_current_range = ''
        self.unit_current_range = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('application_name')
        self._add_mandatory('line_name')
        # self._add_mandatory('parameter_local_name')
        self._add_mandatory('local_name_refresh_period')
        # self._add_mandatory('local_name_description')
        self._add_mandatory('signal_name')
        # self._add_mandatory('signal_description')
        # self._add_mandatory('min_current_range')
        # self._add_mandatory('max_current_range')

    def get_refresh_period(self)->int:
        return 0

    def get_message_length(self)-> Type[APEX_DISCRETE_LENGTH]:
        return APEX_DISCRETE_LENGTH


class DISCRETE_INPUT_LINE(InputLine):

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
        self._add_mandatory('discrete_line_name')
        self._add_mandatory('connector_type_pin_name')
        self._add_mandatory('connector_name')


class DISCRETE_INPUT_SIGNAL(InputSignal):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.application_name = ''
        self.application_description = ''
        self.application_type = ''
        self.line_name = ''
        self.parameter_local_name = ''
        self.local_name_not_produced = ''
        self.local_name_refresh_period = ''
        self.local_name_functional_attribute = ''
        self.local_name_description = ''
        self.parameter_name = ''
        self.parameter_description = ''
        self.parameter_ref_doc = ''
        self.keyword = ''
        self.true_definition = ''
        self.false_definition = ''
        self.signal_name = ''
        self.signal_description = ''
        self.io_type = ''
        self.true_state = ''
        self.false_state = ''
        self.unit = ''
        self.logic = ''
        self.stabilization_time = ''
        self.default_value = ''
        self.min_current_range = ''
        self.unit_current_range = ''
        self.max_current_range = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('application_name')
        self._add_mandatory('line_name')
        # self._add_mandatory('parameter_local_name')
        # self._add_mandatory('local_name_description')
        self._add_mandatory('signal_name')
        self._add_mandatory('logic')
        self._add_mandatory('stabilization_time')

    def get_refresh_period(self)->Type[APEX_DEFAULT_REFRESH]:
        return APEX_DEFAULT_REFRESH

    def get_message_length(self)->Type[APEX_DISCRETE_LENGTH]:
        return APEX_DISCRETE_LENGTH
