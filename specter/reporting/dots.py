from sys import stdout

from specter import _
from specter.spec import TestEvent
from specter.reporting import AbstractConsoleReporterPlugin


class DotsReporter(AbstractConsoleReporterPlugin):

    def __init__(self):
        super(DotsReporter, self).__init__()
        self.total = 0

    def get_name(self):
        return _('Dots Reporter')

    def subscribe_to_describe(self, describe):
        describe.add_listener(TestEvent.COMPLETE, self.test_event)

    def test_event(self, evt):
        self.total += 1
        char = '.' if evt.payload.success else 'x'
        stdout.write(char)
        stdout.flush()

    def print_summary(self):
        print(_('\n{0} Test(s) completed!'.format(self.total)))
