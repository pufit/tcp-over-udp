
import asyncio
import logging
import typing as tp

from tcp_over_udp.common import const
from tcp_over_udp.common.protocol import TCPProtocol, Address
from tcp_over_udp.common.connection import Connection


class TCPClientProtocol(TCPProtocol):

    def __init__(self, target):
        super().__init__(target)
        self.connection = Connection(target)
        self.connections[target] = self.connection

        self.messages_buffer = asyncio.Queue()
        self._bytes_buffer = b''

        self.connected = asyncio.get_running_loop().create_future()

    def connection_made(self, transport: asyncio.DatagramTransport):
        super().connection_made(transport)

        self._send(self.connection, const.Flags.SYN)

    def message_recieved(self, data: bytes, addr: Address):
        self.messages_buffer.put_nowait(data)

    def on_connection_made(self, addr: Address):
        self.connected.set_result(True)

    async def recv(self, size: tp.Optional[int] = None):
        if size is None:
            if self._bytes_buffer:
                data = self._bytes_buffer
                self._bytes_buffer = b''
                return data
            return await self.messages_buffer.get()

        while len(self._bytes_buffer) < size:
            self._bytes_buffer += await self.messages_buffer.get()

        data, self._bytes_buffer = self._bytes_buffer[:size], self._bytes_buffer[size:]
        return data

    @classmethod
    async def start(cls):
        return await asyncio.get_running_loop().create_datagram_endpoint(
            lambda: cls(('127.0.0.1', 9999)),
            remote_addr=('127.0.0.1', 9999)
        )


async def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(name)-24s [LINE:%(lineno)-3s]# %(levelname)-8s [%(asctime)s]  %(message)s')

    protocol: TCPClientProtocol
    _, protocol = await TCPClientProtocol.start()

    await protocol.connected

    import os
    message = os.urandom(int(1024 * 1024 * 15))

    protocol.send(message)
    assert await protocol.recv(int(1024 * 1024 * 15)) == message
    raise Exception('YES!')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
