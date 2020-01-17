import pytest

from specter.runner import SpecterRunner


@pytest.fixture
def runner():
    yield SpecterRunner()


def test_can_run(runner):
    runner.run(['./tests/example_data'])
    pass
