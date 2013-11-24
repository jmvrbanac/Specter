from unittest import TestCase

from specter import util, spec


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

    def test_find_by_metadata(self):
        wrap1 = spec.CaseWrapper(None, None, metadata={'test': 'smoke'})
        wrap2 = spec.CaseWrapper(None, None, metadata={'test': 'bam'})

        test_list = [wrap1, wrap2]
        found = util.find_by_metadata({'test': 'smoke'}, test_list)
        self.assertEqual(len(found), 1)
        self.assertIn(wrap1, found)
