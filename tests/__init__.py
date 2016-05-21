import pytest


@pytest.fixture()
def pass_capfd(request, capfd):
    """Provide capfd object to unittest.TestCase instances"""
    request.instance.capfd = capfd
