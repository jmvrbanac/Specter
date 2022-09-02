from spektrum import Spec, fixture
from spektrum import expect


@fixture
class ExampleTestFixture(Spec):

    def _random_helper_func(self):
        pass

    def this_is_a_test(self):
        """My example doc"""
        expect('bam').to.equal('bam')


class UsingFixture(ExampleTestFixture):

    def another_test(self):
        """
        Blarg

        --------
        description: |
            adsasda
            asdasd
            Something else
        derp: true
        """
        expect('derp').to.equal('derp')
