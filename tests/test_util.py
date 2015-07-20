from unittest import TestCase

from specter import util, spec, metadata, skip


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

        test_list = {wrap1.id: wrap1, wrap2.id: wrap2}
        found = util.find_by_metadata({'test': 'smoke'}, test_list)
        self.assertEqual(len(found), 1)
        self.assertIn(wrap1.id, found)

    def test_extract_metadata(self):

        @metadata(type='testing')
        def sample_func():
            pass

        func, meta = util.extract_metadata(sample_func)
        self.assertEqual(func.__name__, 'sample_func')
        self.assertEqual(meta.get('type'), 'testing')

    def test_extract_metadata_w_skip_before(self):

        @skip('testing_skip')
        @metadata(type='testing')
        def sample_func():
            pass

        func, meta = util.extract_metadata(sample_func)
        self.assertEqual(meta.get('type'), 'testing')

    def test_extract_metadata_w_skip_after(self):

        @metadata(type='testing')
        @skip('testing_skip')
        def sample_func():
            pass

        func, meta = util.extract_metadata(sample_func)
        self.assertEqual(meta.get('type'), 'testing')

    def test_get_real_last_traceback_w_exception_in_old_style_class(self):
        class OldStyleClass:
            def throw(self):
                raise Exception('exception in OldStyleClass')

        try:
            OldStyleClass().throw()
        except Exception as e:
            util.get_real_last_traceback(e)
