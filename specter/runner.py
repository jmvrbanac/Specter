import asyncio
import time

from specter import logger, utils
from specter.spec import Spec
from specter.expect import expect

logger.setup()
log = logger.get(__name__)


def rando(msg):
    raise Exception(msg)


class ExampleSpec(Spec):
    def before_all(self):
        self.bam = 'this is a test'

    def things(self):
        # comment here
        bam = 'this'
        # more comments
        expect('more').to.equal('this')
        expect(bam).to.equal('this')
        expect(
            rando,
            msg='thingy').to.raise_a(Exception)

    # async def should_something_async(self):
    #     await asyncio.sleep(2)

    # def should_do_something_sync(self):
    #     time.sleep(1)

    # class ChildSpec(Spec):
    #     def more_things(self):
    #         raise Exception(self.parent.bam)

    #     async def even_more_things(self):
    #         await asyncio.sleep(2)

    #     class ChildChildSpec(Spec):
    #         def more_things(self):
    #             print(self.parent.parent.bam)

    # class SecondChildSpec(Spec):
    #     def second_more_things(self):
    #         pass

    #     async def second_even_more_things(self):
    #         await asyncio.sleep(1)


class SpecterRunner(object):
    def __init__(self):
        pass

    def run(self):
        loop = asyncio.get_event_loop()
        spec = ExampleSpec()

        loop.run_until_complete(execute_spec(spec))
        pass


async def execute_spec(spec):
        test_futures = [
            execute_test_case(spec, func)
            for func in spec.__test_cases__
        ]
        spec_futures = [
            execute_spec(child(parent=spec))
            for child in spec.children
        ]

        await execute_method(spec.before_all)
        await asyncio.gather(*spec_futures)
        await asyncio.gather(*test_futures)
        await execute_method(spec.after_all)


async def execute_method(method, *args, **kwargs):
    try:
        if asyncio.iscoroutinefunction(method):
            return await method(*args, **kwargs)
        else:
            return method(*args, **kwargs)
    except Exception as exc:
        # Get the tracebacks and attach them to the test case for reporting later.
        tracebacks = utils.get_tracebacks(exc)
        method.__func__.__tracebacks__ = tracebacks


async def execute_test_case(spec, case, *args, **kwargs):
    await execute_method(spec.before_each)
    await execute_method(getattr(spec, case.__name__), *args, **kwargs)
    await execute_method(spec.after_each)
