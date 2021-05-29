import struct
import typing as tp

from tcp_over_udp.common import const
from tcp_over_udp.common.utils import calculate_check_sum


class TCPPacketHeader(tp.NamedTuple):
    sequence_number: int
    ack_number: int
    data_size: int
    checksum: int
    flags: const.Flags

    @classmethod
    def from_bytes(cls, data: bytes) -> 'TCPPacketHeader':
        assert len(data) == const.HEADER_SIZE

        values = struct.unpack(const.HEADER_FORMAT, data)
        # noinspection PyArgumentList
        headers = cls(*values[:-1], const.Flags(values[-1]))
        return headers

    def to_bytes(self, checksum: int) -> bytes:
        return struct.pack(const.HEADER_FORMAT, self.sequence_number, self.ack_number, self.data_size, checksum, self.flags.value)


class TCPPacket(tp.NamedTuple):
    headers: TCPPacketHeader
    data: bytes

    @property
    def valid(self):
        return calculate_check_sum(self) == self.headers.checksum

    @classmethod
    def from_bytes(cls, data: bytes) -> tp.Tuple['TCPPacket', bytes]:
        assert len(data) >= const.HEADER_SIZE, data

        headers = TCPPacketHeader.from_bytes(data[:const.HEADER_SIZE])
        packet_data = data[const.HEADER_SIZE:const.HEADER_SIZE + headers.data_size]
        # noinspection PyTypeChecker
        return cls(headers, packet_data), data[const.HEADER_SIZE + headers.data_size:]

    def to_bytes(self) -> bytes:
        check_sum = calculate_check_sum(self)
        return self.headers.to_bytes(check_sum) + self.data
