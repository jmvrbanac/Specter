from random import shuffle
from argparse import ArgumentParser
from specter import _
from specter.scanner import SuiteScanner
from specter.reporting import ConsoleReporter


class SpecterRunner(object):
    DESCRIPTION = _('Specter is a spec-based testing library to help '
                    'facilitate BDD in Python.')

    def __init__(self):
        super(SpecterRunner, self).__init__()
        self.suite_scanner = SuiteScanner()
        self.collector = ConsoleReporter()
        self.arg_parser = ArgumentParser(description=self.DESCRIPTION)
        self.setup_argparse()

    def setup_argparse(self):
        self.arg_parser.add_argument('--search', type=str, dest='search',
                                     help=_('The spec suite search path.'))
        self.arg_parser.add_argument('--no-art',
                                     dest='no_art', action='store_true',
                                     help=_('Disables ASCII art'))

    def ascii_art(self):
        tag_line = _('Keeping the boogy man away from your code!')
        ascii_art = """
          ___
        _/ @@\\
    ~- ( \\  O/__     Specter
    ~-  \\    \\__)   ~~~~~~~~~~
    ~-  /     \\     {tag}
    ~- /      _\\
       ~~~~~~~~~
    """.format(tag=tag_line)
        print ascii_art

    def run(self):
        self.arguments = self.arg_parser.parse_args()

        if not self.arguments.no_art:
            self.ascii_art()

        self.suite_types = self.suite_scanner.scan(self.arguments.search)
        shuffle(self.suite_types)

        for suite_type in self.suite_types:
            suite = suite_type()
            self.collector.add_describe(suite)
            suite.execute()

        self.collector.print_summary()


def activate():
    runner = SpecterRunner()
    runner.run()
