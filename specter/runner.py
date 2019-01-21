import asyncio
import time

from specter import logger, utils

from specter.spec import get_case_data
from specter.reporting.core import ReportManager
from specter.reporting.pretty import PrettyReporter
from specter.sample import ExampleSpec

logger.setup()
log = logger.get(__name__)


class SpecterRunner(object):
    def __init__(self):
        self.semaphore = asyncio.Semaphore(10)

    def run(self):
        loop = asyncio.get_event_loop()
        reporting = ReportManager()
        # reporter = PrettyReporter()
        # reporter.report_art()

        spec = ExampleSpec()

        loop.run_until_complete(
            execute_spec(spec, self.semaphore, reporting)
        )
        reporting.output()
        # reporter.track_spec(spec)
        # reporter.report_spec(spec)


async def execute_spec(spec, semaphore, reporting):
        reporting.track_spec(spec)

        test_futures = [
            execute_test_case(spec, func, semaphore, reporting)
            for func in spec.__test_cases__
        ]
        spec_futures = [
            execute_spec(child, semaphore, reporting)
            for child in spec.children
        ]

        await execute_method(spec.before_all, semaphore)
        await asyncio.gather(*test_futures)
        await asyncio.gather(*spec_futures)
        await execute_method(spec.after_all, semaphore)


async def execute_method(method, semaphore, *args, **kwargs):
    # If it has the inherited tag, it's from the base class and don't execute
    if getattr(method, '__inherited_from_spec__', None):
        return

    async with semaphore:
        try:
            log.debug('Executing: %s', method.__func__.__qualname__)
            if asyncio.iscoroutinefunction(method):
                return await method(*args, **kwargs)
            else:
                return method(*args, **kwargs)
        except Exception as exc:
            # Get the tracebacks and attach them to the test case for
            # reporting later.
            tracebacks = utils.get_tracebacks(exc)
            method.__func__.__tracebacks__ = tracebacks


async def execute_test_case(spec, case, semaphore, reporting, *args, **kwargs):
    data = get_case_data(case)
    if data.incomplete:
        return

    await execute_method(spec.before_each, semaphore)

    data.start_time = time.time()
    await execute_method(getattr(spec, case.__name__), semaphore, *args, **kwargs)
    data.end_time = time.time()

    await execute_method(spec.after_each, semaphore)

    reporting.case_finished(spec, case)
