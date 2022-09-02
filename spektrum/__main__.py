import argparse
import os
import sys

import coverage

from spektrum.runner import SpektrumRunner
from spektrum.utils import translate_cli_argument

coverage_omit_list = [
    '*/spektrum/*',
    '*/pike/*',
]


def main(argv=None):
    parser = setup_argparse()
    arguments = parser.parse_args(argv)

    concurrency = int(arguments.concurrency)
    search_path = arguments.search
    select_metadata = None
    exclude_metadata = None
    activated_coverage = None

    if not os.path.exists(search_path):
        print(f'Search path "{search_path}" not found...')
        return 1

    if arguments.select_metadata:
        select_metadata = {
            key: translate_cli_argument(value.strip('"\''))
            for key, value in [
                item.split('=')
                for item in arguments.select_metadata
            ]
        }

    if arguments.exclude_metadata:
        exclude_metadata = {
            key: translate_cli_argument(value.strip('"\''))
            for key, value in [
                item.split('=')
                for item in arguments.exclude_metadata
            ]
        }

    runner = SpektrumRunner(
        reporting_options={
            'show_all_expects': arguments.show_all_expects,
            'xunit_results': arguments.xunit_results,
            'tr_endpoint': arguments.tr_endpoint,
            'tr_username': arguments.tr_username,
            'tr_apikey': arguments.tr_apikey,
            'tr_project': arguments.tr_project,
            'tr_suite': arguments.tr_suite,
            'tr_template': arguments.tr_template,
            'tr_run': arguments.tr_run,
        },
        concurrency=concurrency,
    )

    if arguments.coverage:
        activated_coverage = coverage.coverage(omit=coverage_omit_list)
        activated_coverage._warn_no_data = False
        activated_coverage.start()

    success = runner.run(
        search_paths=[search_path],
        module_name=arguments.select_module,
        metadata=select_metadata,
        exclude=exclude_metadata,
        test_names=arguments.select_tests,
        dry_run=arguments.dry_run,
    )

    if activated_coverage:
        activated_coverage.stop()
        activated_coverage.save()

    if not success:
        sys.exit(1)


def setup_argparse():
    parser = argparse.ArgumentParser(
        description='Spektrum is a spec-based testing library to help facilitate BDD in Python.'
    )

    parser.add_argument(
        '-s', '--search',
        type=str,
        dest='search',
        metavar='',
        help='The spec suite folder path.',
        default='spec',
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
        '--coverage',
        dest='coverage',
        action='store_true',
        help='Activates coverage.py integration'
    )

    parser.add_argument(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        help='Executes through suites without setup/teardown and test cases'
    )

    parser.add_argument(
        '--show-all-expects',
        dest='show_all_expects',
        action='store_true',
        help='Displays all expectations for test cases',
    )

    parser.add_argument(
        '--xunit-results',
        dest='xunit_results',
        metavar='',
        default=None,
        help='Saves out xUnit compatible results to a specified file',
    )

    parser.add_argument(
        '--tr-endpoint',
        dest='tr_endpoint',
        metavar='',
        default='https://madqe.testrail.io',
        help='TestRail Endpoint',
    )

    parser.add_argument(
        '--tr-username',
        dest='tr_username',
        metavar='',
        default=None,
        help='TestRail Username',
    )

    parser.add_argument(
        '--tr-apikey',
        dest='tr_apikey',
        metavar='',
        default=None,
        help='TestRail API Key',
    )

    parser.add_argument(
        '--tr-project',
        dest='tr_project',
        metavar='',
        default=1,
        type=int,
        help='TestRail Project ID',
    )

    parser.add_argument(
        '--tr-suite',
        dest='tr_suite',
        metavar='',
        default=4,
        type=int,
        help='TestRail Suite ID',
    )

    parser.add_argument(
        '--tr-template',
        dest='tr_template',
        metavar='',
        default=4,
        type=int,
        help='TestRail Template ID',
    )

    parser.add_argument(
        '--tr-run',
        dest='tr_run',
        metavar='',
        default=None,
        type=int,
        help='TestRail Run ID for updating an existing run',
    )

    parser.add_argument(
        '--exclude-by-metadata',
        dest='exclude_metadata',
        metavar='',
        help=('Excludes tests to run by specifying a list of key=value pairs you wish to exclude'),
        default=[],
        nargs='*'
    )
    return parser


if __name__ == '__main__':
    main()
