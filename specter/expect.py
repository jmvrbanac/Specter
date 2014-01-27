import inspect
import functools
# Making sure we support 2.7 and 3+
try:
    from types import ClassType as ClassObjType
except:
    from types import ModuleType as ClassObjType

from specter import _
from specter.spec import (CaseWrapper, FailedRequireException,
                          TestSkippedException, TestIncompleteException)
from specter.util import get_called_src_line, get_expect_param_strs


class ExpectAssert(object):

    def __init__(self, target, required=False, src_params=None,
                 caller_args=[]):
        super(ExpectAssert, self).__init__()
        self.prefix = _('expect')
        self.target = target
        self.target_src_param = src_params[0] if src_params else None
        self.expected_src_param = src_params[1] if src_params else None
        self.actions = [target]
        self.success = False
        self.used_negative = False
        self.required = required
        self.caller_args = caller_args
        self.custom_msg = None

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
        self.actions.extend([action_name, expected])
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
                      condition=self.target is None)

    def be_true(self):
        self._compare(action_name=_('be'), expected=True,
                      condition=self.target)

    def be_false(self):
        self._compare(action_name=_('be'), expected=False,
                      condition=not self.target)

    def contain(self, expected):
        self._compare(action_name=_('contain'), expected=expected,
                      condition=expected in self.target)

    def be_in(self, expected):
        self._compare(action_name=_('be in'), expected=expected,
                      condition=self.target in expected)

    def raise_a(self, exception):
        self.expected = exception
        self.actions.extend(['raise', exception])
        condition = False

        try:
            self.target(*self.caller_args)
        except Exception as e:
            condition = True and type(e) is exception

        self.success = condition if not self.used_negative else not condition

        if not self.success:
            was = 'wasn\'t' if self.used_negative else 'was'
            msg = _('Function {func_name} {was} expected to raise "{excpt}"'
                    ''.format(func_name=self.target_src_param,
                              excpt=self.expected.__name__,
                              was=was))
            self.custom_msg = msg

    def __str__(self):
        action_list = []
        action_list.extend(self.actions)
        action_list[0] = self.target_src_param or str(self.target)
        action_list[-1] = self.expected_src_param or str(self.expected)

        return ' '.join([str(action) for action in action_list])


class RequireAssert(ExpectAssert):

    def __init__(self, target, src_params=None, caller_args=[]):
        super(RequireAssert, self).__init__(target=target, required=True,
                                            src_params=src_params,
                                            caller_args=caller_args)
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


def expect(obj, caller_args=[]):
    """ Primary method for test assertions in Specter
    :param obj: The evaluated target object
    :param caller_args: Is only used when using expecting a raised Exception
    """
    src_line = get_called_src_line(use_child_attr='__spec__')
    src_params = get_expect_param_strs(src_line)
    expect_obj = ExpectAssert(obj, src_params=src_params,
                              caller_args=caller_args)
    _add_expect_to_wrapper(expect_obj)
    return expect_obj


def require(obj, caller_args=[]):
    """ Primary method for test assertions in Specter
    :param obj: The evaluated target object
    :param caller_args: Is only used when using expecting a raised Exception
    """
    src_line = get_called_src_line(use_child_attr='__spec__')
    src_params = get_expect_param_strs(src_line)
    require_obj = RequireAssert(obj, src_params=src_params,
                                caller_args=caller_args)
    _add_expect_to_wrapper(require_obj)
    return require_obj


def skip(reason):
    """ The skip decorator allows for you to always bypass a test.

    :param reason: Expects a string
    """
    def decorator(test_func):
        if not isinstance(test_func, (type, ClassObjType)):
            func_data = None
            if test_func.__name__ == 'DECORATOR_ONCALL':
                # Call down and save the results
                func_data = test_func()

            @functools.wraps(test_func)
            def skip_wrapper(*args, **kwargs):
                other_data = {
                    'real_func': func_data[0] if func_data else test_func,
                    'metadata': func_data[1] if func_data else None
                }
                raise TestSkippedException(test_func, reason, other_data)
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


def metadata(**key_value_pairs):
    """ The metadata decorator allows for you to tag specific tests with
    key/value data for run-time processing or reporting. The common use case
    is to use metadata to tag a test as a positive or negative test type.

    .. code-block:: python

        # Example of using the metadata decorator
        @metadata(type='negative')
        def it_shouldnt_do_something(self):
            pass
    """
    def onTestFunc(func):
        def DECORATOR_ONCALL(*args, **kwargs):
            return (func, key_value_pairs)
        return DECORATOR_ONCALL
    return onTestFunc
