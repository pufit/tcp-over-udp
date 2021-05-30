
import argparse
import asyncio
import logging

from tcp_over_udp.common.protocol import TCPProtocol, Address


class TCPServerProtocol(TCPProtocol):

    logger = logging.getLogger('tcp_over_udp.server')

    def __init__(self):
        super().__init__()

    def message_recieved(self, data: bytes, addr: Address):
        self.logger.info('[%s] Message recieved %s', addr, data)

    @classmethod
    async def start(cls, host: str = '0.0.0.0', port: int = 8956):
        cls.logger.info('Starting UDP server')

        return await asyncio.get_running_loop().create_datagram_endpoint(
            lambda: cls(),
            local_addr=(host, port)
        )


def build_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-H', '--host', type=str,
        help='Host to serve',
        default='0.0.0.0',
    )

    parser.add_argument(
        '-p', '--port', type=int,
        help='Port to serve',
        default=8956
    )

    parser.add_argument(
        '-l', '--logging-level', type=str,
        help='Logging level',
        default='INFO',
    )

    return parser


async def main():
    args = build_parser().parse_args()

    logging.basicConfig(
        level=logging.getLevelName(args.logging_level),
        format='%(name)-24s [LINE:%(lineno)-3s]# %(levelname)-8s [%(asctime)s]  %(message)s'
    )

    await TCPServerProtocol.start(host=args.host, port=args.port)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
