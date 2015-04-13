from specter import _
from specter.spec import TestEvent, DescribeEvent, DataDescribe
from specter.reporting import AbstractConsoleReporter, AbstractSerialReporter
from specter.reporting.utils import (
    TestStatus, print_expects, print_to_screen, get_color_from_status,
    print_test_args, get_item_level, print_indent_msg, ConsoleColors)


class ConsoleReporter(AbstractConsoleReporter, AbstractSerialReporter):
    """ Simple BDD Style console reporter. """

    def __init__(self, output_docstrings=False, use_color=True):
        super(ConsoleReporter, self).__init__()
        self.use_color = use_color
        self.test_total = 0
        self.test_expects = 0
        self.passed_tests = 0
        self.skipped_tests = 0
        self.errored_tests = 0
        self.failed_tests = 0
        self.incomplete_tests = 0
        self.output_docstrings = output_docstrings
        self.show_all = False

    def get_name(self):
        return 'Simple BDD Serial console reporter'

    def add_arguments(self, argparser):
        argparser.add_argument(
            '--show-all-expects', dest='show_all_expects', action='store_true',
            help=_('Displays all expectations for test cases'))

    def process_arguments(self, args):
        if args.no_color:
            self.use_color = False
        if args.show_all_expects:
            self.show_all = True

    def get_test_case_status(self, test_case, name):
        status = TestStatus.FAIL
        if (test_case.success
                and not test_case.skipped
                and not test_case.incomplete):
            status = TestStatus.PASS
        elif test_case.incomplete:
            status = TestStatus.INCOMPLETE
            name = u'{name} (incomplete)'.format(name=name)
        elif test_case.skipped:
            status = TestStatus.SKIP
            name = u'{name} (skipped): {reason}'.format(
                name=name, reason=test_case.skip_reason)
        elif test_case.error:
            status = TestStatus.ERROR

        return status, name

    def add_to_totals(self, test_case):
        self.test_total += 1
        if (test_case.success
                and not test_case.skipped
                and not test_case.incomplete):
            self.passed_tests += 1
        elif test_case.skipped:
            self.skipped_tests += 1
        elif test_case.incomplete:
            self.incomplete_tests += 1
        elif test_case.error:
            self.errored_tests += 1
        else:
            self.failed_tests += 1
        self.test_expects += len(test_case.expects)

    def output_test_case_result(self, test_case, level):
        name = test_case.pretty_name
        if level > 0:
            name = u'\u221F {0}'.format(name)

        status, name = self.get_test_case_status(test_case, name)

        self.output(name, level, status)
        print_test_args(test_case.execute_kwargs, level, status,
                        self.use_color)

        if test_case.doc and self.output_docstrings:
            print_indent_msg(test_case.doc, level + 1, status)

        # Print error if it exists
        if test_case.error:
            for line in test_case.error:
                self.output(line, level + 2, TestStatus.FAIL)

        if status == TestStatus.FAIL or self.show_all:
            print_expects(test_case, level, self.use_color)

    def subscribe_to_spec(self, spec):
        spec.add_listener(TestEvent.COMPLETE, self.test_complete)
        spec.add_listener(DescribeEvent.START, self.start_spec)

    def test_complete(self, evt):
        test_case = evt.payload
        level = get_item_level(test_case)

        self.output_test_case_result(test_case, level)

        self.add_to_totals(test_case)

    def start_spec(self, evt):
        level = get_item_level(evt.payload)
        name = evt.payload.name
        if level > 0:
            name = u'\u221F {0}'.format(name)

        # Output Spec name
        color = ConsoleColors.GREEN if self.use_color else None
        print_indent_msg(name, level, color=color)

        # Output Docstrings if enabled
        if evt.payload.doc and self.output_docstrings:
            print_indent_msg(evt.payload.doc, level + 1)

        # Warn of duplicates
        if isinstance(evt.payload, DataDescribe) and evt.payload.dup_count:
            color = ConsoleColors.YELLOW if self.use_color else None
            print_indent_msg('Warning: Noticed {0} duplicate data '
                             'set(s)'.format(evt.payload.dup_count),
                             level + 1, color=color)

    def output(self, msg, indent, status=None):
        """ Alias for print_indent_msg with color determined by status."""
        color = None
        if self.use_color:
            color = get_color_from_status(status)
        print_indent_msg(msg, indent, color)

    def print_summary(self):
        msg = """------- Summary --------
Pass            | {passed}
Skip            | {skipped}
Fail            | {failed}
Error           | {errored}
Incomplete      | {incomplete}
Test Total      | {total}
 - Expectations | {expects}
""".format(
            total=self.test_total, passed=self.passed_tests,
            failed=self.failed_tests, expects=self.test_expects,
            skipped=self.skipped_tests, incomplete=self.incomplete_tests,
            errored=self.errored_tests)

        status = TestStatus.FAIL
        if self.failed_tests == 0 and self.errored_tests == 0:
            status = TestStatus.PASS

        print_to_screen('\n')
        self.output('-' * 24, 0, status)
        self.output(msg, 0, status)
        self.output('-' * 24, 0, status)
