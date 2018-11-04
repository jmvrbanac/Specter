import sys
import textwrap

import colored

from specter import logger, utils
from specter.spec import get_case_data

log = logger.get(__name__)

UNICODE_SEP = u'\u221F'
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
red = colored.fg('red')
purple = colored.fg('purple_1b')
reset = colored.attr('reset')


def supports_colors():
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


class PrettyReporter(object):
    def __init__(self):
        self.sep = UNICODE_SEP
        self.use_colors = supports_colors()

    def report_art(self):
        tag = 'Keeping the Bogeyman away from your code!'
        ascii_art = textwrap.dedent(f"""
              ___
            _/ @@\\
        ~- ( \\  O/__     Specter
        ~-  \\    \\__)   ~~~~~~~~~
        ~-  /     \\     {tag}
        ~- /      _\\
           ~~~~~~~~~
        """)
        print(ascii_art)

    def report_spec(self, spec, level=0):
        spec_name = utils.camelcase_to_spaces(type(spec).__name__)
        msg = f'{"  " * level}{spec_name}'
        log.info(f'{msg}')

        for case in spec.__test_cases__:
            case_name = case.__name__.replace('_', ' ')
            successful = all(expect.success for expect in spec.__expects__[case])
            data = get_case_data(case)

            color = good
            if not successful:
                color = red
            elif data.incomplete:
                color = purple

            msg = f'{"  " * (level + 1)}{self.sep} {case_name}'
            log.info(f'{color}{msg}{reset}')

            for expect in spec.__expects__[case]:
                color = good if expect.success else red
                msg = f'{"  " * (level + 2)}{self.sep} {str(expect)}'
                log.info(f'{color}{msg}{reset}')

        for child in spec.children:
            self.report_spec(child, level + 1)
