import types
from unittest import TestCase

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


class TestRequireAssertion(TestExpectAssertion):

    def _create_assert(self, target):
        return RequireAssert(target)


class TestExceptions(TestCase):

    def test_create_instance_test_skipped_exception(self):
        inst = TestSkippedException(lambda: None, reason='boom')

        self.assertIsNotNone(inst)
        self.assertIs(type(inst.func), types.FunctionType)
        self.assertEqual(inst.reason, 'boom')
