from sys import stdout

from specter import _
from specter.spec import TestEvent
from specter.reporting import AbstractConsoleReporter
from specter.reporting import AbstractParallelReporter
from specter.reporting.console import print_test_msg, print_test_args
from specter.reporting.console import print_expects, TestStatus


class DotsReporter(AbstractConsoleReporter, AbstractParallelReporter):

    def __init__(self):
        super(DotsReporter, self).__init__()
        self.total = 0
        self.failed_tests = []

    def get_name(self):
        return _('Dots Reporter')

    def subscribe_to_describe(self, describe):
        describe.add_listener(TestEvent.COMPLETE, self.test_event)

    def print_error(self, wrapper):
        """ A crude way of output the errors for now. This needs to be
        cleaned up into something better.
        """
        level = 0
        parent = wrapper.parent
        while parent:
            print_test_msg(parent.name, level, TestStatus.FAIL)
            level += 1
            parent = parent.parent

        print_test_msg(wrapper.name, level, TestStatus.FAIL)
        print_test_args(wrapper.execute_kwargs, level, TestStatus.FAIL)

        if wrapper.error:
            for line in wrapper.error:
                print_test_msg(line, level+2, TestStatus.FAIL)

        print_expects(wrapper, level)

    def test_event(self, evt):
        self.total += 1
        if evt.payload.success:
            char = '.'
        else:
            char = 'x'
            self.failed_tests.append(evt.payload)
        stdout.write(char)
        stdout.flush()

    def print_summary(self):
        print(_('\n{0} Test(s) Executed!'.format(self.total)))

        if len(self.failed_tests) > 0:
            print(_('\nFailed test information:'))
            for wrapper in self.failed_tests:
                self.print_error(wrapper)
