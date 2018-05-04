"""Test a freshly-flashed PD Buddy Sink"""

import argparse
import sys
import time

import pdbuddy


class ExitCode:
    configuration_error = 1
    wrong_output = 2


class SinkTester:
    """Tests a PD Buddy Sink"""

    cfg_20v = pdbuddy.SinkConfig(status=pdbuddy.SinkStatus.VALID,
            flags=pdbuddy.SinkFlags.NONE, v=20000, vmin=None, vmax=None,
            i=1000, idim=pdbuddy.SinkDimension.CURRENT)
    cfg_9v = pdbuddy.SinkConfig(status=pdbuddy.SinkStatus.VALID,
            flags=pdbuddy.SinkFlags.NONE, v=9000, vmin=None, vmax=None, i=1000,
            idim=pdbuddy.SinkDimension.CURRENT)

    flip_poll = 0.125
    flip_delay = 1

    @staticmethod
    def _get_tty():
        devices = list(pdbuddy.Sink.get_devices())
        # If the wrong number of devices is present, complain and exit.
        if len(devices) < 1:
            raise ValueError('No PD Buddy Sink devices found')
        elif len(devices) > 1:
            raise ValueError('Multiple PD Buddy Sink devices found')
        # Set tty to the auto-detected Sink
        return devices[0].device

    def _pre_write(self, cfg):
        """Notify the user that new configuration is being written"""
        print('Writing {v:.1f} V configuration object…'.format(v=cfg.v/1000.))

    def _cfg_verify(self, sink, cfg):
        """Verify that the given configuration is on the Sink"""
        actual_cfg = sink.get_cfg()
        assert actual_cfg == cfg, ('Configuration error; expected config:\n'
                '{cfg}\n'
                'actual config:\n'
                '{actual_cfg}'.format(cfg=cfg, actual_cfg=actual_cfg))

    def _post_write(self, cfg):
        """Notify the user that new configuration has been written"""
        print('Done.')

    def _write_verify(self, sink, cfg):
        """Write a SinkConfig to a Sink and verify that it was written"""
        self._pre_write(cfg)

        sink.set_tmpcfg(cfg)
        sink.write()

        self._cfg_verify(sink, cfg)

        self._post_write(cfg)

    def _test_output(self, sink, voltage):
        """Test if the Sink's output is correct"""
        answer = input("Is the Sink's output stable at {:.1f} V [Y,n]? ".format(
            voltage/1000. * sink.output))
        return not answer.lower().startswith('n')

    def _output_verify(self, sink):
        """Verify that the Sink's output is correct"""
        # Get the configured voltage
        voltage = sink.get_cfg().v
        if voltage is None:
            voltage = 0

        assert self._test_output(sink, voltage), 'Wrong output voltage'

    def _test_phase1(self, sink):
        # Make sure output is disabled to start
        sink.output = False

        # Set initial configuration
        self._write_verify(sink, self.cfg_20v)

        # Turn on the output and ensure that it's correct
        sink.output = True
        self._output_verify(sink)

        # Turn off the output and ensure that it's off
        sink.output = False
        self._output_verify(sink)

        # Turn on the output again and ensure that it's back at 20 V
        sink.output = True
        self._output_verify(sink)

        # Set second configuration
        self._write_verify(sink, self.cfg_9v)

        # Ensure that the output is 9 V now
        self._output_verify(sink)

    def _alert_flip(self):
        print('Remove, flip, and re-insert the USB connector.')

    def _flip(self):
        self._alert_flip()

        # Wait for the Sink to be disconnected
        while len(list(pdbuddy.Sink.get_devices())):
            time.sleep(self.flip_poll)

        # Wait for the Sink to be connected
        while not len(list(pdbuddy.Sink.get_devices())):
            time.sleep(self.flip_poll)

        time.sleep(self.flip_delay)

    def _test_phase2(self, sink):
        # Ensure that the Sink is configured for 9 V
        self._cfg_verify(sink, self.cfg_9v)

        # Ensure that the output is off
        self._output_verify(sink)

        # Turn on the output and ensure that it's correct (9 V)
        sink.output = True
        self._output_verify(sink)

        # Erase the sink's configuration
        sink.erase()

        # Ensure there's no output despite it being enabled
        sink.output = True
        self._output_verify(sink)

    def test(self):
        """Test a PD Buddy Sink"""
        with pdbuddy.Sink(self._get_tty()) as sink:
            self._test_phase1(sink)

        self._flip()

        with pdbuddy.Sink(self._get_tty()) as sink:
            self._test_phase2(sink)


def main():
    # Make the argument parser
    parser = argparse.ArgumentParser(description='Test a PD Buddy Sink')
    parser.add_argument('-l', '--list-devices', action='store_true',
            help='list connected PD Buddy Sinks and exit')

    # Parse arguments
    args = parser.parse_args()

    # If asked to, list devices and exit
    if args.list_devices:
        for sinkinfo in pdbuddy.Sink.get_devices():
            print(sinkinfo.device, '-', sinkinfo.manufacturer,
                    sinkinfo.product, sinkinfo.serial_number)
        sys.exit(0)

    tester = SinkTester()
    try:
        tester.test()
    except (AssertionError, ValueError) as e:
        print(e)
        sys.exit(1)

    # Congratulations, all tests passed!
    print('Test successful!')

if __name__ == '__main__':
    main()
