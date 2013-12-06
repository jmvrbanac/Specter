from unittest import TestCase

from specter.runner import SpecterRunner


class TestSpecterRunner(TestCase):

    def setUp(self):
        self.runner = SpecterRunner()

    def test_ascii_art_generation(self):
        """ We just want to know if it creates something"""
        art = self.runner.generate_ascii_art()

        self.assertGreater(len(art), 0)

    def test_run(self):
        self.runner.run(args=['--search', './tests/example_data', '--no-art'])
        reporter = self.runner.reporter_manager.reporters[0]
        self.assertEqual(len(self.runner.suite_types), 4)
        self.assertEqual(reporter.skipped_tests, 1)
        self.assertEqual(reporter.test_total, 11)

    def test_run_w_coverage(self):
        self.runner.run(args=['--search', './tests/example_data', '--no-art',
                              '--coverage'])
        reporter = self.runner.reporter_manager.reporters[0]
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
        reporter = self.runner.reporter_manager.reporters[0]
        self.assertEqual(len(self.runner.suite_types), 1)
        self.assertEqual(reporter.skipped_tests, 0)
        self.assertEqual(reporter.test_total, 2)

    def test_run_w_select_by_metadata(self):
        self.runner.run(args=['--search', './tests/example_data', '--no-art',
                              '--select-by-metadata', 'test="smoke"'])
        reporter = self.runner.reporter_manager.reporters[0]
        self.assertEqual(len(self.runner.suite_types), 4)
        self.assertEqual(reporter.test_total, 1)
