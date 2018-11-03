import textwrap

from specter import logger, utils

log = logger.get(__name__)

UNICODE_SEP = u'\u221F'
ASCII_SEP = '-'


class PrettyReporter(object):
    def __init__(self):
        self.sep = UNICODE_SEP
        pass

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
        log.info(ascii_art)

    def report_spec(self, spec, level=0):
        spec_name = utils.camelcase_to_spaces(type(spec).__name__)
        log.info(f'{"  " * level}{spec_name}')

        for case in spec.__test_cases__:
            case_name = case.__name__.replace('_', ' ')
            log.info(f'{"  " * (level + 1)}{self.sep} {case_name}')

        for child in spec.children:
            self.report_spec(child, level + 1)
