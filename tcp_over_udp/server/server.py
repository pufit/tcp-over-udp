
import asyncio
import logging

from tcp_over_udp.common.protocol import TCPProtocol, Address


class TCPServerProtocol(TCPProtocol):

    logger = logging.getLogger('tcp_over_udp.server')

    def __init__(self):
        super().__init__()

        self.counter = 0

    def message_recieved(self, data: bytes, addr: Address):
        self.counter += len(data)
        # self.send(data, addr)

        if self.counter == 15 * 1024 * 1024:
            raise Exception('kek!')

    @classmethod
    async def start(cls):
        cls.logger.info('Starting UDP server')

        return await asyncio.get_running_loop().create_datagram_endpoint(
            lambda: cls(),
            local_addr=('0.0.0.0', 9999)
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(name)-24s [LINE:%(lineno)-3s]# %(levelname)-8s [%(asctime)s]  %(message)s')

    loop = asyncio.get_event_loop()
    loop.create_task(TCPServerProtocol.start())
    loop.run_forever()
