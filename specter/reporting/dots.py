from sys import stdout

from specter import _
from specter.spec import TestEvent
from specter.reporting import AbstractConsoleReporterPlugin


class DotsReporter(AbstractConsoleReporterPlugin):

    def get_name(self):
        return _('Dots Reporter')

    def subscribe_to_describe(self, describe):
        describe.add_listener(TestEvent.COMPLETE, self.test_event)

    def test_event(self, evt):
        char = '.' if evt.payload.success else 'x'
        stdout.write(char)
        stdout.flush()

    def print_summary(self):
        print(_('\nTest Run Complete!'))
