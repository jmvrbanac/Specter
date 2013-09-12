from time import time
from types import FunctionType


class TimedObject(object):
    def __init__(self):
        super(TimedObject, self).__init__()
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.start_time = time()

    def stop(self):
        self.end_time = time()

    @property
    def elapsed_time(self):
        elapsed = self.end_time - self.start_time
        return elapsed if elapsed >= 0 else 0


class CaseWrapper(TimedObject):
    def __init__(self, case_func):
        super(CaseWrapper, self).__init__()
        self.case_func = case_func
        self.expects = []

    def execute(self, context=None):
        self.start()
        result = self.case_func(context or self)
        self.stop()
        return result

    @property
    def name(self):
        return self.case_func.func_name

    @property
    def doc(self):
        return self.case_func.__doc__


class Describe(object):
    def __init__(self):
        super(Describe, self).__init__()
        self.cases = [CaseWrapper(case_func) for case_func in self.case_funcs]
        self.describes = [desc_type() for desc_type in self.describe_types]

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def doc(self):
        return self.__dict__.__doc__

    @property
    def __members__(self):
        return {key: val for key, val in vars(type(self)).items()}

    @property
    def describe_types(self):
        return [val for key, val in self.__members__.items()
                if Describe.plugin_filter(val)]

    @property
    def case_funcs(self):
        return [val for key, val in self.__members__.items()
                if Describe.case_filter(val)]

    def before_each(self):
        pass

    def after_each(self):
        pass

    def execute(self):
        # Execute Cases
        for case in self.cases:
            self.before_each()
            case.execute(context=self)
            self.after_each()

        # Execute Suites
        for describe in self.describes:
            describe.execute()

    @classmethod
    def plugin_filter(cls, other):
        if not isinstance(other, type):
            return False

        return issubclass(other, Describe) and other is not cls

    @classmethod
    def case_filter(cls, obj):
        if type(obj) is not FunctionType:
            return False

        func_name = obj.func_name
        return (not func_name.startswith('_') and
                not func_name == 'execute' and
                not func_name == 'before_each' and
                not func_name == 'after_each')


class Spec(Describe):
    pass
