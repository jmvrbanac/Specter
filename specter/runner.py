from argparse import ArgumentParser
from specter import _
from specter.scanner import SuiteScanner

class SpecterRunner(object):
    DESCRIPTION = _('Specter is a spec-based testing library to help '
                    'facilitate BDD in Python.')

    def __init__(self):
        super(SpecterRunner, self).__init__()
        self.suite_scanner = SuiteScanner()
        self.arg_parser = ArgumentParser(description=self.DESCRIPTION)
        self.setup_argparse()

    def setup_argparse(self):
        self.arg_parser.add_argument('--search', type=str, dest='search',
                                     help=_('The spec suite search path.'))

    def run(self):
        self.arguments = self.arg_parser.parse_args()
        self.suite_types = self.suite_scanner.scan(self.arguments.search)

        for suite_type in self.suite_types:
            suite = suite_type()
            suite.execute()




def activate():
    tag_line = _('Keeping the boogy man out of your code!')
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

    runner = SpecterRunner()
    runner.run()