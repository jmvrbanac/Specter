import sys
from random import shuffle
from time import time
from types import FunctionType
from pyevents.manager import EventDispatcher
from pyevents.event import Event


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
    def __init__(self, case_func, parent):
        super(CaseWrapper, self).__init__()
        self.case_func = case_func
        self.expects = []
        self.parent = parent

    def execute(self, context=None):
        self.start()
        result = self.case_func(context or self)
        self.stop()
        return result

    @property
    def name(self):
        return self.case_func.func_name

    @property
    def pretty_name(self):
        return self.case_func.func_name.replace('_', ' ')

    @property
    def doc(self):
        return self.case_func.__doc__

    @property
    def success(self):
        return len([exp for exp in self.expects if not exp.success]) == 0


class Describe(EventDispatcher):
    def __init__(self, parent=None):
        super(Describe, self).__init__()
        self.parent = parent
        self.cases = [CaseWrapper(case_func, parent=self)
                      for case_func in self.case_funcs]
        self.describes = [desc_type(parent=self)
                          for desc_type in self.describe_types]

        shuffle(self.cases)
        shuffle(self.describes)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def doc(self):
        return self.__dict__.__doc__

    @property
    def __members__(self):
        if sys.version_info<(2,7,0):
            results = dict((key, val)
                           for key, val in vars(type(self)).items())
        else:
            results = {key: val for key, val in vars(type(self)).items()}
        return results

    @property
    def describe_types(self):
        return [val for key, val in self.__members__.items()
                if Describe.plugin_filter(val)]

    @property
    def case_funcs(self):
        return [val for key, val in self.__members__.items()
                if Describe.case_filter(val)]

    @property
    def top_parent(self):
        parent_above = last_parent = self.parent or self

        while parent_above is not None:
            last_parent = parent_above
            parent_above = parent_above.parent

        return last_parent

    def before_each(self):
        pass

    def after_each(self):
        pass

    def execute(self):
        self.top_parent.dispatch(DescribeEvent(DescribeEvent.START, self))
        # Execute Cases
        for case in self.cases:
            self.before_each()
            case.execute(context=self)
            self.after_each()
            self.top_parent.dispatch(TestEvent(case))

        # Execute Suites
        for describe in self.describes:
            describe.execute()
        self.top_parent.dispatch(DescribeEvent(DescribeEvent.COMPLETE, self))

    @classmethod
    def plugin_filter(cls, other):
        if not isinstance(other, type):
            return False

        return (issubclass(other, Describe) and
                other is not cls
                and other is not Spec)

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


class DescribeEvent(Event):
    START = 'start'
    COMPLETE = 'complete'


class TestEvent(Event):
    COMPLETE = 'test_complete'

    def __init__(self, payload):
        super(TestEvent, self).__init__(TestEvent.COMPLETE, payload=payload)
