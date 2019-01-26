"""
Specter Test Runner

Usage:
  specter [options]

Options:
  -h --help                   Show this screen.
  -s --search=<search>        Search path for specifications [default: ./spec]
  -c --concurrency=<ct>       The base concurrency level [default: 1]
"""
import os

from docopt import docopt

from specter.runner import SpecterRunner


def main(argv=None):
    arguments = docopt(__doc__, argv=argv)
    concurrency = int(arguments['--concurrency'])
    search_path = arguments['--search']

    if not os.path.exists(search_path):
        print(f'Search path "{search_path}" not found...')
        return 1

    runner = SpecterRunner(concurrency)
    runner.run([search_path])
