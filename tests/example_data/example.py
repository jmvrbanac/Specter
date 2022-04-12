from spektrum import Spec, DataSpec
from spektrum import expect, require, skip_if, incomplete, metadata, fixture


def expects_from_a_called_func():
    expect('this should work').not_to.be_none()


class TestObj(object):
    def __str__(self):
        return '<object>\nbam\ntest'


class ExampleSpec(Spec):
    """Basic File to test scanner and runner"""
    def before_all(self):
        self.thing = 'blarg'

    def _my_failed_method(self):
        require('bam').to.equal('trace')

    def this_is_a_test(self):
        """My example doc"""
        require('bam').to.equal('bam')
        expect('bam').to.equal('bam')

    def verify_we_can_handle_a_raise(self):
        def test_raise(things):
            raise Exception(things)

        expect(test_raise, ['things']).to.raise_a(Exception)
        expect(test_raise, things='things').to.raise_a(Exception)

    @skip_if(True, 'Not needed')
    def a_skipped_test(self):
        expect('trace').not_to.equal('boom')

    @incomplete
    def an_incomplete_test(self):
        expect('this should never be called').to.equal(None)

    @metadata(test='smoke')
    def a_test_with_metadata(self):
        expect(True).to.be_true()

    def causing_a_traceback(self):
        expect(Nope).to.be_none()  # NOQA

    def causes_multi_line_error(self):
        expect(TestObj()).to.be_none()

    def shows_called_func_expects(self):
        expects_from_a_called_func()
        self._my_failed_method()

    def multi_line_expect(self):
        expect((
            'this '
            'is a test'
        )).to.equal('this is a test')

    class ExampleDataDescribe(DataSpec):
        DATASET = {
            'test': {'sample': [1]},
            'test2': {'args': {'sample': [2]}, 'meta': {'test': 'sample'}}
        }

        def sample_data(self, sample):
            expect(sample).to.equal([1])

    class BeforeAllError(Spec):
        async def before_all(self):
            raise Exception('bam')

        async def blarg(self):
            pass

    class AfterAllError(Spec):
        async def after_all(self):
            raise Exception('bam')

        async def blarg(self):
            pass

    class BeforeEachError(Spec):
        async def before_each(self):
            raise Exception('bam')

        async def blarg(self):
            pass

    class AfterEachError(Spec):
        async def after_each(self):
            raise Exception('bam')

        async def blarg(self):
            pass


@fixture
class ExampleFixture(Spec):
    def this_should_work(self):
        pass


class ExampleSpecUsingAFixture(ExampleFixture):
    def this_should_work_too(self):
        pass
