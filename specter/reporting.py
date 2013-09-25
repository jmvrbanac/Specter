from specter.spec import TestEvent, DescribeEvent


class ConsoleColors():
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class ConsoleReporter(object):
    """ Temporary console reporter.
    At least until I can get a real one written.
    """
    INDENT = 2

    def __init__(self, output_docstrings=False):
        super(ConsoleReporter, self).__init__()
        self.test_total = 0
        self.test_expects = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.output_docstrings = output_docstrings

    def add_describe(self, describe):
        describe.add_listener(TestEvent.COMPLETE, self.event_received)
        describe.add_listener(DescribeEvent.START, self.start_describe)

    def print_passfail_msg(self, msg, level, success=True):
        if success:
            self.print_indent_msg(
                msg=msg, level=level, color=ConsoleColors.GREEN)
        else:
            self.print_indent_msg(
                msg=msg, level=level, color=ConsoleColors.RED)

    def print_indent_msg(self, msg, level=0, color=ConsoleColors.WHITE):
        indent = u' ' * self.INDENT
        msg = u'{0}{1}'.format(str(indent * level), msg)
        self.print_colored(msg=msg, color=color)

    def print_colored(self, msg, color=ConsoleColors.WHITE):
        print u'\033[{color}m{msg}\033[0m'.format(color=color, msg=msg)

    def get_item_level(self, item):
        levels = 0
        parent_above = item.parent
        while parent_above is not None:
            levels += 1
            parent_above = parent_above.parent
        return levels

    def event_received(self, evt):
        test_case = evt.payload
        level = self.get_item_level(test_case)
        name = test_case.pretty_name
        if level > 0:
            name = u'\u221F {0}'.format(name)

        self.print_passfail_msg(name, level, test_case.success)

        if test_case.doc and self.output_docstrings:
            self.print_indent_msg(test_case.doc, level+1, test_case.success)

        # Print error if it exists
        if test_case.error:
            msg = 'Exception thrown: {0}'.format(test_case.error)
            self.print_passfail_msg(msg, level+1, False)

        # Print expects
        for expect in test_case.expects:
            expect_msg = u'\u2022 {0}'.format(expect)
            self.print_passfail_msg(expect_msg, level+1,
                                    success=expect.success)

        # Add test to totals
        self.test_total += 1
        if test_case.success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        self.test_expects += len(test_case.expects)

    def start_describe(self, evt):
        level = self.get_item_level(evt.payload)
        name = evt.payload.name
        if level > 0:
            name = u'\u221F {0}'.format(name)
        self.print_indent_msg(name, level, color=ConsoleColors.GREEN)
        if evt.payload.doc and self.output_docstrings:
            self.print_indent_msg(evt.payload.doc, level+1)

    def print_summary(self):
        msg = """------- Summary --------
Passed       | {passed}
Failed       | {failed}
Expectations | {expects}
Test Total   | {total}
""".format(
            total=self.test_total, passed=self.passed_tests,
            failed=self.failed_tests, expects=self.test_expects)

        success = self.failed_tests == 0

        self.print_colored('\n')
        self.print_passfail_msg('-'*24, 0, success)
        self.print_passfail_msg(msg, 0, success)
        self.print_passfail_msg('-'*24, 0, success)
