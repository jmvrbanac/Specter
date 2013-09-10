import inspect

class SuiteResults(object):
    def __init__(self):
        super(SuiteResults, self).__init__()
        self.start_time = None
        self.end_time = None
        self.children = []

class Suite(object):
    def __init__(self):
        super(Suite, self).__init__()
        self.results = []

    def get_nested_suites(self):
        members = inspect.getmembers(self)
        return [val for name, val in members if self.is_suite(val)]

    def execute(self):
        print self.get_nested_suites()

    @classmethod
    def is_suite(cls, obj_type):
        if not isinstance(obj_type, type):
            return False

        return issubclass(obj_type, Suite) and obj_type is not cls
