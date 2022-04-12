from xml.etree.ElementTree import Element, tostring as element_to_str
from spektrum import logger, utils

log = logger.get(__name__)


class XUnitRenderer(object):
    def __init__(self, reporting_options=None):
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
        return str(self.suite.elapsed_time)

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
        element = Element(
            'testsuite',
            attrib={
                'name': self.name,
                'time': self.time,
                'errors': self.errors,
                'failures': self.failures,
                'skipped': self.skipped,
                'tests': self.tests,
            },
        )

        for case in self.suite.cases:
            test_case = XUnitTestCase(case)
            element.append(test_case.convert_to_xml())

        return element


class XUnitTestCase(object):
    def __init__(self, case):
        self.case = case
        self.skipped_case = XUnitSkippedCase(self.case)
        self.failure_case = XUnitFailureCase(self.case)
        self.error_case = XUnitErrorCase(self.case)

    @property
    def name(self):
        return self.case.raw_name

    @property
    def classname(self):
        return self.case.class_name

    @property
    def time(self):
        return str(self.case.elapsed_time)

    def convert_to_xml(self):
        element = Element(
            'testcase',
            attrib={
                'name': self.name,
                'classname': self.classname,
                'time': self.time,
            },
        )

        if self.skipped_case.has_skipped_case:
            element.append(self.skipped_case.convert_to_xml())

        if self.failure_case.has_failure_case:
            element.extend(self.failure_case.convert_to_xml())

        if self.error_case.has_error_case:
            element.append(self.error_case.convert_to_xml())

        return element


class XUnitSkippedCase(object):
    def __init__(self, case):
        self.case = case

    @property
    def has_skipped_case(self):
        return self.case.skipped or self.case.incomplete

    @property
    def skip_msg(self):
        if self.case.incomplete:
            return "Test Case Marked as Incomplete."
        return self.case.skip_reason

    def convert_to_xml(self):
        element = Element('skipped')
        element.text = self.skip_msg
        return element


class XUnitFailureCase(object):
    def __init__(self, case):
        self.case = case

    @property
    def has_failure_case(self):
        return not self.case.successful and not self.case.errors

    @staticmethod
    def failure_message(expect):
        return f'Failed: {expect.evaluation}'

    @staticmethod
    def failure_body(expect):
        return f"""
        <![CDATA[
        Target: {expect.target} : {expect.target_name}
        Expected: {expect.expected} : {expect.expected_name}
        ]]>
        """

    def convert_to_xml(self):
        elements = []

        for expect in self.case.expects:
            if not expect.success:
                element = Element('failure', {'message': self.failure_message(expect)})
                element.text = self.failure_body(expect)
                elements.append(element)

        return elements


class XUnitErrorCase(object):
    def __init__(self, case):
        self.case = case

    @property
    def has_error_case(self):
        return self.case.errors

    @staticmethod
    def error_message(errors, error_type):
        all_errors = ''
        for error in errors:
            all_errors += '\n'.join(str(line) for line in error)

        return f'''
        <![CDATA[{utils.traceback_occurred_msg(error_type)}:
        {all_errors}
        ]]>
        '''

    def convert_to_xml(self):
        element = Element('error')
        element.text = self.error_message(self.case.errors, self.case.error_type)
        return element
