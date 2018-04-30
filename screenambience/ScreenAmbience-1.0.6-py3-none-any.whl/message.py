import ctypes
import socket
import struct
import sys
from bitstruct import pack, byteswap, calcsize
from binascii import hexlify

FRAME_HEADER_FORMAT = 'u16u2u1u1u12u32'
FRAME_HEADER_BYTESWAP = '224'

FRAME_ADDRESS_FORMAT = 'u64u48u6u1u1u8'
FRAME_ADDRESS_BYTESWAP = '8611'

PROTOCOL_HEADER_FORMAT = 'u64u16u16'
PROTOCOL_HEADER_BYTESWAP = '822'

BROADCAST_IP = "10.0.0.255" 

# Packet building reference on LIFX forums: https://community.lifx.com/t/building-a-lifx-packet/59/3
def send_packet(packet):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    result = bytes.fromhex(packet.hex())
    sock.sendto(result, (BROADCAST_IP, 56700))

def sizeof(format):
    return calcsize(format)

def make_frame_header(size, origin, tagged, addressable, protocol, source):
    unswapped_header = pack(FRAME_HEADER_FORMAT, size, origin, 0, addressable, protocol, source)
    frame_header = byteswap(FRAME_HEADER_BYTESWAP, unswapped_header)
    return frame_header

def make_frame_address(target, ack_required, res_required, sequence):
    target = target.split(':')
    target.reverse()
    target = ''.join(target)
    target = int(target, 16)
    unswapped_header = pack(FRAME_ADDRESS_FORMAT, target, 0, 0, ack_required, res_required, sequence)
    frame_address = byteswap(FRAME_ADDRESS_BYTESWAP, unswapped_header)
    return frame_address


def make_protocol_header(message_type):
    unswapped_header = pack(PROTOCOL_HEADER_FORMAT, 0, message_type, 0)
    protocol_header = byteswap(PROTOCOL_HEADER_BYTESWAP, unswapped_header)
    return protocol_header


def set_zone_color(average_screen_color, duration, mac_address, start, end):
    payload_format = 'u8u8u16u16u16u16u32u8'
    payload_byteswap = '11222241'

    packet_size = (sizeof(FRAME_HEADER_FORMAT + FRAME_ADDRESS_FORMAT + PROTOCOL_HEADER_FORMAT + payload_format)) / 8
    frame_header = make_frame_header(packet_size, 0, 0, 1, 1024, 0)
    frame_address = make_frame_address(mac_address, 0, 0, 0)
    protocol_header = make_protocol_header(501)
    header = frame_header + frame_address + protocol_header
    unswapped_payload = pack (payload_format, start, end, *average_screen_color, duration, 1)
    payload = byteswap(payload_byteswap, unswapped_payload)
    packet = header + payload
    send_packet(packet)