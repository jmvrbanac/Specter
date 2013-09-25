import inspect

from specter import _
from specter.spec import CaseWrapper, FailedRequireException


class ExpectAssert(object):

    def __init__(self, target, required=False):
        super(ExpectAssert, self).__init__()
        self.prefix = _('expect')
        self.target = target
        self.actions = [str(target)]
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

    def equal(self, expected):
        self.expected = expected
        self.actions.extend([_('equal'), str(expected)])
        self._verify_condition(condition=self.target == expected)

    def be_greater_than(self, expected):
        self.expected = expected
        self.actions.extend([_('be greater than'), str(expected)])
        self._verify_condition(condition=self.target > expected)

    def be_less_than(self, expected):
        self.expected = expected
        self.actions.extend([_('be less than'), str(expected)])
        self._verify_condition(condition=self.target < expected)

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
