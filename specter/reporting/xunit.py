from specter import logger

log = logger.get(__name__)


class XUnitRenderer(object):
    def __init__(self, manager, reporting_options=None):
        self.manager = manager
        self.reporting_options = reporting_options or {}

    def render(self, report):
        print("************************")
        print("XUnitRenderer!")
        print("************************")