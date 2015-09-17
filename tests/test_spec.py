try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase
from time import sleep

from specter.spec import (TimedObject, CaseWrapper, Spec, Describe,
                          copy_function, get_function_kwargs,
                          convert_to_hashable)


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

    def bad_handler(self, context):
        print(self.object_that_doesnt_exist)

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

    def test_raised_exception(self):
        self.wrapper = CaseWrapper(case_func=self.bad_handler, parent=None)
        self.wrapper.execute()

        self.assertIsNotNone(self.wrapper.error)
        self.assertIs(type(self.wrapper.error), list)

    def test_name_property(self):
        self.assertEqual(self.wrapper.name, 'example_handler')

    def test_pretty_name_property(self):
        self.assertEqual(self.wrapper.pretty_name, 'example handler')

    def test_doc_property(self):
        self.assertEqual(self.wrapper.doc, 'Test Doc String')

    def test_good_success(self):
        # Create a generic object we can use to test with
        obj = type('inline', (object,), {'success': True})
        self.wrapper.start()
        self.wrapper.expects.append(obj)
        self.wrapper.stop()

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
        self.assertEqual(self.spec.name, 'Example Spec')

    def test_doc_property(self):
        self.assertEqual(self.spec.doc, 'Example Doc String')

    def test_success_property(self):
        self.assertFalse(self.spec.success)

    def test_execute_with_hooks(self):
        hook1_calls = []
        spec = ExampleSpec()
        spec._hook1 = lambda s: hook1_calls.append(s)

        spec.standard_execution()
        self.assertEqual(len(hook1_calls), 0)
        self.assertTrue(spec.complete)

        spec = ExampleSpec()
        spec._hook1 = lambda s: hook1_calls.append(s)
        spec.hooks = ('_hook1',)
        spec.standard_execution()

        self.assertEqual(len(hook1_calls), 1)
        self.assertTrue(spec.complete)


class TestSpecHelpers(TestCase):

    def test_copy_function(self):
        def sample_func(arg, argv):
            pass

        new_func = copy_function(sample_func, 'new_func_name')
        self.assertEqual(new_func.__name__, 'new_func_name')
        self.assertNotEqual(sample_func, new_func)

    def test_get_function_args_with_an_optional_arg(self):
        def test_func(arg, argv=None):
            pass

        args = {'arg': 'temp'}
        kwargs = get_function_kwargs(test_func, args)
        self.assertEqual(kwargs.get('arg'), 'temp')
        self.assertIsNone(kwargs.get('argv'))


class TestConvertToHashable(TestCase):

    def test_dict(self):
        hash(convert_to_hashable({}))

    def test_list(self):
        hash(convert_to_hashable([]))

    def test_list_of_dicts(self):
        hash(convert_to_hashable([{}, {}, {}]))

    def test_dict_with_list_values(self):
        hash(convert_to_hashable({'a': [], 'b': []}))

    def test_dict_with_list_of_dict_values(self):
        hash(convert_to_hashable({'a': [{}, {}], 'b': [{}, {}]}))
