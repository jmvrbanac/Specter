from collections import defaultdict
import types
import uuid

from specter import logger, utils


class Spec(object):
    __FIXTURE__ = False

    def __init__(self, parent=None):
        self._id = str(uuid.uuid4())
        self._log = logger.get(utils.get_fullname(self))
        self.parent = parent
        self.children = [child(parent=self) for child in find_children(self)]
        self.__expects__ = defaultdict(list)

    @classmethod
    def __members__(cls):
        classes = list(cls.__bases__) + [cls]

        all_members = {
            name: value
            for klass in classes
            for name, value in vars(klass).items()
        }

        return all_members

    @property
    def __test_cases__(self):
        return [
            val
            for key, val in self.__members__().items()
            if case_filter(self, val)
        ]

    @classmethod
    def is_fixture(cls):
        return getattr(cls, '__FIXTURE__', False) is True

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


class TestCaseData(object):
    def __init__(self):
        self.incomplete = False
        self.metadata = {}
        self.start_time = 0
        self.end_time = 0


def incomplete(f):
    get_case_data(f).incomplete = True
    return f


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


def child_filter(cls, other):
    if not isinstance(other, type):
        return False

    if getattr(other, 'is_fixture') and other.is_fixture():
        return False

    return (
        issubclass(other, Spec)
        and other is not cls
        and other is not Spec
    )


def find_children(cls):
    return [
        val
        for key, val in cls.__members__().items()
        if child_filter(cls, val)
    ]


def case_as_dict(spec, case):
    data = get_case_data(case)
    tracebacks = getattr(case, '__tracebacks__', [])
    successful = (
        not tracebacks and
        all(expect.success for expect in spec.__expects__[case])
    )

    # TODO: Clean this up
    for tb in tracebacks:
        frame = tb['frame']
        filename = frame.f_code.co_filename
        separator = '-' * (len(filename) + 2)

        formatted = ['|  ' + line for line in tb['source']]
        formatted[-1] = f'-->' + formatted[-1][2:]
        tb['formatted'] = '\n'.join([
            separator,
            f'- {filename}',
            separator,
            *formatted,
            separator,
        ])

    return {
        'name': utils.snakecase_to_spaces(case.__name__),
        'raw_name': case.__name__,
        'start': data.start_time,
        'end': data.end_time,
        'success': successful,
        'skipped': False,
        'metadata': data.metadata,
        'expects': [
            {
                'evaluation': str(exp),
                'required': exp.required,
                'success': exp.success,
            }
            for exp in spec.__expects__[case]
        ],
        'error': '\n'.join([tb['formatted'] for tb in tracebacks]) or None
    }


def spec_as_dict(spec):
    return {
        'name': utils.camelcase_to_spaces(type(spec).__name__),
        'module': spec.__module__,
        'doc': spec.__doc__,
        'cases': [
            case_as_dict(spec, case)
            for case in spec.__test_cases__
        ],
        'specs': [
            spec_as_dict(child)
            for child in spec.children
        ],
    }
