import sys

import colored

from spektrum import logger, utils

log = logger.get(__name__)

UNICODE_SKIP = u'\u2607'
UNICODE_SEP = u'\u221F'
UNICODE_ARROW = u'\u2192'
UNICODE_ARROW_BAR = u'\u219B'
UNICODE_CHECK = u'\u2713'
UNICODE_X = u'\u2717'
ASCII_SEP = '-'


# class ConsoleColors(object):
#     BLACK = 30
#     RED = 31
#     GREEN = 32
#     YELLOW = 33
#     BLUE = 34
#     MAGENTA = 35
#     CYAN = 36
#     WHITE = 37

good = colored.fg('blue')
fail = colored.fg('red')
purple = colored.fg('purple_1b')
yellow = colored.fg('yellow_4a')
reset = colored.attr('reset')


def supports_colors():
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def print_indent(msg, level=0, color=None):
    msg = f'{"  " * level}{msg}'

    if color:
        msg = f'{color}{msg}{reset}'

    print(msg)


def get_spec_color(spec):
    color = good

    if not spec.successful:
        color = fail

    return color


def get_case_color(case):
    color = good

    if case.incomplete:
        color = purple
    elif case.skipped:
        color = yellow
    elif case.successful is False:
        color = fail

    return color


def get_expect_color(expect):
    color = good

    if not expect.success:
        color = fail

    return color


class PrettyRenderer(object):
    def __init__(self, reporting_options=None):
        self.total = 0
        self.passed = 0
        self.skipped = 0
        self.failed = 0
        self.errored = 0
        self.incomplete = 0
        self.expectations = 0
        self.reporting_options = reporting_options or {}

    def count_case(self, case):
        self.total += 1
        self.expectations += len(case.expects)

        if case.errors:
            self.errored += 1

        elif case.successful is False:
            self.failed += 1

        elif case.skipped and not case.incomplete:
            self.skipped += 1

        elif case.incomplete:
            self.incomplete += 1

        elif case.successful:
            self.passed += 1

    def render_spec(self, spec, level=0):
        if not has_tests_at_any_level(spec):
            return

        print_indent(spec.name, level, color=get_spec_color(spec))

        for case in spec.cases:
            self.count_case(case)
            errors = case.errors
            mark = UNICODE_CHECK
            skip_reason = case.skip_reason or ''

            if not case.successful:
                mark = UNICODE_X
            elif case.skipped:
                mark = UNICODE_SKIP
            elif case.incomplete:
                mark = UNICODE_SKIP

            if skip_reason:
                skip_reason = f' - skipped: {skip_reason}'

            print_indent(
                f'{UNICODE_SEP} {mark} {case.name}{skip_reason}',
                level + 1,
                color=get_case_color(case)
            )

            if self.reporting_options.get('show_all_expects'):
                for expect in case.expects:
                    mark = UNICODE_CHECK if expect.success else UNICODE_X
                    arrow = UNICODE_ARROW_BAR if expect.required else UNICODE_ARROW

                    print_indent(
                        f'{arrow} {mark} {expect.evaluation}',
                        level + 2,
                        color=get_expect_color(expect)
                    )
                    if not expect.success:
                        print_indent('Values:', level + 3, color=get_expect_color(expect))
                        print_indent('-------', level + 3, color=get_expect_color(expect))
                        print_indent(
                            f'| {expect.target_name}: {expect.target}',
                            level + 3,
                            color=get_expect_color(expect)
                        )

                        if str(expect.expected_name) != str(expect.expected):
                            print_indent(
                                f'| {expect.expected_name}: {expect.expected}',
                                level + 3,
                                color=get_expect_color(expect)
                            )

            if errors:
                print_errors(errors, level, case.error_type)

        for child_spec in spec.specs:
            self.render_spec(child_spec, level + 1)

    def render(self, report):
        for spec in report:
            self.render_spec(spec)

        print('------------------------')
        print('------- Summary --------')
        print(f'Pass            | {self.passed}')
        print(f'Skip            | {self.skipped}')
        print(f'Fail            | {self.failed}')
        print(f'Error           | {self.errored}')
        print(f'Incomplete      | {self.incomplete}')
        print(f'Test Total      | {self.total}')
        print(f' - Expectations | {self.expectations}')
        print('------------------------')


def has_tests_at_any_level(spec):
    if len(spec.cases) > 0:
        return True

    return any([has_tests_at_any_level(child) for child in spec.specs])


def print_errors(errors, level, error_type):
    print_indent('')
    print_indent(
        utils.traceback_occurred_msg(error_type),
        level + 2,
        color=fail
    )
    print_indent(
        '-' * 40,
        level + 2,
        color=fail
    )

    for error in errors:
        for line in error:
            print_indent(
                line,
                level + 2,
                color=fail
            )
