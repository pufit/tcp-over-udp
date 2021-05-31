import asyncio
import collections
import functools
import logging
import typing as tp

from tcp_over_udp.common import const
from tcp_over_udp.common.message import TCPPacket, TCPPacketHeader
from tcp_over_udp.common.connection import Connection, ConnectionState
from tcp_over_udp.common.utils import get_ack_offset


Address = tp.Tuple[str, int]


class TCPProtocol(asyncio.protocols.DatagramProtocol):

    logger = logging.getLogger('tcp_over_udp.abstract')

    def __init__(self, target=None):
        self.transport: tp.Optional[asyncio.DatagramTransport] = None

        self.connections: tp.Dict[Address, Connection] = {}

        self._waiting_ack: tp.DefaultDict[str, tp.Dict[int, asyncio.TimerHandle]] = collections.defaultdict(dict)
        self._ack_futures: tp.DefaultDict[str, tp.Dict[int, asyncio.Future]] = collections.defaultdict(dict)

        self._target = target

        self._update_open_connections_task = asyncio.get_running_loop().create_task(self._update_open_connections_loop())

        self._outgoing_queue = asyncio.Queue()
        self._packet_sender_task = asyncio.get_running_loop().create_task(self._packet_sender_loop())

        self._stopped = False

    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = transport

    def datagram_received(self, data: bytes, addr: Address):
        while data:
            packet, data = TCPPacket.from_bytes(data)

            if packet.valid:
                self._process_packet(packet, addr)

    def message_recieved(self, data: bytes, addr: Address):
        raise NotImplementedError

    def on_connection_made(self, addr: Address):
        pass

    def send(self, data: bytes, address=None):
        if not (connection := self.connections.get(address or self._target)) or not connection.state == ConnectionState.ESTABLISHED:
            raise ValueError('Connection closed')

        self._outgoing_queue.put_nowait((data, connection))

    def close(self):
        self.transport.abort()
        self._update_open_connections_task.cancel()
        self._packet_sender_task.cancel()

        self._stopped = True

    def _ack_packet(self, addr, ack: int):
        if handler := self._waiting_ack[addr].get(ack):
            handler.cancel()
            del self._waiting_ack[addr][ack]

            self._ack_futures[addr][ack].set_result(ack)
            del self._ack_futures[addr][ack]

            for other_ack in self._waiting_ack[addr].copy().keys():
                if other_ack < ack:
                    self._waiting_ack[addr][other_ack].cancel()
                    del self._waiting_ack[addr][other_ack]

                    self._ack_futures[addr][other_ack].set_result(other_ack)
                    del self._ack_futures[addr][other_ack]

    def _process_packet(self, packet: TCPPacket, address: Address):
        if not (connection := self.connections.get(address)):
            connection = Connection(address)
            self.connections[address] = connection

        self.logger.debug(
            '[LOCAL=%s, REMOTE=%s ACK=%s SEQ=%s] Got packet %s',
            connection.local_sequence_number,
            connection.remote_sequence_number,
            packet.headers.ack_number,
            packet.headers.sequence_number,
            packet
        )

        if const.Flags.ACK in packet.headers.flags:
            self._ack_packet(connection.address, packet.headers.ack_number)

        if connection.state != ConnectionState.ESTABLISHED:
            self._handle_connection_established(connection, packet)

        else:
            self._handle_incoming_packet(connection, packet)

        self.logger.debug(
            '[LOCAL=%s, REMOTE=%s] Processed',
            connection.local_sequence_number,
            connection.remote_sequence_number,
        )

    def _handle_connection_established(self, connection: Connection, packet: TCPPacket):
        if const.Flags.SYN in packet.headers.flags and connection.state == ConnectionState.CLOSED:
            connection.state = ConnectionState.SYN_RECEIVED
            connection.remote_sequence_number = packet.headers.sequence_number
            connection.remote_sequence_number += get_ack_offset(len(packet.data), packet.headers.flags)

            self._send(connection, const.Flags.ACK | const.Flags.SYN)

        elif const.Flags.ACK in packet.headers.flags and connection.state == ConnectionState.SYN_RECEIVED:
            connection.state = ConnectionState.ESTABLISHED
            connection.remote_sequence_number += get_ack_offset(len(packet.data), packet.headers.flags)

            self._send(connection, const.Flags.ACK)
            self.logger.info('[%s] Connection established', connection.address)
            self.on_connection_made(connection.address)

    def _handle_incoming_packet(self, connection: Connection, packet: TCPPacket):
        if packet.headers.sequence_number < connection.remote_sequence_number:
            self._send(connection, const.Flags.ACK)
            return

        connection.push_packet(packet)

        if const.Flags.PSH in packet.headers.flags:
            self._process_heap(connection)

    def _process_heap(self, connection: Connection):
        sequence_number = connection.remote_sequence_number

        messages = [packet.data for packet in connection.process_heap()]
        if not messages:
            return

        if sequence_number != connection.remote_sequence_number:
            self._send(connection, const.Flags.ACK)

        message = b''.join(messages)
        if message:
            self.message_recieved(message, connection.address)

    def _send(self, connection: Connection, flags: const.Flags, data: bytes = b''):
        data_size = len(data)

        packet = TCPPacket(
            headers=TCPPacketHeader(
                sequence_number=connection.local_sequence_number,
                ack_number=connection.remote_sequence_number,
                data_size=data_size,
                checksum=0,
                flags=flags,
            ),
            data=data,
        )

        ack_offset = get_ack_offset(data_size, flags)
        connection.local_sequence_number += ack_offset
        need_ack = bool(ack_offset)

        return self._send_packet(connection, packet, need_ack)

    def _send_packet(self, connection: Connection, packet: TCPPacket, need_ack=True):
        self.logger.debug(
            '[ACK=%s SEQ=%s] Send packet %s',
            packet.headers.ack_number,
            packet.headers.sequence_number,
            packet,
        )

        self.transport.sendto(packet.to_bytes(), connection.address)

        if need_ack:
            handler = asyncio.get_running_loop().call_later(
                const.PACKET_ACK_TIMEOUT,
                functools.partial(self._send_packet, connection, packet, need_ack)
            )

            self._waiting_ack[connection.address or self._target][connection.local_sequence_number] = handler
            if not (future := self._ack_futures[connection.address or self._target].get(connection.local_sequence_number)):
                future = asyncio.get_running_loop().create_future()
                self._ack_futures[connection.address or self._target][connection.local_sequence_number] = future

            return future

        future = asyncio.get_running_loop().create_future()
        future.set_result(connection.local_sequence_number)
        return future

    async def _update_open_connections_loop(self):
        while not self._stopped:
            for connection in self.connections.values():
                self._process_heap(connection)

            await asyncio.sleep(0.5)

    async def _packet_sender_loop(self):
        while not self._stopped:
            data, connection = await self._outgoing_queue.get()

            max_part_size = const.MTU - const.IP_SIZE - const.UDP_SIZE - const.HEADER_SIZE

            window_size = 0
            max_i = len(data) // max_part_size + bool(len(data) % max_part_size)
            for i in range(0, max_i):
                packet_data = data[i * max_part_size:min(len(data), (i + 1) * max_part_size)]

                window_size += len(packet_data)
                if window_size >= const.WINDOW_SIZE:
                    window_size = 0
                    await self._send(connection, const.Flags.PSH | const.Flags.ACK, packet_data)
                else:
                    flags = const.Flags.PSH | const.Flags.ACK if i == max_i - 1 else const.Flags.ACK

                    # noinspection PyAsyncCall
                    self._send(connection, flags, packet_data)
