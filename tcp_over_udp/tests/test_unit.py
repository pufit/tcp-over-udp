
import os
import pytest
import typing as tp
import asyncio

from tcp_over_udp.server import TCPServerProtocol
from tcp_over_udp.client import TCPClientProtocol


class TCPTestServerProtocol(TCPServerProtocol):

    def message_recieved(self, data: bytes, addr):
        self.send(data, addr)


@pytest.fixture(scope='function')
async def server():
    _, protocol = await TCPTestServerProtocol.start()
    yield protocol
    for waiting_ack in protocol._waiting_ack.values():
        assert not waiting_ack

    protocol.close()


@pytest.fixture(scope='function')
async def client():
    _, protocol = await TCPClientProtocol.start()
    await protocol.connected
    yield protocol

    for waiting_ack in protocol._waiting_ack.values():
        assert not waiting_ack

    protocol.close()


@pytest.fixture(scope='function')
async def clients():

    clients = []

    for _ in range(10):
        _, protocol = await TCPClientProtocol.start()
        await protocol.connected

        clients.append(protocol)

    yield clients

    for protocol in clients:
        for waiting_ack in protocol._waiting_ack.values():
            assert not waiting_ack

        protocol.close()


@pytest.mark.asyncio
async def test_hello_world(server: TCPTestServerProtocol, client: TCPClientProtocol):
    client.send(b'Hello world!')

    assert await client.recv() == b'Hello world!'


@pytest.mark.asyncio
async def test_part_message(server: TCPTestServerProtocol, client: TCPClientProtocol):
    client.send(b'abcde' * 500)

    assert await client.recv() == b'abcde' * 500


@pytest.mark.asyncio
async def test_part_messages(server: TCPTestServerProtocol, client: TCPClientProtocol):
    messages = [os.urandom(2000) for _ in range(10)]
    for message in messages:
        client.send(message)

    for message in messages:
        assert await client.recv() == message


@pytest.mark.asyncio
async def test_big_message(server: TCPTestServerProtocol, client: TCPClientProtocol):
    message = os.urandom(1024 * 1024 * 10)

    client.send(message)
    assert await client.recv(1024 * 1024 * 10) == message


@pytest.mark.asyncio
async def test_several_clients(server: TCPTestServerProtocol, clients: tp.List[TCPClientProtocol]):
    messages = [os.urandom(1024 * 1024) for _ in range(10)]

    for client, message in zip(clients, messages):
        client.send(message)

    for client, message in zip(clients, messages):
        assert await client.recv(1024 * 1024) == message

    await asyncio.sleep(1)  # waiting ack packets from clients


@pytest.mark.asyncio
async def test_client_recv(server: TCPTestServerProtocol, client: TCPClientProtocol):
    message = os.urandom(1024)
    client.send(message)

    part_one = await client.recv(512)
    part_two = await client.recv()

    assert part_one + part_two == message
