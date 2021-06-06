
import asyncio
import logging
from async_timeout import timeout
from tcp_over_udp.client import TCPClientProtocol


async def main():
    client: TCPClientProtocol
    _, client = await TCPClientProtocol.start(host='main-server')

    await client.connected

    i = 0
    while True:

        with open(f'files/{i + 1}', 'rb') as f:
            data = f.read()

        client.logger.info('Send file %s', i + 1)
        client.send(data)

        async with timeout(30):
            assert await client.recv(len(data)) == data
            client.logger.info('Recieved!')

        i = (i + 1) % 5
        await asyncio.sleep(5)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(name)-24s [LINE:%(lineno)-3s]# %(levelname)-8s [%(asctime)s]  %(message)s'
    )

    asyncio.run(main())
