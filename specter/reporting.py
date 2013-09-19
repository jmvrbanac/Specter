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
    INDENT = 2

    def __init__(self):
        super(ConsoleReporter, self).__init__()
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.assertions = 0

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
        self.print_indent_msg(test_case.doc, level+1)

        # Print expects
        for expect in test_case.expects:
            expect_msg = u'\u2022 {0}'.format(expect)
            self.print_passfail_msg(expect_msg, level+1,
                                    success=expect.success)

        # Add test to totals
        self.total += 1
        if test_case.success:
            self.passed += 1
        else:
            self.failed += 1
        self.assertions += len(test_case.expects)

    def start_describe(self, evt):
        level = self.get_item_level(evt.payload)
        name = evt.payload.name
        if level > 0:
            name = u'\u221F {0}'.format(name)
        self.print_indent_msg(name, level, color=ConsoleColors.GREEN)
        if evt.payload.doc:
            self.print_indent_msg(evt.payload.doc, level+1)

    def print_summary(self):
        msg = """-- Summary of tests --
Total        | {total}
Passed       | {passed}
Failed       | {failed}
Expectations | {expects}""".format(
            total=self.total, passed=self.passed,
            failed=self.failed, expects=self.assertions)

        self.print_colored('\n')
        self.print_passfail_msg('-'*24, 0, self.failed == 0)
        self.print_passfail_msg(msg, 0, self.failed == 0)
        self.print_passfail_msg('-'*24, 0, self.failed == 0)
