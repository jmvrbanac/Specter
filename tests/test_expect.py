import ast
import inspect
import types
from unittest import TestCase

from specter.util import ExpectParams
from specter.expect import (ExpectAssert, RequireAssert, TestSkippedException,
                            FailedRequireException)


class TestExpectAssertion(TestCase):

    def _create_assert(self, target, caller_args=[]):
        return ExpectAssert(target, caller_args=caller_args)

    def test_verify_true_condition(self):
        target = 'test'
        expect = self._create_assert(target)
        self.assertTrue(expect._verify_condition(True))

    def test_verify_false_condition(self):
        target = 'test'
        expect = self._create_assert(target)
        try:
            success = expect._verify_condition(False)
        except FailedRequireException as e:
            self.assertIsNotNone(e)
        else:
            self.assertFalse(success)

    def test_creating_a_blank_reference(self):
        target = 'test'
        expect = self._create_assert(target)
        self.assertEqual(expect.target, target)

    def test_expect_equal(self):
        target = 'test'
        expect = self._create_assert(target)
        expect.to.equal(target)
        self.assertTrue(expect.success)

    def test_expect_not_to_equal(self):
        target = 'test'
        expect = self._create_assert(target)
        expect.not_to.equal('nope')
        self.assertTrue(expect.success)

    def test_expect_almost_equal(self):
        target = 0.010000001
        expect = self._create_assert(target)
        expect.to.almost_equal(0.01)
        self.assertTrue(expect.success)

    def test_expect_almost_equal_with_places(self):
        target = 0.011
        expect = self._create_assert(target)
        expect.to.almost_equal(0.01, places=2)
        self.assertTrue(expect.success)

    def test_expect_not_to_almost_equal(self):
        target = 0.01
        expect = self._create_assert(target)
        expect.not_to.almost_equal(0.02)
        self.assertTrue(expect.success)

    def test_expect_almost_equal_places_not_int(self):
        expect = self._create_assert(0.01)
        with self.assertRaises(TypeError):
            expect.to.almost_equal(0.01, places=None)

    def test_expect_greater_than(self):
        target = 100
        expect = self._create_assert(target)
        expect.to.be_greater_than(99)
        self.assertTrue(expect.success)

    def test_expect_not_greater_than(self):
        target = 100
        expect = self._create_assert(target)
        expect.not_to.be_greater_than(100)
        self.assertTrue(expect.success)

    def test_expect_less_than(self):
        target = 99
        expect = self._create_assert(target)
        expect.to.be_less_than(100)
        self.assertTrue(expect.success)

    def test_expect_not_less_than(self):
        target = 99
        expect = self._create_assert(target)
        expect.not_to.be_less_than(99)
        self.assertTrue(expect.success)

    def test_expect_none(self):
        target = None
        expect = self._create_assert(target)
        expect.to.be_none()
        self.assertTrue(expect.success)

    def test_expect_not_none(self):
        target = 'bam'
        expect = self._create_assert(target)
        expect.not_to.be_none()
        self.assertTrue(expect.success)

    def test_expect_contain(self):
        target = 'this is a test'
        expect = self._create_assert(target)
        expect.to.contain('is')
        self.assertTrue(expect.success)

    def test_expect_not_contain(self):
        target = 'this is a test'
        expect = self._create_assert(target)
        expect.not_to.contain('bam')
        self.assertTrue(expect.success)

    def test_expect_be_in(self):
        target = 'is'
        expect = self._create_assert(target)
        expect.to.be_in('this is a test')
        self.assertTrue(expect.success)

    def test_expect_be_in_list(self):
        target = 'is'
        expect = self._create_assert(target)
        expect.to.be_in(['test', 'is', 'bam'])
        self.assertTrue(expect.success)

    def test_expect_not_be_in(self):
        target = 'bam'
        expect = self._create_assert(target)
        expect.not_to.be_in('this is a test')
        self.assertTrue(expect.success)

    def test_expect_be_a_w_str(self):
        target = 'test'
        expect = self._create_assert(target)
        expect.to.be_a(str)
        self.assertTrue(expect.success)

    def test_expect_not_be_a_w_str(self):
        target = 102
        expect = self._create_assert(target)
        expect.not_to.be_a(str)
        self.assertTrue(expect.success)

    def test_expect_be_an_instance_of(self):
        class Bam(object):
            pass

        target = Bam()
        expect = self._create_assert(target)
        expect.to.be_an_instance_of(Bam)
        self.assertTrue(expect.success)

    def test_expect_not_be_an_instance_of(self):
        class Bam(object):
            pass

        class OtherBam(object):
            pass

        target = Bam()
        expect = self._create_assert(target)
        expect.not_to.be_an_instance_of(OtherBam)
        self.assertTrue(expect.success)

    def test_expect_true(self):
        target = True
        expect = self._create_assert(target)
        expect.to.be_true()
        self.assertTrue(expect.success)

    def test_expect_not_true(self):
        target = False
        expect = self._create_assert(target)
        expect.not_to.be_true()
        self.assertTrue(expect.success)

    def test_expect_false(self):
        target = False
        expect = self._create_assert(target)
        expect.to.be_false()
        self.assertTrue(expect.success)

    def test_expect_not_false(self):
        target = True
        expect = self._create_assert(target)
        expect.not_to.be_false()
        self.assertTrue(expect.success)

    def test_multi_line_expect(self):
        from tests.example_data import example
        tree = ast.parse(inspect.getsource(example))

        # Dynamically find the right method
        our_expect = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == 'multi_line_expect':
                    our_expect = node

        params = ExpectParams(our_expect.lineno + 1, example)
        self.assertEqual(params.cmp_arg, "'this is a test'")
        self.assertEqual(params.expect_arg, "'this is a test'")
        self.assertEqual(params.expect_type, 'expect')
        self.assertEqual(params.cmp_type, 'equal')

    def test_expect_raise(self):
        def sample_raise_func():
            raise Exception('bam')

        target = sample_raise_func
        expect = self._create_assert(target)
        expect.to.raise_a(Exception)
        self.assertTrue(expect.success)

    def test_expect_not_raise(self):
        def sample_raise_func():
            raise Exception('bam')

        target = sample_raise_func
        expect = self._create_assert(target)
        expect.not_to.raise_a(Exception)
        self.assertFalse(expect.success)

    def test_expect_should_surface_not_specified_assertion(self):
        class SecondException(Exception):
            pass

        class RandoException(Exception):
            pass

        def sample_raise_func():
            raise RandoException()

        target = sample_raise_func
        expect = self._create_assert(target)
        expect.not_to.raise_a(SecondException)
        self.assertFalse(expect.success)

    def test_expect_should_succeed_with_not_assertion_and_no_raise(self):
        def sample_raise_func():
            pass

        target = sample_raise_func
        expect = self._create_assert(target)
        expect.not_to.raise_a(Exception)
        self.assertTrue(expect.success)


class TestRequireAssertion(TestExpectAssertion):

    def _create_assert(self, target):
        return RequireAssert(target)


class TestExceptions(TestCase):

    def test_create_instance_test_skipped_exception(self):
        inst = TestSkippedException(lambda: None, reason='boom')

        self.assertIsNotNone(inst)
        self.assertIs(type(inst.func), types.FunctionType)
        self.assertEqual(inst.reason, 'boom')
