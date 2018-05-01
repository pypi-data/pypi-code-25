"""
Created on Feb 17 2018

@author: MCC
"""

from ctypes import c_longlong, c_double, byref
from .ul_exception import ULException
from .ul_c_interface import lib, AiConfigItem, AiConfigItemDbl
from .ul_enums import AiChanType, TcType, AutoZeroMode, AdcTimingMode, IepeMode, CouplingMode


class AiConfig:
    """
    Provides information about the configuration of the analog input subsystem.

    Args:
        handle: UL DAQ Device handle.
    """

    def __init__(self, handle):
        self.__handle = handle

    def set_chan_type(self, channel, chan_type):
        # type: (int, AiChanType) -> None
        """
        Configures the channel type for the specified A/D channel.

        Args:
            channel (int): The A/D channel number.
            chan_type (AiChanType): The channel type to be set.

        Raises:
            :class:`ULException`
        """
        err = lib.ulAISetConfig(self.__handle, AiConfigItem.CHAN_TYPE, channel, chan_type)
        if err != 0:
            raise ULException(err)
    
    def get_chan_type(self, channel):
        # type: (int) -> AiChanType
        """
        Gets the channel type for the specified A/D channel.

        Args:
            channel (int): The A/D channel number.

        Returns:
            AiChanType:

            The channel type of the specified channel.

        Raises:
            :class:`ULException`
        """
        chan_type = c_longlong()
        err = lib.ulAIGetConfig(self.__handle, AiConfigItem.CHAN_TYPE, channel, byref(chan_type))
        if err != 0:
            raise ULException(err)
        return chan_type.value

    def set_chan_tc_type(self, channel, tc_type):
        # type: (int, TcType) -> None
        """
        Configures the thermocouple type for the specified A/D channel.

        Args:
            channel (int): The A/D channel number whose thermocouple type is being set.
            tc_type (TcType): The thermocouple type to set`

        Raises:
            :class:`ULException`
        """
        err = lib.ulAISetConfig(self.__handle, AiConfigItem.CHAN_TC_TYPE, channel, tc_type)
        if err != 0:
            raise ULException(err)
    
    def get_chan_tc_type(self, channel):
        # type: (int) -> TcType

        """
        Gets the thermocouple type for the specified A/D channel.

        Args:
            channel (int): The A/D channel number whose thermocouple type is being determined.

        Returns:
            TcType:

            The thermocouple type of the specified channel.

        Raises:
            :class:`ULException`
        """
        tc_type = c_longlong()
        err = lib.ulAIGetConfig(self.__handle, AiConfigItem.CHAN_TYPE, channel, byref(tc_type))
        if err != 0:
            raise ULException(err)
        return tc_type.value

    def set_auto_zero_mode(self, mode):
        # type: (AutoZeroMode) -> None

        err = lib.ulAISetConfig(self.__handle, AiConfigItem.AUTO_ZERO_MODE, 0, mode)
        if err != 0:
            raise ULException(err)
    
    def get_auto_zero_mode(self):
        # type: () -> AutoZeroMode

        mode = c_longlong()
        err = lib.ulAIGetConfig(self.__handle, AiConfigItem.AUTO_ZERO_MODE, 0, byref(mode))
        if err != 0:
            raise ULException(err)
        return mode.value

    def set_adc_timing_mode(self, mode):
        # type: (AdcTimingMode) -> None

        err = lib.ulAISetConfig(self.__handle, AiConfigItem.ADC_TIMING_MODE, 0, mode)
        if err != 0:
            raise ULException(err)
    
    def get_adc_timing_mode(self):
        # type: () -> AdcTimingMode

        mode = c_longlong()
        err = lib.ulAIGetConfig(self.__handle, AiConfigItem.ADC_TIMING_MODE, 0, byref(mode))
        if err != 0:
            raise ULException(err)
        return mode.value

    def set_chan_iepe_mode(self, channel, mode):
        # type: (int, IepeMode) -> None

        err = lib.ulAISetConfig(self.__handle, AiConfigItem.CHAN_IEPE_MODE, channel, mode)
        if err != 0:
            raise ULException(err)
    
    def get_chan_iepe_mode(self, channel):
        # type: (int) -> IepeMode

        mode = c_longlong()
        err = lib.ulAIGetConfig(self.__handle, AiConfigItem.CHAN_IEPE_MODE, channel, byref(mode))
        if err != 0:
            raise ULException(err)
        return mode.value

    def set_chan_coupling_mode(self, channel, mode):
        # type: (int, CouplingMode) -> None

        err = lib.ulAISetConfig(self.__handle, AiConfigItem.CHAN_COUPLING_MODE, channel, mode)
        if err != 0:
            raise ULException(err)
    
    def get_chan_coupling_mode(self, channel):
        # type: (int) -> CouplingMode

        mode = c_longlong()
        err = lib.ulAIGetConfig(self.__handle, AiConfigItem.CHAN_COUPLING_MODE, channel, byref(mode))
        if err != 0:
            raise ULException(err)
        return mode.value

    def set_chan_sensor_sensitivity(self, channel, sensitivity):
        # type: (int, float) -> None

        err = lib.ulAISetConfigDbl(self.__handle, AiConfigItemDbl.CHAN_SENSOR_SENSIVITY, channel, sensitivity)
        if err != 0:
            raise ULException(err)
    
    def get_chan_sensor_sensitivity(self, channel):
        # type: (int) -> float

        sensitivity = c_double()
        err = lib.ulAIGetConfigDbl(self.__handle, AiConfigItemDbl.CHAN_SENSOR_SENSIVITY, channel,
                                   byref(sensitivity))
        if err != 0:
            raise ULException(err)
        return sensitivity.value

    def set_chan_slope(self, channel, slope):
        # type: (int, float) -> None

        err = lib.ulAISetConfigDbl(self.__handle, AiConfigItemDbl.CHAN_SLOPE, channel, slope)
        if err != 0:
            raise ULException(err)
    
    def get_chan_slope(self, channel):
        # type: (int) -> float

        slope = c_double()
        err = lib.ulAIGetConfigDbl(self.__handle, AiConfigItemDbl.CHAN_SLOPE, channel, byref(slope))
        if err != 0:
            raise ULException(err)
        return slope.value

    def set_chan_offset(self, channel, offset):
        # type: (int, float) -> None

        err = lib.ulAISetConfigDbl(self.__handle, AiConfigItemDbl.CHAN_OFFSET, channel, offset)
        if err != 0:
            raise ULException(err)
    
    def get_chan_offset(self, channel):
        # type: (int) -> float

        offset = c_double()
        err = lib.ulAIGetConfigDbl(self.__handle, AiConfigItemDbl.CHAN_OFFSET, channel, byref(offset))
        if err != 0:
            raise ULException(err)
        return offset.value
    
    def get_cal_date(self):
        # type: () -> str
        """
        Gets the calibration date for the DAQ device.

        Returns:
            str:

            A string containing the calibration date for the DAQ device.

        Raises:
            :class:`ULException`
        """
        cal_date = c_longlong()
        err = lib.ulAIGetConfig(self.__handle, AiConfigItem.CAL_DATE, 0, byref(cal_date))
        if err != 0:
            raise ULException(err)
        return cal_date.value
