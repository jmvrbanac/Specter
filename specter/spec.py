from collections import defaultdict
import types

from specter import logger, utils


class Spec(object):
    __FIXTURE__ = False

    def __init__(self, parent=None):
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
