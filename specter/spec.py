from types import FunctionType


class SuiteResults(object):
    def __init__(self):
        super(SuiteResults, self).__init__()
        self.start_time = None
        self.end_time = None
        self.children = []


class Suite(object):
    def __init__(self):
        super(Suite, self).__init__()

    @property
    def __members__(self):
        return {key: val for key, val in vars(type(self)).items()}

    @property
    def child_suites(self):
        return [val for key, val in self.__members__.items()
                if Suite.plugin_filter(val)]

    @property
    def tests(self):
        return [val for key, val in self.__members__.items()
                if Suite.test_filter(val)]

    def execute(self):
        # Execute Tests
        for test_func in self.tests:
            result = test_func(self)

        # Execute Suites
        for child_type in self.child_suites:
            child = child_type()
            child.execute()

    @classmethod
    def plugin_filter(cls, other):
        if not isinstance(other, type):
            return False

        return issubclass(other, Suite) and other is not cls

    @classmethod
    def test_filter(cls, obj):
        if type(obj) is not FunctionType:
            return False

        func_name = obj.func_name
        return (not func_name.startswith('_') and
                not func_name == 'execute')
