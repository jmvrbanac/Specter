import argparse
import os
import sys

from specter.runner import SpecterRunner


def main(argv=None):
    parser = setup_argparse()
    arguments = parser.parse_args(argv)

    concurrency = int(arguments.concurrency)
    search_path = arguments.search
    select_metadata = None

    if not os.path.exists(search_path):
        print(f'Search path "{search_path}" not found...')
        return 1

    if arguments.select_metadata:
        select_metadata = {
            key: value.strip('"\'')
            for key, value in [
                item.split('=')
                for item in arguments.select_metadata
            ]
        }

    runner = SpecterRunner(
        reporting_options={
            'show_all_expects': arguments.show_all_expects,
        },
        concurrency=concurrency,
    )
    success = runner.run(
        search_paths=[search_path],
        module_name=arguments.select_module,
        metadata=select_metadata,
        test_names=arguments.select_tests,
    )

    if not success:
        sys.exit(1)


def setup_argparse():
    parser = argparse.ArgumentParser(
        description='Specter is a spec-based testing library to help facilitate BDD in Python.'
    )

    parser.add_argument(
        '-s', '--search',
        type=str,
        dest='search',
        metavar='',
        help='The spec suite folder path.',
    )
    parser.add_argument(
        '-p', '--select-module',
        dest='select_module',
        metavar='',
        help='Selects a module path to run. Ex: sample.TestClass',
        default=None,
    )
    parser.add_argument(
        '-t', '--select-tests',
        dest='select_tests',
        metavar='',
        help='Selects tests by name (comma delimited list).',
        type=lambda s: [item.strip() for item in s.split(',')],
        default=None
    )
    parser.add_argument(
        '-m', '--select-by-metadata',
        dest='select_metadata',
        metavar='',
        help=('Selects tests to run by specifying a list of '
              'key=value pairs you wish to run'),
        default=[],
        nargs='*'
    )

    parser.add_argument(
        '-c', '--concurrency',
        dest='concurrency',
        type=int,
        metavar='',
        help='The base concurrency level',
        default=1,
    )

    parser.add_argument(
        '--show-all-expects',
        dest='show_all_expects',
        action='store_true',
        help='Displays all expectations for test cases',
    )
    return parser
