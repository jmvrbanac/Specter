"""
Specter Test Runner

Usage:
  specter [options]

Options:
  -h --help              Show this screen.
  -s --search=<search>   Search path for specifications [default: spec]
"""
from docopt import docopt

from specter.runner import SpecterRunner


def main(argv=None):
    arguments = docopt(__doc__, argv=argv)
    runner = SpecterRunner()
    runner.run()
    print(arguments)
    pass
