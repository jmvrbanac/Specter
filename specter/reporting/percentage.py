from sys import stdout

import six
import time

from specter import _
from specter.spec import TestEvent, DescribeEvent
from specter.reporting import AbstractConsoleReporterPlugin


class PercentageReporter(object):
    def __init__(self):
        super(PercentageReporter, self).__init__()
        self.modules = {}
        self.message = ''
        self.num_events = 0
        self.describes = []

    def get_name(self):
        return _('Percentage Reporter')

    def subscribe_to_describe(self, describe):
        self.describes.append(describe)
        describe.add_listener(TestEvent.COMPLETE, self.test_event)
        describe.add_listener(DescribeEvent.COMPLETE, self.describe_event)

    def test_event(self, evt):
        test_case = evt.payload
        describe = test_case.parent
        self.modules[describe.real_class_path] = self.get_numbers(describe)
        self.print_precentage_bars()

    def describe_event(self, evt):
        describe = evt.payload
        self.modules[describe.real_class_path] = self.get_numbers(describe)

    def get_numbers(self, describe):
        cases_completed = [case for case in describe.cases if case.complete]
        num_completed = float(len(cases_completed))
        num_total = float(len(describe.cases))
        return [num_completed, num_total]

    def get_bar(self, percentage):
        equals = int((percentage * 50))
        complete = '-' * equals
        remainder = '_' * (50 - equals)
        nice_percent = int((percentage * 100))
        bar = 'Test Progress: [{0}{1}] {2}%'.format(complete,
                                                    remainder,
                                                    nice_percent)
        return bar

    def get_message(self):
        total = 0
        completed = 0
        for module, value in six.iteritems(self.modules):
            completed += value[0]
            total += value[1]

        percentage = completed / total
        return self.get_bar(percentage)

    def wait_for_complete(self):
        complete = not False in [d.complete for d in self.describes]
        while not complete:
            for d in self.describes:
                print d.name, d.complete
            complete = not False in [d.complete for d in self.describes]
            time.sleep(0.1)

    def print_summary(self):
        #self.wait_for_complete()
        print('')

    def print_precentage_bars(self):
        amount_to_remove = len(self.message)
        backspaces = '\b \b' * amount_to_remove
        self.message = self.get_message()
        msg = '{back}{msg}'.format(back=backspaces, msg=self.message)

        stdout.write(msg)
        stdout.flush()
