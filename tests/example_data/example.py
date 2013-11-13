from specter.spec import Spec, DataDescribe
from specter.expect import expect, require, skip_if, incomplete


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

    def causing_a_traceback(self):
        expect(Nope).to.be_none()  # NOQA

    class ExampleDataDescribe(DataDescribe):
        DATASET = {
            'test': {'arg': [1]},
            'test2': {'arg': [1]}
        }

        def sample_data(self, arg):
            expect(arg).to.equal([1])


class ExampleFixture(Spec):
    pass


class ExampleSpecUsingAFixture(ExampleFixture):
    def this_should_work(self):
        pass
