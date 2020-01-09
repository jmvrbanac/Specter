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
            element = self.suite_tree(spec, element)

        return element

    def suite_tree(self, spec, element):
        test_suite = XUnitTestSuite(spec)
        element.append(test_suite.convert_to_xml())

        for child_spec in spec.specs:
            element = self.suite_tree(child_spec, element)

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

    @property
    def name(self):
        return self.suite.name

    @property
    def time(self):
        return "N/A"

    @property
    def errors(self):
        return str(len([case for case in self.suite.cases if case.errors]))

    @property
    def failures(self):
        return str(len([case for case in self.suite.cases if not case.successful]))

    @property
    def skipped(self):
        return str(len([case for case in self.suite.cases if case.skipped or case.incomplete]))

    @property
    def tests(self):
        return str(len(self.suite.cases))

    def convert_to_xml(self):
        element = Element('testsuite', {'name': self.name,
                                        'time': self.time,
                                        'errors': self.errors,
                                        'failures': self.failures,
                                        'skipped': self.skipped,
                                        'tests': self.tests})

        for case in self.suite.cases:
            test_case = XUnitTestCase(case)
            element.append(test_case.convert_to_xml())

        return element


class XUnitTestCase(object):
    def __init__(self, case):
        self.case = case

    @property
    def name(self):
        return self.case.raw_name

    @property
    def classname(self):
        return "N/A"

    @property
    def time(self):
        return "N/A"

    def convert_to_xml(self):
        element = Element('testcase', {'name': self.name,
                                       'classname': self.classname,
                                       'time': self.time})
        return element


