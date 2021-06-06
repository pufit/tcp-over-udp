import pytest

from docker_composer import DockerCompose


@pytest.fixture(scope='module', autouse=True)
def build_docker():
    compose = DockerCompose()
    compose.up(no_start=True, no_deps=True, build=True).call()
    yield
    compose.down().call()


def test_loss():
    compose = DockerCompose()
    compose.up(abort_on_container_exit=True, detach=False).call('main-server', 'main-client', 'loss').check_returncode()
    compose.down().call()


def test_delay():
    compose = DockerCompose()
    compose.up(abort_on_container_exit=True, detach=False).call('main-server', 'main-client', 'delay').check_returncode()
    compose.down().call()


def test_duplicate():
    compose = DockerCompose()
    compose.up(abort_on_container_exit=True, detach=False).call('main-server', 'main-client', 'duplicate').check_returncode()
    compose.down().call()


def test_corrupt():
    compose = DockerCompose()
    compose.up(abort_on_container_exit=True, detach=False).call('main-server', 'main-client', 'corrupt').check_returncode()
    compose.down().call()


def test_all():
    compose = DockerCompose()
    compose.up(abort_on_container_exit=True, detach=False).call(
        'main-server',
        'main-client',
        'loss',
        'delay',
        'duplicate',
        'corrupt',
    ).check_returncode()
    compose.down().call()
