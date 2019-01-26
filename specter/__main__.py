"""
Specter Test Runner

Usage:
  specter [options]

Options:
  -h --help              Show this screen.
  -s --search=<search>   Search path for specifications [default: ./spec]
"""
import os

from docopt import docopt

from specter.runner import SpecterRunner


def main(argv=None):
    arguments = docopt(__doc__, argv=argv)

    search_path = arguments['--search']
    if not os.path.exists(search_path):
        print(f'Search path "{search_path}" not found...')
        return 1

    runner = SpecterRunner()
    runner.run([search_path])
