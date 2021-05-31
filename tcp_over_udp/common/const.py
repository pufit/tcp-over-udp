import struct
import enum

SEQUENCE_NUMBER_FORMAT = 'I'
SEQUENCE_NUMBER_SIZE = struct.calcsize(SEQUENCE_NUMBER_FORMAT)

ACK_NUMBER_FORMAT = 'I'
ACK_NUMBER_SIZE = struct.calcsize(ACK_NUMBER_FORMAT)

DATA_FORMAT = 'H'
DATA_SIZE = struct.calcsize(DATA_FORMAT)

CHECKSUM_FORMAT = 'H'
CHECKSUM_SIZE = struct.calcsize(CHECKSUM_FORMAT)

FLAGS_FORMAT = 'B'
FLAGS_SIZE = struct.calcsize(FLAGS_FORMAT)

WINDOW_SIZE = 1024 * 100  # bytes

PACKET_ACK_TIMEOUT = 1  # seconds


class Flags(enum.Flag):
    ACK = enum.auto()
    PSH = enum.auto()
    RST = enum.auto()
    SYN = enum.auto()
    FIN = enum.auto()


HEADER_FORMAT = f'>{SEQUENCE_NUMBER_FORMAT}{ACK_NUMBER_FORMAT}{DATA_FORMAT}{CHECKSUM_FORMAT}{FLAGS_FORMAT}'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

MTU = 1500
IP_SIZE = 20
UDP_SIZE = 8
