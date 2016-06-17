from unittest import TestCase
import pytest

from specter.reporting.console import ConsoleReporter
from specter.reporting.utils import TestStatus, pretty_print_args

from specter.reporting.xunit import XUnitReporter
from specter.spec import DescribeEvent, Describe

import os
import xml.etree.ElementTree as ET


@pytest.fixture()
def pass_capfd(request, capfd):
    """Provide capfd object to unittest.TestCase instances"""
    request.instance.capfd = capfd


@pytest.mark.usefixtures('pass_capfd')
class TestConsoleReporter(TestCase):

    def setUp(self):
        self.default_reporter = ConsoleReporter()

    def _get_output(self):
        stdout, _ = self.capfd.readouterr()
        return stdout

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
    def test_pretty_print_args_with_empty_kwargs(self):
        result = pretty_print_args(None)
        self.assertEqual(result, 'None')


class TestXUnitReporter(TestCase):

    def test_outputs_valid_xml(self):
        xunit_reporter = XUnitReporter()
        describe = Describe()
        describe_event = DescribeEvent(DescribeEvent.COMPLETE, describe)
        xunit_reporter.describe_complete(describe_event)
        xunit_reporter.filename = 'xunit.xml'
        try:
            xunit_reporter.finished()
            ET.parse(xunit_reporter.filename)
        finally:
            os.remove(xunit_reporter.filename)
