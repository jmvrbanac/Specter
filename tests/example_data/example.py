from specter.spec import Spec
from specter.expect import expect, require, skip_if


class ExampleSpec(Spec):
    """Basic File to test scanner and runner"""

    def this_is_a_test(self):
        """My example doc"""
        require('bam').to.equal('bam')
        expect('bam').to.equal('bam')

    @skip_if(True, 'Not needed')
    def a_skipped_test(self):
        expect('trace').not_to.equal('boom')
