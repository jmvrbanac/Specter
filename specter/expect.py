import inspect

from specter import _
from specter.spec import CaseWrapper


class ExpectAssert(object):

    def __init__(self, target):
        super(ExpectAssert, self).__init__()
        self.target = target
        self.actions = [str(target)]
        self.success = False
        self.used_negative = False

    def _verify_condition(self, condition):
        return condition if not self.used_negative else not condition

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
        self.actions.extend([_('equal'), str(expected)])
        result = self.target == expected
        self.success = self._verify_condition(result)

        return self

    def be_greater_than(self, expected):
        self.actions.extend([_('be greater than'), str(expected)])
        result = self.target > expected
        self.success = self._verify_condition(result)

        return self

    def be_less_than(self, expected):
        self.actions.extend([_('be less than'), str(expected)])
        result = self.target < expected
        self.success = self._verify_condition(result)

        return self

    def __str__(self):
        action_str = ' '.join(self.actions)
        return _('expects {0}').format(action_str)


def expect(obj):
    expect_obj = ExpectAssert(obj)
    try:
        for frame in inspect.stack():
            if frame[3] == 'execute':
                wrapper = frame[0].f_locals.get('self')
                if type(wrapper) is CaseWrapper:
                    wrapper.expects.append(expect_obj)
    except Exception as error:
        raise Exception(_('Error attempting to add expect to parent '
                        'wrapper: {err}').format(err=error))

    return expect_obj
