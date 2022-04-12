import pytest

from spektrum.runner import SpektrumRunner


@pytest.fixture
def runner():
    yield SpektrumRunner()


def test_can_run(runner):
    runner.run(['./tests/example_data'])
    pass
