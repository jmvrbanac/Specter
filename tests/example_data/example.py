from specter.spec import Spec
from specter.expect import expect


class ExampleSpec(Spec):
    """Basic File to test scanner and runner"""

    def this_is_a_test(self):
        """My example doc"""
        expect('bam').to.equal('bam')
