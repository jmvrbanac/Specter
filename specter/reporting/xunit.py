from xml.etree.ElementTree import Element, tostring as element_to_str

import six
from specter.spec import DescribeEvent
from specter.reporting import AbstractParallelReporter, AbstractSerialReporter


class XUnitReporter(AbstractSerialReporter, AbstractParallelReporter):
    """ A simple xUnit format report generator for the Specter framework. """
    # TODO: Make this more efficient!

    def __init__(self):
        self.suites = []
        self.filename = ''

    def process_arguments(self, args):
        if args.xunit_results:
            self.filename = args.xunit_results

    def get_name(self):
        return 'xUnit report generator'

    def subscribe_to_describe(self, describe):
        describe.add_listener(DescribeEvent.COMPLETE, self.describe_complete)

    def describe_complete(self, evt):
        describe = evt.payload

        suite = XUnitTestSuite()
        suite.assign_describe(describe)
        self.suites.append(suite)

    def convert_to_xml(self):
        test_suites = Element('testsuites')

        for suite in self.suites:
            test_suites.append(suite.convert_to_xml())

        return test_suites

    def finished(self):
        if not self.filename:
            return

        body = element_to_str(self.convert_to_xml(), encoding='utf8')

        handle = open(self.filename, 'w')
        handle.write('{0}'.format(body))
        handle.close()


class XUnitTestSuite(object):
    def __init__(self):
        self.describe = None
        self.tests = []

    def assign_describe(self, describe):
        self.describe = describe
        for key, case in six.iteritems(self.describe.cases):
            test_case = XUnitTestCase()
            test_case.assign_case_wrapper(case)
            self.tests.append(test_case)

    @property
    def name(self):
        return self.describe.name

    @property
    def time(self):
        return str(self.describe.total_time)

    @property
    def errors(self):
        return str(len([test for test in self.tests if test.error]))

    @property
    def failures(self):
        return str(len([test for test in self.tests if not test.success]))

    @property
    def skipped(self):
        return str(len([test for test in self.tests if test.skipped]))

    def convert_to_xml(self):
        element = Element('testsuite', {'name': self.name,
                                        'tests': str(len(self.tests)),
                                        'errors': self.errors,
                                        'failures': self.failures,
                                        'skipped': self.skipped,
                                        'time': self.time})
        for test in self.tests:
            element.append(test.convert_to_xml())
        return element

    def __str__(self):
        return element_to_str(self.convert_to_xml(), encoding='utf8')


class XUnitTestCase(object):
    def __init__(self):
        self.case_wrapper = None

    @property
    def name(self):
        return str(self.case_wrapper.name)

    @property
    def error(self):
        return self.case_wrapper.error

    @property
    def success(self):
        return self.case_wrapper.success

    @property
    def skipped(self):
        return self.case_wrapper.skipped

    @property
    def failures(self):
        return [expect for expect in self.case_wrapper.expects
                if not expect.success]

    @property
    def module(self):
        return self.case_wrapper.parent.real_class_path

    @property
    def time(self):
        return str(self.case_wrapper.elapsed_time)

    def assign_case_wrapper(self, wrapper):
        self.case_wrapper = wrapper

    def convert_to_xml(self):
        failure_msg = """
<![CDATA[
Target: {target}: {target_param}
Expected: {expected}: {expected_param}
]]>"""

        element = Element('testcase', {'classname': self.module,
                                       'name': self.name,
                                       'time': self.time})

        # Add failures
        for expect in self.failures:
            failure = Element('failure', {
                'message': 'Failed: {0}'.format(expect)})
            failure.text = failure_msg.format(
                target=expect.target,
                target_param=expect.target_src_param,
                expected=expect.expected,
                expected_param=expect.expected_src_param)
            element.append(failure)

        # Add Skipped
        if self.skipped:
            skipped_element = Element('skipped')
            skipped_element.text = self.case_wrapper.skip_reason
            element.append(skipped_element)

        # Add Errors
        if self.error:
            msg = '<![CDATA['
            for err in self.error:
                msg += '{0}\n'.format(err)
            msg += ']]>'

            error_element = Element('error')
            error_element.text = msg
            element.append(error_element)

        return element

    def __str__(self):
        return element_to_str(self.convert_to_xml(), encoding='utf8')
