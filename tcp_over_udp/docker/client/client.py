
import asyncio
import logging
from tcp_over_udp.client import TCPClientProtocol


async def main():
    client: TCPClientProtocol
    _, client = await TCPClientProtocol.start()

    await client.connected

    i = 0
    while True:

        with open(f'files/{i + 1}') as f:
            data = f.read().encode()

        client.logger.info('Send file %s', i + 1)
        client.send(data)

        assert await client.recv(len(data)) == data
        client.logger.info('Recieved!')

        i = (i + 1) % 5
        await asyncio.sleep(5)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(name)-24s [LINE:%(lineno)-3s]# %(levelname)-8s [%(asctime)s]  %(message)s'
    )

    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
