import inspect
import functools
import re
# Making sure we support 2.7 and 3+
try:
    from types import ClassType as ClassObjType
except:
    from types import ModuleType as ClassObjType

from specter import _
from specter.spec import (CaseWrapper, FailedRequireException,
                          TestSkippedException, TestIncompleteException)


class ExpectAssert(object):

    def __init__(self, target, required=False, src_params=None):
        super(ExpectAssert, self).__init__()
        self.prefix = _('expect')
        self.target = target
        self.target_src_param = src_params[0] if src_params else None
        self.expected_src_param = src_params[1] if src_params else None
        self.actions = ['{target}'.format(
            target=self.target_src_param or str(target))]
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
        self.actions.extend([action_name, '{0}'.format(
            self.expected_src_param or str(expected))])
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

    def be_in(self, expected):
        self._compare(action_name=_('be in'), expected=expected,
                      condition=expected in self.target)

    def __str__(self):
        action_str = ' '.join(self.actions)
        return _('{prefix} {action}').format(prefix=self.prefix,
                                             action=action_str)


class RequireAssert(ExpectAssert):

    def __init__(self, target, src_params=None):
        super(RequireAssert, self).__init__(target=target, required=True,
                                            src_params=src_params)
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


def get_called_src_line():
    src_line = None
    try:
        last_frame = inspect.currentframe().f_back.f_back
        last_module = inspect.getmodule(type(last_frame.f_locals['self']))
        line = last_frame.f_lineno - 1
        src_line = inspect.getsourcelines(last_module)[0][line]
    except:
        pass
    return src_line


def get_expect_param_strs(src_line):
    matches = re.search('\((.*?)\)\..*\((.*?)\)', src_line)
    return (matches.group(1), matches.group(2)) if matches else None


def expect(obj):
    src_params = get_expect_param_strs(get_called_src_line())
    expect_obj = ExpectAssert(obj, src_params=src_params)
    _add_expect_to_wrapper(expect_obj)
    return expect_obj


def require(obj):
    src_params = get_expect_param_strs(get_called_src_line())
    require_obj = RequireAssert(obj, src_params=src_params)
    _add_expect_to_wrapper(require_obj)
    return require_obj


def skip(reason):
    """ The skip decorator allows for you to always bypass a test.

    :param reason: Expects a string
    """
    def decorator(test_func):
        if not isinstance(test_func, (type, ClassObjType)):
            @functools.wraps(test_func)
            def skip_wrapper(*args, **kwargs):
                raise TestSkippedException(test_func, reason)
            test_func = skip_wrapper
        return test_func
    return decorator


def skip_if(condition, reason=None):
    """ The skip_if decorator allows for you to bypass a test given that a
    specific condition is met.

    :param condition: Expects a boolean
    :param reason: Expects a string
    """
    if condition:
        return skip(reason)

    def wrapper(func):
        return func
    return wrapper


def incomplete(test_func):
    """ The incomplete decorator behaves much like a normal skip; however,
    tests that are marked as incomplete get tracked under a different metric.
    This allows for you to create a skeleton around all of your features and
    specifications, and track what tests have been written and what
    tests are left outstanding.

    .. code-block:: python

        # Example of using the incomplete decorator
        @incomplete
        def it_should_do_something(self):
            pass
    """
    if not isinstance(test_func, (type, ClassObjType)):
        @functools.wraps(test_func)
        def skip_wrapper(*args, **kwargs):
            raise TestIncompleteException(test_func, _('Test is incomplete'))
        return skip_wrapper
