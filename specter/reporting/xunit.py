from xml.etree.ElementTree import Element, tostring as element_to_str
from specter import logger

log = logger.get(__name__)


class XUnitRenderer(object):
    def __init__(self, manager, reporting_options=None):
        self.manager = manager
        self.reporting_options = reporting_options or {}
        self.filename = self.reporting_options.get('xunit_results')
        self.report = None

    def convert_to_xml(self):
        element = Element('testsuites')

        for spec in self.report:
            test_suite = XUnitTestSuite(spec)
            element.append(test_suite.convert_to_xml())

        return element

    def render(self, report):
        if not self.filename:
            return

        self.report = report

        body = element_to_str(self.convert_to_xml(), encoding='utf8')

        handle = open(self.filename, 'w')
        handle.write(body.decode('utf8'))
        handle.close()


class XUnitTestSuite(object):
    def __init__(self, suite):
        self.suite = suite

    def convert_to_xml(self):
        element = Element('testsuite', {'name': self.suite.name})

        for case in self.suite.cases:
            test_case = XUnitTestCase(case)
            element.append(test_case.convert_to_xml())

        return element


class XUnitTestCase(object):
    def __init__(self, case):
        self.case = case

    def convert_to_xml(self):
        element = Element('testcase', {'name': self.case.raw_name})
        return element


