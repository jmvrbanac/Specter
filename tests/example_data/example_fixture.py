from specter.spec import Spec, fixture
from specter.expect import expect


@fixture
class ExampleTestFixture(Spec):

    def _random_helper_func(self):
        pass

    def this_is_a_test(self):
        """My example doc"""
        expect('bam').to.equal('bam')


class UsingFixture(ExampleTestFixture):

    def another_test(self):
        pass
