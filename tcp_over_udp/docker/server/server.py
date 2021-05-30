import asyncio
import logging

from tcp_over_udp.server import TCPServerProtocol


class EchoServer(TCPServerProtocol):

    def message_recieved(self, data: bytes, addr):
        self.logger.info('[%s] Message recieved (len %s)', addr, len(data))
        self.send(data, addr)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(name)-24s [LINE:%(lineno)-3s]# %(levelname)-8s [%(asctime)s]  %(message)s'
    )

    loop = asyncio.get_event_loop()
    loop.create_task(EchoServer.start())
    loop.run_forever()
