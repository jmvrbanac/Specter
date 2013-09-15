from specter.spec import TestEvent, DescribeEvent


class ConsoleReporter(object):
    INDENT = 2

    def __init__(self):
        super(ConsoleReporter, self).__init__()

    def add_describe(self, describe):
        describe.add_listener(TestEvent.COMPLETE, self.event_received)
        describe.add_listener(DescribeEvent.START, self.start_describe)

    def print_msg(self, msg, level=0, success=True):
        indent = u' ' * self.INDENT
        msg = u'{0}{1}'.format(str(indent * level), msg)
        if success:
            print u'\033[92m{0}\033[0m'.format(msg)
        else:
            print u'\033[91m{0} | FAILED \033[0m'.format(msg)

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
        self.print_msg(name, level, test_case.success)

        # Print expects
        for expect in test_case.expects:
            expect_msg = u'\u2022 {0}'.format(expect)
            self.print_msg(expect_msg, level+1, success=expect.success)

    def start_describe(self, evt):
        level = self.get_item_level(evt.payload)
        name = evt.payload.name
        if level > 0:
            name = u'\u221F {0}'.format(name)
        self.print_msg(name, level)
