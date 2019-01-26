import asyncio
import time

from pike.manager import PikeManager

from specter import logger, utils

from specter.spec import get_case_data, Spec
from specter.reporting.core import ReportManager
from specter.reporting.pretty import PrettyReporter

logger.setup()
log = logger.get(__name__)


class SpecterRunner(object):
    def __init__(self):
        self.semaphore = asyncio.Semaphore(2)

    def run(self, search_paths):
        loop = asyncio.get_event_loop()
        reporting = ReportManager()
        # reporter = PrettyReporter()
        # reporter.report_art()

        with PikeManager(search_paths) as mgr:
            future = asyncio.gather(*[
                execute_spec(cls(), self.semaphore, reporting)
                for cls in mgr.get_all_inherited_classes(Spec)
            ])

            loop.run_until_complete(future)
            reporting.report_specter_format()


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
                ret = await method(*args, **kwargs)
            else:
                ret = method(*args, **kwargs)

            log.debug('Finished: %s', method.__func__.__qualname__)
            return ret

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
