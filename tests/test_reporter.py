from unittest import TestCase
from nose.plugins.capture import Capture
from specter.reporting.console import ConsoleReporter
from specter.reporting.utils import TestStatus, pretty_print_args


class TestConsoleReporter(TestCase):

    def setUp(self):
        self.default_reporter = ConsoleReporter()
        self.console = Capture()
        self.console.begin()

    def tearDown(self):
        self.console.end()

    def _get_output(self):
        return self.console.buffer

    def test_get_name(self):
        self.assertEqual(self.default_reporter.get_name(),
                         'Simple BDD Serial console reporter')

    def test_process_args(self):
        class dotted_dict(object):
            def __getattr__(self, attr):
                return self.__dict__.get(attr)

        args = dotted_dict()
        args.no_color = True

        self.default_reporter.process_arguments(args)
        self.assertFalse(self.default_reporter.use_color)

    def test_no_color_print(self):
        self.default_reporter.use_color = False
        self.default_reporter.output('test', 0, TestStatus.PASS)

        self.assertEqual(self._get_output(), 'test\n')

    def test_color_print(self):
        self.default_reporter.output('test', 0, TestStatus.PASS)
        self.assertEqual(self._get_output(), '\x1b[32mtest\x1b[0m\n')


class TestReporterUtils(TestCase):
    def setUp(self):
        self.console = Capture()
        self.console.begin()

    def tearDown(self):
        self.console.end()

    def test_pretty_print_args_with_empty_kwargs(self):
        result = pretty_print_args(None)
        self.assertEqual(result, 'None')
