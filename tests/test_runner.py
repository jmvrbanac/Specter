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
        self.assertEqual(len(self.runner.suite_types), 1)
        self.assertEqual(self.runner.collector.skipped_tests, 1)
        self.assertEqual(self.runner.collector.test_total, 4)
