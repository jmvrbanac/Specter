from unittest import TestCase
from nose.plugins.capture import Capture

from specter.runner import SpecterRunner
from specter.reporting.console import ConsoleReporter


class TestSpecterRunner(TestCase):

    def setUp(self):
        self.runner = SpecterRunner()
        self.console = Capture()
        self.console.begin()

    def tearDown(self):
        self.console.end()

    def get_console_reporter(self, reporters):
        for r in reporters:
            if type(r) is ConsoleReporter:
                return r

    def test_ascii_art_generation(self):
        """ We just want to know if it creates something"""
        art = self.runner.generate_ascii_art()
        self.assertGreater(len(art), 0)

    def test_run(self):
        self.runner.run(args=['--search', './tests/example_data', '--no-art'])
        reporter = self.get_console_reporter(
            self.runner.reporter_manager.reporters)

        self.assertEqual(len(self.runner.suite_types), 4)
        self.assertEqual(reporter.skipped_tests, 1)
        self.assertEqual(reporter.test_total, 11)

    def test_run_w_coverage(self):
        self.runner.run(args=['--search', './tests/example_data', '--no-art',
                              '--coverage'])
        reporter = self.get_console_reporter(
            self.runner.reporter_manager.reporters)

        self.assertEqual(len(self.runner.suite_types), 4)
        self.assertEqual(reporter.skipped_tests, 1)
        self.assertEqual(reporter.test_total, 11)

    def test_run_w_bad_path(self):
        self.runner.run(args=['--search', './cobble'])
        self.assertEqual(len(self.runner.suite_types), 0)

    def test_run_w_select_module(self):
        self.runner.run(args=['--search', './tests/example_data', '--no-art',
                              '--select-module',
                              'example.ExampleDataDescribe'])
        reporter = self.get_console_reporter(
            self.runner.reporter_manager.reporters)

        self.assertEqual(len(self.runner.suite_types), 1)
        self.assertEqual(reporter.skipped_tests, 0)
        self.assertEqual(reporter.test_total, 2)

    def test_run_w_select_by_metadata(self):
        self.runner.run(args=['--search', './tests/example_data', '--no-art',
                              '--select-by-metadata', 'test="smoke"'])
        reporter = self.get_console_reporter(
            self.runner.reporter_manager.reporters)

        self.assertEqual(len(self.runner.suite_types), 4)
        self.assertEqual(reporter.test_total, 1)

    def test_run_w_xunit(self):
        self.runner.run(args=['--search', './tests/example_data', '--no-art',
                              '--xunit-result', './sample_xunit.xml'])
        self.assertEqual(len(self.runner.reporter_manager.reporters), 4)

    def test_run_w_json(self):
        self.runner.run(args=['--search', './tests/example_data', '--no-art',
                              '--json-result', './sample.json'])
        self.assertEqual(len(self.runner.reporter_manager.reporters), 4)

    def test_run_w_parallel(self):
        self.runner.run(args=['--search', './tests/example_data', '--no-art',
                              '--parallel'])
        self.assertEqual(len(self.runner.suite_types), 4)
