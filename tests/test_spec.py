try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase
from time import sleep

from specter.spec import TimedObject, CaseWrapper, Spec, Describe


class TestTimedObject(TestCase):

    def test_creation_of_timed_object(self):
        obj = TimedObject()
        self.assertEqual(obj.start_time, 0)
        self.assertEqual(obj.end_time, 0)

    def test_start_stop(self):
        obj = TimedObject()
        obj.start()
        sleep(0.05)
        obj.stop()

        self.assertGreater(obj.start_time, 0)
        self.assertGreater(obj.end_time, 0)

    def test_elapsed_time(self):
        obj = TimedObject()
        obj.start()
        sleep(0.05)
        obj.stop()

        self.assertGreater(obj.elapsed_time, 0.05)


class TestCaseWrapper(TestCase):

    def example_handler(self, context):
        """Test Doc String"""
        self.called = True

    def setUp(self):
        super(TestCaseWrapper, self).setUp()
        self.called = False
        self.wrapper = CaseWrapper(case_func=self.example_handler, parent=None)

    def test_execute(self):
        self.wrapper.execute()
        self.assertTrue(self.called)

    def test_name_property(self):
        self.assertEqual(self.wrapper.name, 'example_handler')

    def test_pretty_name_property(self):
        self.assertEqual(self.wrapper.pretty_name, 'example handler')

    def test_doc_property(self):
        self.assertEqual(self.wrapper.doc, 'Test Doc String')

    def test_good_success(self):
        # Create a generic object we can use to test with
        obj = type('inline', (object,), {'success': True})
        self.wrapper.expects.append(obj)

        self.assertTrue(self.wrapper.success)

    def test_failure(self):
        # Create a generic object we can use to test with
        obj = type('inline', (object,), {'success': False})
        self.wrapper.expects.append(obj)

        self.assertFalse(self.wrapper.success)


# Class Structure Used for testing
class ExampleSpec(Spec):
    """Example Doc String"""
    def example_spec_test_case(self):
        pass

    class ExampleDescribe(Describe):
        def example_describe_test_case(self):
            pass


class TestSpecDescribe(TestCase):

    def setUp(self):
        self.spec = ExampleSpec()

    def test_name_property(self):
        self.assertEqual(self.spec.name, 'ExampleSpec')

    def test_doc_property(self):
        self.assertEqual(self.spec.doc, 'Example Doc String')
