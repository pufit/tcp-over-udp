import enum
import heapq
import random
import typing as tp
from dataclasses import dataclass, field

from tcp_over_udp.common.message import TCPPacket
from tcp_over_udp.common.utils import get_ack_offset


class ConnectionState(enum.IntEnum):
    CLOSED = 0
    SYN_SENT = 1
    SYN_RECEIVED = 2
    ESTABLISHED = 3
    FIN_WAIT_ONE = 4
    FIN_WAIT_TWO = 5


@dataclass(order=True)
class HeapMessage:
    sequence_number: int
    packet: TCPPacket = field(compare=False)


@dataclass
class Connection:
    address: tp.Tuple[str, int]

    last_active: float = 0
    state: ConnectionState = ConnectionState.CLOSED

    local_sequence_number: int = field(default_factory=lambda: random.randint(0, 1000))
    remote_sequence_number: int = field(default_factory=lambda: random.randint(0, 1000))

    incoming_heap: tp.List[HeapMessage] = field(default_factory=list)

    def push_packet(self, packet: TCPPacket):
        heapq.heappush(self.incoming_heap, HeapMessage(packet.headers.sequence_number, packet))

    def process_heap(self):
        while self.incoming_heap:
            item = heapq.heappop(self.incoming_heap)

            if item.sequence_number < self.remote_sequence_number:
                continue

            if item.sequence_number == self.remote_sequence_number:
                self.remote_sequence_number += get_ack_offset(len(item.packet.data), item.packet.headers.flags)
                yield item.packet
            else:
                heapq.heappush(self.incoming_heap, item)
                break
