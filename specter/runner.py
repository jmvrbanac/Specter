import asyncio
import itertools
import time

from pike.manager import PikeManager

from specter import logger, utils

from specter.exceptions import FailedRequireException
from specter.spec import get_case_data, Spec, spec_filter
from specter.reporting.core import ReportManager
from specter.reporting.pretty import PrettyRenderer

logger.setup()
log = logger.get(__name__)


class SpecterRunner(object):
    def __init__(self, concurrency=1):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.reporting = ReportManager()
        self.renderer = PrettyRenderer()

    def run(self, search_paths, module_name=None, metadata=None, test_names=None):
        loop = asyncio.get_event_loop()

        with PikeManager(search_paths) as mgr:
            selected_modules = [
                cls
                for cls in mgr.get_all_inherited_classes(Spec)
                if spec_filter(Spec, cls)
            ]

            if module_name:
                selected_modules = self.filter_by_module_name(
                    selected_modules,
                    module_name
                )

            future = asyncio.gather(*[
                execute_spec(cls(), self.semaphore, self.reporting, metadata, test_names)
                for cls in selected_modules
            ])

            loop.run_until_complete(future)
            print('\n', flush=True)


            report = self.reporting.build_report()
            self.renderer.render(report)

    def filter_by_module_name(self, classes, name):
        found = [
            cls
            for cls in classes
            if name in '{}.{}'.format(cls.__module__, cls.__name__)
        ]

        # Only search children if the class cannot be found at the package lvl
        if not found:
            children = [cls.__get_all_child_describes__() for cls in classes]
            found = [
                cls
                for cls in itertools.chain.from_iterable(children)
                if name in '{}.{}'.format(cls.__module__, cls.__name__)
            ]

        return found


async def execute_spec(spec, semaphore, reporting, metadata=None, test_names=None):
        reporting.track_spec(spec)

        test_semaphore = semaphore
        spec_semaphore = semaphore

        if spec.__CASE_CONCURRENCY__:
            test_semaphore = spec.__CASE_CONCURRENCY__
        if spec.__SPEC_CONCURRENCY__:
            spec_semaphore = spec.__SPEC_CONCURRENCY__

        # I Don't really like messing with the test list after the fact.
        # This should really get fixed at somepoint
        if test_names:
            spec.__test_cases__ = utils.find_by_names(test_names, spec.__test_cases__)
        if metadata:
            spec.__test_cases__ = utils.find_by_metadata(metadata, spec.__test_cases__)

        test_futures = [
            execute_test_case(spec, func, test_semaphore, reporting)
            for func in spec.__test_cases__
        ]
        spec_futures = [
            execute_spec(child, spec_semaphore, reporting, metadata, test_names)
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

        except FailedRequireException:
            pass

        except Exception as exc:
            # Get the tracebacks and attach them to the test case for
            # reporting later.
            tracebacks = utils.get_tracebacks(exc)
            method.__func__.__tracebacks__ = tracebacks


async def execute_test_case(spec, case, semaphore, reporting, *args, **kwargs):
    data = get_case_data(case)
    if data.incomplete:
        return

    # If we're executing a data-driven case we need to override the kwargs
    if data.type == 'data-driven':
        kwargs = data.data_kwargs

    await execute_method(spec.before_each, semaphore)

    data.start_time = time.time()
    await execute_method(getattr(spec, case.__name__), semaphore, *args, **kwargs)
    data.end_time = time.time()

    await execute_method(spec.after_each, semaphore)

    reporting.case_finished(spec, case)
