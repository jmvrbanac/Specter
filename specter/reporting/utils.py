import re
import six

from specter import _


class TestStatus():
    PASS = 'passed'
    FAIL = 'failed'
    SKIP = 'skipped'
    INCOMPLETE = 'incomplete'
    ERROR = 'error'


class ConsoleColors():
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


def get_color_from_status(status):
    color = None
    if status == TestStatus.PASS:
        color = ConsoleColors.GREEN
    elif status == TestStatus.SKIP:
        color = ConsoleColors.YELLOW
    elif status == TestStatus.INCOMPLETE:
        color = ConsoleColors.MAGENTA
    elif status is not None:
        color = ConsoleColors.RED

    return color


def print_test_msg(msg, level, status=None, use_color=True):
    color = get_color_from_status(status) if use_color else None
    print_indent_msg(msg=msg, level=level, color=color)


def pretty_print_args(kwargs):
    if kwargs is None:
        return u'None'
    first_seen = False
    parts = []
    for k, v in six.iteritems(kwargs):
        if not first_seen:
            first_seen = True
        else:
            parts.append(', ')
        parts.append('{name} = {value}'.format(name=k, value=v))
    return u''.join(parts)


def print_test_args(kwargs, level, status=TestStatus.PASS, use_color=True):
    if kwargs and (status == TestStatus.ERROR or
                   status == TestStatus.FAIL):
        msg = u''.join([
            u'  Parameters: ',
            pretty_print_args(kwargs)
        ])
        print_test_msg(msg, level, status, use_color)


def print_indent_msg(msg, level=0, color=None):
    indent = u' ' * 2
    msg = u'{0}{1}'.format(str(indent * level), msg)
    print_to_screen(msg=msg, color=color)


def print_msg_list(msg_list, level, color=None):
    for msg in msg_list:
        print_indent_msg(msg=msg, level=level, color=color)


def print_to_screen(msg, color=None):
    if color:
        msg = u'\033[{color}m{msg}\033[0m'.format(color=color, msg=msg)

    # Re-encode msg to result everything to UTF-8
    encoded_bytes = msg.encode('utf-8')
    print(encoded_bytes.decode('utf-8'))


def get_item_level(item):
    levels = 0
    parent_above = item.parent
    while parent_above is not None:
        levels += 1
        parent_above = parent_above.parent
    return levels


def print_expects(test_case, level, use_color=True):
    # Print expects
    for expect in test_case.expects:
        mark = u'\u2718'

        status = TestStatus.FAIL
        if expect.success:
            status = TestStatus.PASS
            mark = u'\u2714'

        # Turn off the status if we're not using color
        if not use_color:
            status = None

        expect_msg = u'{mark} {msg}'.format(mark=mark, msg=expect)

        print_test_msg(expect_msg, level + 1, status=status)

        def hardcoded(param):
            result = re.match('^(\'|"|\d)', str(param)) is not None
            return result

        def print_param(value, param, indent, prefix):
            if not expect.success and not hardcoded(param):
                msg_list = str(value).splitlines() or ['']
                prefix = _('{0}: {1}').format(param or prefix, msg_list[0])
                print_indent_msg(prefix, indent)
                if len(msg_list) > 1:
                    print_msg_list(msg_list[1:], indent)

        if expect.custom_msg:
            print_test_msg(expect.custom_msg, level + 3, status=status)

        # Print the target parameter
        try:
            print_param(expect.target, expect.target_src_param,
                        level + 3, 'Target')
        except:
            print_param('ERROR - Couldn\'t evaluate target value',
                        expect.target_src_param, level + 3, 'Target')

        # Print the expected parameter
        try:
            print_param(expect.expected, expect.expected_src_param,
                        level + 3, 'Expected')
        except:
            print_param('ERROR - Couldn\'t evaluate expected value',
                        expect.expected_src_param, level + 3, 'Expected')
