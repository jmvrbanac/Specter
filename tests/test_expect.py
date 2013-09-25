from unittest import TestCase

from specter.expect import ExpectAssert, RequireAssert


class TestExpectAssertion(TestCase):

    def test_creating_a_blank_reference(self):
        target = 'test'
        expect = ExpectAssert(target)
        self.assertEqual(expect.target, target)

    def test_expect_equal(self):
        target = 'test'
        expect = ExpectAssert(target)
        expect.to.equal(target)
        self.assertTrue(expect.success)

    def test_expect_not_to_equal(self):
        target = 'test'
        expect = ExpectAssert(target)
        expect.not_to.equal('nope')
        self.assertTrue(expect.success)

    def test_expect_greater_than(self):
        target = 100
        expect = ExpectAssert(target)
        expect.to.be_greater_than(99)
        self.assertTrue(expect.success)

    def test_expect_not_greater_than(self):
        target = 100
        expect = ExpectAssert(target)
        expect.not_to.be_greater_than(100)
        self.assertTrue(expect.success)

    def test_expect_less_than(self):
        target = 99
        expect = ExpectAssert(target)
        expect.to.be_less_than(100)
        self.assertTrue(expect.success)

    def test_expect_not_less_than(self):
        target = 99
        expect = ExpectAssert(target)
        expect.not_to.be_less_than(99)
        self.assertTrue(expect.success)


class TestExpectAssertion(TestCase):

    def test_creating_a_blank_reference(self):
        target = 'test'
        expect = RequireAssert(target)
        self.assertEqual(expect.target, target)

    def test_expect_equal(self):
        target = 'test'
        expect = RequireAssert(target)
        expect.to.equal(target)
        self.assertTrue(expect.success)