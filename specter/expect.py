import inspect

from specter.spec import CaseWrapper


class ExpectAssert(object):

    def __init__(self, target):
        super(ExpectAssert, self).__init__()
        self.target = target
        self.actions = []
        self.success = False

    def to_be(self, expected):
        self.actions.extend([str(self.target), 'to be', str(expected)])
        try:
            assert self.target == expected
            self.success = True
        except:
            pass

        return self

    def __str__(self):
        action_str = ' '.join(self.actions)
        return 'expects {0}'.format(action_str)


def expect(obj):
    expect_obj = ExpectAssert(obj)
    try:
        for frame in inspect.stack():
            if frame[3] == 'execute':
                wrapper = frame[0].f_locals.get('self')
                if type(wrapper) is CaseWrapper:
                    wrapper.expects.append(expect_obj)
    except Exception as error:
        raise Exception('Error attempting to add expect to parent '
                        'wrapper: {err}'.format(err=error))

    return expect_obj
