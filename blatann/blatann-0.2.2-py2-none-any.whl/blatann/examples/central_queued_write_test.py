import struct
from blatann import BleDevice, uuid
from blatann.gap import smp
from blatann.examples import example_utils, constants
from blatann.nrf import nrf_events

logger = example_utils.setup_logger(level="DEBUG")


def main(serial_port):
    # Set the target to the peripheral's advertised name
    target_device_name = constants.PERIPHERAL_NAME

    # Create and open the BLE device (and suppress spammy logs)
    ble_device = BleDevice(serial_port)
    ble_device.event_logger.suppress(nrf_events.GapEvtAdvReport)
    ble_device.open()

    logger.info("Scanning for '{}'".format(target_device_name))
    target_address = example_utils.find_target_device(ble_device, target_device_name)

    if not target_address:
        logger.info("Did not find target peripheral")
        return

    # Initiate the connection and wait for it to finish
    logger.info("Found match: connecting to address {}".format(target_address))
    peer = ble_device.connect(target_address).wait()
    if not peer:
        logger.warning("Timed out connecting to device")
        return

    # Wait up to 10 seconds for service discovery to complete
    logger.info("Connected, conn_handle: {}".format(peer.conn_handle))
    _, event_args = peer.discover_services().wait(10, exception_on_timeout=False)
    logger.info("Service discovery complete! status: {}".format(event_args.status))

    def on_write_complete(sender, event_args):
        """
        :param sender:
        :type event_args: blatann.event_args.WriteCompleteEventArgs
        """
        write_id = getattr(event_args, "id", None)
        logger.info("Write complete for value {}, status {}, id {}".format(event_args.value, event_args.status, write_id))

    def on_read_complete(sender, event_args):
        """
        :param sender:
        :type event_args: blatann.event_args.WriteCompleteEventArgs
        """
        read_id = getattr(event_args, "id", None)
        logger.info("Write complete for value {}, status {}, id {}".format(event_args.value, event_args.status, read_id))
    # Find the hex conversion characteristic. This characteristic takes in a bytestream and converts it to its
    # hex representation. e.g. '0123' -> '30313233'
    hex_convert_char = peer.database.find_characteristic(constants.HEX_CONVERT_CHAR_UUID)
    if hex_convert_char:
        hex_convert_char.on_write_complete.register(on_write_complete)
        hex_convert_char.on_read_complete.register(on_read_complete)
        write1_data = "ABCD"
        write2_data = "DEFG"

        logger.info("Sending first write")
        w1 = hex_convert_char.write(write1_data)

        logger.info("Sending read")
        w2 = hex_convert_char.read()

        logger.info("Sending second write")
        w3 = hex_convert_char.write(write2_data)

        logger.info("Waiting on second write")
        w3.wait()
        logger.info("Waiting on read")
        w2.wait()
        logger.info("Waiting on first write")
        w1.wait()
        logger.info("Writes complete")

    # Clean up
    logger.info("Disconnecting from peripheral")
    peer.disconnect().wait()
    ble_device.close()


if __name__ == '__main__':
    main("COM60")


