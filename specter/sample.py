import asyncio
import time

from specter.spec import Spec
from specter.expect import expect


class ExampleSpec(Spec):
    def before_all(self):
        self.bam = 'this is a test'

    def things(self):
        # comment here
        bam = 'this'
        # more comments
        expect('more').to.equal('this')
        expect(bam).to.equal('this')
        # expect(
        #     rando,
        #     msg='thingy').to.raise_a(Exception)

    async def should_something_async1(self):
        await asyncio.sleep(1)

    async def should_something_async2(self):
        await asyncio.sleep(1)

    async def should_something_async3(self):
        await asyncio.sleep(1)

    async def should_something_async4(self):
        await asyncio.sleep(1)

    def should_do_something_sync(self):
        time.sleep(1)

    class ChildSpec(Spec):
        def more_things(self):
            raise Exception(self.parent.bam)

        async def even_more_things(self):
            await asyncio.sleep(2)

        class ChildChildSpec(Spec):
            def more_things(self):
                print(self.parent.parent.bam)

    class SecondChildSpec(Spec):
        def second_more_things(self):
            pass

        async def second_even_more_things(self):
            await asyncio.sleep(1)
