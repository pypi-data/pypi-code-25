"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""

from time import sleep
from jemu_mem_peripheral import JemuMemPeripheral
import threading
from common import JemuConnectionException


class JemuSudo(JemuMemPeripheral):
    _id = None
    _jemu_connection = None
    _peripheral_type = None
    _state = None

    _DESCRIPTION = "description"
    _STOP_AFTER_COMMAND = "stop_after"
    _START_COMMAND = "resume_running"
    _COMMAND = "command"
    _NANO_SECONDS = "nanoseconds"
    _TYPE_STRING = "type"
    _PERIPHERAL_ID = "peripheral_id"
    _PERIPHERAL_TYPE = "peripheral_type"
    _STOPPED = "stopped"
    _RESUMED = "resumed"
    _COMMAND_SET_TIMER = "set_timer"
    _MESSAGE_ID = "message_id"
    _GET_STATE_COMMAND = "get_state"
    _CANCEL_STOP_ON_TICK = "cancel_stop"
    _CANCEL_STOP_RESPONSE = "stop_canceled"
    _GET_DEVICE_TIME = "get_device_time"
    _VALUE = "value"
    _TIMER_ID = "timer_id"
    _EMULATOR_STATE = "emulator_state"
    _DEVICE_TIME = "device_time"

    def __init__(self, jemu_connection, id, peripheral_type):
        JemuMemPeripheral.__init__(self, jemu_connection, id, peripheral_type, None)
        self._id = id
        self._timer_id_counter = 0
        self._peripheral_type = peripheral_type
        self._jemu_connection = jemu_connection
        self._jemu_connection.register(self.receive_packet)
        self._timer_id_callback_dict = {}
        self._device_time_lock = threading.RLock()
        self._device_time = None
        self._stopped_packet_received = threading.Event()

    def _generate_json_command(self, command):
        return {
            self._COMMAND: command,
        }

    def stop_after_ns(self, nanoseconds):
        json_command = self._generate_json_command(self._STOP_AFTER_COMMAND)
        json_command[self._NANO_SECONDS] = nanoseconds
        self._jemu_connection.send_command_async(json_command, self._id, self._peripheral_type)

    def run_for_ns(self, nanoseconds):
        if self.get_state() == 'running':
            self._stopped_packet_received.clear()
            self.stop_after_ns(0)
            self._wait_for_event_from_connection(self._stopped_packet_received)

        if nanoseconds > 0:
            self._stopped_packet_received.clear()
            self.stop_after_ns(nanoseconds)
            self.resume()
            self._wait_for_event_from_connection(self._stopped_packet_received)

    def resume(self):
        if self.get_state() == 'paused':
            jemu_packet = self._jemu_connection.send_command(self._generate_json_command(self._START_COMMAND), self._id, self._peripheral_type)
            if not (self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._RESUMED):
                raise JemuConnectionException("Error: Couldn't resume jemu")

    def wait_until_stopped(self):
        self._stopped_packet_received.clear()
        self._wait_for_event_from_connection(self._stopped_packet_received)

    def _wait_for_event_from_connection(self, event):
        while not event.is_set():
            if not self._jemu_connection.is_connected():
                raise JemuConnectionException("Error: The Emulator was closed unexpectedly.")
            event.wait(0.2)

    def cancel_stop(self):
        jemu_packet = self._jemu_connection.send_command(self._generate_json_command(self._CANCEL_STOP_ON_TICK), self._id, self._peripheral_type)
        if not (self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._CANCEL_STOP_RESPONSE):
            raise JemuConnectionException("Error: Couldn't cancel stop")

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._DESCRIPTION] == self._STOPPED:
            self._stopped_packet_received.set()

        elif self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._TIMER_ID:
            cur_id = jemu_packet[self._VALUE]
            for id_from_dict in self._timer_id_callback_dict:
                if id_from_dict == int(cur_id):
                    self._timer_id_callback_dict[int(cur_id)]()

    def set_timer(self, ticks, callback):
        self._timer_id_callback_dict.update({self._timer_id_counter: callback})
        json_command = self._generate_json_command(self._COMMAND_SET_TIMER)
        json_command[self._NANO_SECONDS] = ticks
        json_command[self._MESSAGE_ID] = self._timer_id_counter
        self._timer_id_counter += 1
        self._jemu_connection.send_command_async(json_command, self._id, self._peripheral_type)

    def get_state(self):
        jemu_packet = self._jemu_connection.send_command(self._generate_json_command(self._GET_STATE_COMMAND), self._id, self._peripheral_type)
        if self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._EMULATOR_STATE and self._VALUE in jemu_packet:
            return jemu_packet[self._VALUE]
        else:
            raise JemuConnectionException("Error: Couldn't get jemu state")

    def get_device_time_ns(self):
        jemu_packet = self._jemu_connection.send_command(self._generate_json_command(self._GET_DEVICE_TIME), self._id, self._peripheral_type)
        if self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._DEVICE_TIME and self._VALUE in jemu_packet:
            return jemu_packet[self._VALUE]
        else:
            raise JemuConnectionException("Error: Couldn't get device time")
