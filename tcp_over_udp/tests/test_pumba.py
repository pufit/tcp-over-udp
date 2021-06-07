import pytest

from docker_composer import DockerCompose


@pytest.fixture(scope='module', autouse=True)
def build_docker():
    compose = DockerCompose()
    compose.up(no_start=True, no_deps=True, build=True).call()
    yield
    compose.down().call()


@pytest.fixture(scope='function')
def compose():
    compose = DockerCompose()
    yield compose
    compose.down().call()


def test_loss(compose):
    compose.up(abort_on_container_exit=True, detach=False).call('main-server', 'main-client', 'loss').check_returncode()


def test_delay(compose):
    compose.up(abort_on_container_exit=True, detach=False).call('main-server', 'main-client', 'delay').check_returncode()


def test_duplicate(compose):
    compose.up(abort_on_container_exit=True, detach=False).call('main-server', 'main-client', 'duplicate').check_returncode()


def test_corrupt(compose):
    compose.up(abort_on_container_exit=True, detach=False).call('main-server', 'main-client', 'corrupt').check_returncode()


def test_all(compose):
    compose.up(abort_on_container_exit=True, detach=False).call(
        'main-server',
        'main-client',
        'loss',
        'delay',
        'duplicate',
        'corrupt',
    ).check_returncode()
