from unittest import TestCase

from specter import util


class TestSpecterUtil(TestCase):

    def test_get_called_src_line_error(self):
        handled = util.get_called_src_line()
        self.assertIsNone(handled)

    def test_convert_camelcase_error(self):
        result = util.convert_camelcase(None)
        self.assertEqual(result, '')

    def test_get_numbered_source_error(self):
        result = util.get_numbered_source(None, 1)
        self.assertIn('Error finding traceback!', result)
