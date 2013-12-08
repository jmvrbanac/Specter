from specter.spec import Spec, DataDescribe
from specter.expect import expect, require, skip_if, incomplete, metadata


class TestObj(object):
    def __str__(self):
        return '<object>\nbam\ntest'


class ExampleSpec(Spec):
    """Basic File to test scanner and runner"""

    def this_is_a_test(self):
        """My example doc"""
        require('bam').to.equal('bam')
        expect('bam').to.equal('bam')

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

    class ExampleDataDescribe(DataDescribe):
        DATASET = {
            'test': {'sample': [1]},
            'test2': {'args': {'sample': [2]}, 'meta': {'test': 'sample'}}
        }

        def sample_data(self, sample):
            expect(sample).to.equal([1])


class ExampleFixture(Spec):
    pass


class ExampleSpecUsingAFixture(ExampleFixture):
    def this_should_work(self):
        pass
