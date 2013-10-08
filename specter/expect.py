import inspect
import functools
# Making sure we support 2.7 and 3+
try:
    from types import ClassType as ClassObjType
except:
    from types import ModuleType as ClassObjType

from specter import _
from specter.spec import (CaseWrapper, FailedRequireException,
                          TestSkippedException)


class ExpectAssert(object):

    def __init__(self, target, required=False):
        super(ExpectAssert, self).__init__()
        self.prefix = _('expect')
        self.target = target
        self.actions = ['"{target}"'.format(target=str(target))]
        self.success = False
        self.used_negative = False
        self.required = required

    def _verify_condition(self, condition):
        self.success = condition if not self.used_negative else not condition
        if self.required and not self.success:
            raise FailedRequireException()
        return self.success

    @property
    def not_to(self):
        self.actions.append(_('not'))
        self.used_negative = not self.used_negative
        return self.to

    @property
    def to(self):
        self.actions.append(_('to'))
        return self

    def _compare(self, action_name, expected, condition):
        self.expected = expected
        self.actions.extend([action_name, '"{0}"'.format(str(expected))])
        self._verify_condition(condition=condition)

    def equal(self, expected):
        self._compare(action_name=_('equal'), expected=expected,
                      condition=self.target == expected)

    def be_greater_than(self, expected):
        self._compare(action_name=_('be greater than'), expected=expected,
                      condition=self.target > expected)

    def be_less_than(self, expected):
        self._compare(action_name=_('be less than'), expected=expected,
                      condition=self.target < expected)

    def be_none(self):
        self._compare(action_name=_('be'), expected=None,
                      condition=self.target == None)

    def be_true(self):
        self._compare(action_name=_('be'), expected=True,
                      condition=self.target == True)

    def be_false(self):
        self._compare(action_name=_('be'), expected=False,
                      condition=self.target == False)

    def contain(self, expected):
        self._compare(action_name=_('contain'), expected=expected,
                      condition=expected in self.target)

    def __str__(self):
        action_str = ' '.join(self.actions)
        return _('{prefix} {action}').format(prefix=self.prefix,
                                             action=action_str)


class RequireAssert(ExpectAssert):

    def __init__(self, target):
        super(RequireAssert, self).__init__(target=target, required=True)
        self.prefix = _('require')


def _add_expect_to_wrapper(obj_to_add):
    try:
        for frame in inspect.stack():
            if frame[3] == 'execute':
                wrapper = frame[0].f_locals.get('self')
                if type(wrapper) is CaseWrapper:
                    wrapper.expects.append(obj_to_add)
    except Exception as error:
        raise Exception(_('Error attempting to add expect to parent '
                        'wrapper: {err}').format(err=error))


def expect(obj):
    expect_obj = ExpectAssert(obj)
    _add_expect_to_wrapper(expect_obj)
    return expect_obj


def require(obj):
    require_obj = RequireAssert(obj)
    _add_expect_to_wrapper(require_obj)
    return require_obj


def skip(reason):
    def decorator(test_func):
        if not isinstance(test_func, (type, ClassObjType)):
            @functools.wraps(test_func)
            def skip_wrapper(*args, **kwargs):
                raise TestSkippedException(test_func, reason)
            test_func = skip_wrapper
        return test_func
    return decorator


def skip_if(condition, reason=None):
    if condition:
        return skip(reason)

    def wrapper(func):
        return func
    return wrapper
