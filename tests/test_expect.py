from unittest import TestCase

from specter.expect import ExpectAssert, RequireAssert


class TestExpectAssertion(TestCase):

    def _create_assert(self, target):
        return ExpectAssert(target)

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


class TestRequireAssertion(TestExpectAssertion):

    def _create_assert(self, target):
        return RequireAssert(target)
