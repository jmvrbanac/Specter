import asyncio
from collections import defaultdict
import functools
import types
import uuid

from specter import logger, utils


class Spec(object):
    DATASET = {}
    __parent_cls__ = None
    __FIXTURE__ = False
    __CASE_CONCURRENCY__ = None
    __SPEC_CONCURRENCY__ = None

    def __init__(self, parent=None):
        self._id = str(uuid.uuid4())
        self._log = logger.get(utils.get_fullname(self))
        self.parent = parent
        self.children = [child(parent=self) for child in find_children(self)]
        self.__expects__ = defaultdict(list)
        self.__test_cases__ = [
            val
            for key, val in type(self).__members__().items()
            if case_filter(self, val)
        ]

        if self.DATASET:
            self.__build_data_spec__()

    @classmethod
    def get_parent_class_name(cls):
        parents = cls.__qualname__.split('.')[:-1]
        if not parents:
            return

        return parents[-1]

    def __build_data_spec__(self):
        cases = []
        for test_func in self.__test_cases__:
            base_metadata = get_case_data(test_func).metadata

            for name, data in self.DATASET.items():
                args, meta = data, dict(base_metadata)

                # Handle complex dataset item
                if 'args' in data and 'meta' in data:
                    args = data.get('args', {})
                    meta.update(data.get('meta', {}))

                # Extract name, args and duplicate function
                func_name = '{0}_{1}'.format(test_func.__name__, name)
                prefix, *_ = test_func.__qualname__.rpartition('.')

                new_func = types.FunctionType(
                    test_func.__code__,
                    test_func.__globals__,
                    func_name,
                    test_func.__defaults__,
                    test_func.__closure__,
                )
                new_func.__qualname__ = '{0}.{1}'.format(prefix, func_name)

                kwargs = utils.get_function_kwargs(test_func, args)

                case_data = get_case_data(new_func)
                case_data.type = 'data-driven'
                case_data.data_kwargs = kwargs

                test_func_data = get_case_data(test_func)
                case_data.incomplete = test_func_data.incomplete
                case_data.skip = test_func_data.skip

                if getattr(test_func, 'skipped', None):
                    test_func()
                    test_func_data = get_case_data(test_func)

                    case_data.skipped = test_func_data.skipped
                    case_data.skip_reason = test_func_data.skip_reason

                unbound_method = types.MethodType(new_func, self)

                setattr(self, func_name, unbound_method)
                get_case_data(new_func).metadata = meta
                cases.append(new_func)

        self.__test_cases__ = cases

    @classmethod
    def __members__(cls):
        classes = list(cls.__bases__) + [cls]

        all_members = {
            name: value
            for klass in classes
            for name, value in vars(klass).items()
            if name not in ['__parent_cls__']
        }

        # Add parent class references
        for name, value in all_members.items():
            if isinstance(value, type) and issubclass(value, Spec):
                all_members[name].__parent_cls__ = cls

        return all_members

    @classmethod
    def is_fixture(cls):
        return vars(cls).get('__FIXTURE__') is True

    @property
    def has_dependencies(self):
        for case in self.__test_cases__:
            data = getattr(case, '__specter__', None)
            if not data or not (data.skip or data.incomplete):
                return True

        for child in self.children:
            if child.has_dependencies:
                return True

        return False

    @utils.tag_as_inherited
    async def before_all(self):
        pass

    @utils.tag_as_inherited
    async def before_each(self):
        pass

    @utils.tag_as_inherited
    async def after_each(self):
        pass

    @utils.tag_as_inherited
    async def after_all(self):
        pass


class DataSpec(Spec):
    pass


class TestCaseData(object):
    def __init__(self):
        self.type = 'standard'
        self.incomplete = False
        self.skip = False
        self.skipped = False
        self.skip_reason = None
        self.metadata = {}
        self.data_kwargs = {}
        self.start_time = 0
        self.end_time = 0
        self.before_each_traces = []
        self.after_each_traces = []


def incomplete(f):
    get_case_data(f).incomplete = True
    return f


def skip(reason):
    """The skip decorator allows for you to always bypass a test.

    :param reason: Expects a string
    """
    def decorator(test_func):
        if not isinstance(test_func, (type, types.ModuleType)):
            # If a decorator, call down and save the results
            if test_func.__name__ == 'DECORATOR_ONCALL':
                test_func()

            get_case_data(test_func).skip = True

            @functools.wraps(test_func)
            def skip_wrapper(*args, **kwargs):
                data = get_case_data(test_func)
                data.skipped = True
                data.skip_reason = reason

            skip_wrapper.skipped = True

            test_func = skip_wrapper

        return test_func
    return decorator


def skip_if(condition, reason=None):
    """The skip_if decorator allows for you to bypass a test on conditions

    :param condition: Expects a boolean
    :param reason: Expects a string
    """
    if condition:
        return skip(reason)

    def wrapper(func):
        return func
    return wrapper


def metadata(**kv_pairs):
    def decorated(f):
        get_case_data(f).metadata = kv_pairs
        return f
    return decorated


def get_case_data(case):
    data = getattr(case, '__specter__', None)
    if not data:
        case.__specter__ = TestCaseData()
    return case.__specter__


def case_filter(cls, obj):
    if not isinstance(obj, types.FunctionType):
        return False

    reserved = [
        'before_each',
        'after_each',
        'before_all',
        'after_all',
    ]

    func_name = obj.__name__
    return (
        not func_name.startswith('_')
        and func_name not in reserved
    )


def spec_filter(cls, other):
    if not isinstance(other, type):
        return False

    if getattr(other, 'is_fixture') and other.is_fixture():
        return False

    return (
        issubclass(other, Spec)
        and other is not cls
        and other is not Spec
        and other is not DataSpec
    )


def find_children(cls):
    children = [
        val
        for key, val in cls.__members__().items()
        if spec_filter(cls, val)
    ]

    return children


def fixture(cls):
    """A decorator to set the fixture flag on the class."""
    setattr(cls, '__FIXTURE__', True)
    return cls


def concurrency(case=None, spec=None):
    """A decorator to override the case and child spec concurrency level."""

    def decorator(cls):
        if case:
            setattr(cls, '__CASE_CONCURRENCY__', asyncio.Semaphore(case))
        if spec:
            setattr(cls, '__SPEC_CONCURRENCY__', asyncio.Semaphore(spec))
        return cls

    return decorator
