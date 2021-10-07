import asyncio
import itertools
import time

from pike.manager import PikeManager

from specter import logger, utils

from specter.exceptions import FailedRequireException
from specter.spec import get_case_data, Spec, spec_filter, find_children, TestCaseData
from specter.reporting.core import ReportManager
from specter.reporting.pretty import PrettyRenderer
from specter.reporting.xunit import XUnitRenderer

logger.setup()
log = logger.get(__name__)


class SpecterRunner(object):
    def __init__(self, reporting_options=None, concurrency=1):
        self.spec_semaphore = asyncio.Semaphore(concurrency)
        self.test_semaphore = asyncio.Semaphore(concurrency)
        self.reporting = ReportManager(reporting_options)
        self.renderer = PrettyRenderer(reporting_options)
        self.xunit_renderer = XUnitRenderer(reporting_options)

    def run(self, search_paths, module_name=None, metadata=None, test_names=None, exclude=None):
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

            # TODO(jmvrbanac): Change how nested specs are executed
            # coroutines = []
            # for cls in selected_modules:
            #     exc_func = execute_spec
            #     spec = cls()

            #     if spec.__parent_cls__:
            #         exc_func = execute_nested_spec

            #     coroutines.append(
            #         exc_func(spec, self.semaphore, self.reporting, metadata, test_names)
            #     )

            # future = asyncio.gather(*coroutines)

            future = asyncio.gather(*[
                execute_spec(cls(), self.spec_semaphore, self.test_semaphore, self.reporting, metadata, test_names, exclude)
                for cls in selected_modules
            ])

            loop.run_until_complete(future)
            print('\n', flush=True)

            report = self.reporting.build_report()
            self.renderer.render(report)

            if self.xunit_renderer.filename:
                self.xunit_renderer.render(report)

        return self.reporting.success

    def filter_by_module_name(self, classes, name):
        found = [
            cls
            for cls in classes
            if name in '{}.{}'.format(cls.__module__, cls.__name__)
        ]

        # Only search children if the class cannot be found at the package lvl
        if not found:
            children = [find_children(cls) for cls in classes]
            found = [
                cls
                for cls in itertools.chain.from_iterable(children)
                if name in '{}.{}'.format(cls.__module__, cls.__name__)
            ]

        return found


async def execute_nested_spec(spec, semaphore, reporting, metadata=None, test_names=None,
                              exclude=None):
    parents = []
    cls = spec.__parent_cls__
    last = None

    while cls:
        parent = cls(parent=last)
        last = parent

        parents.append(parent)
        cls = parent.__parent_cls__

    # Walk up the tree to setup specs
    parents.reverse()
    last = None
    for parent in parents:
        successful = await setup_spec(parent, semaphore, reporting)
        if successful is False:
            reporting.case_finished(spec, TestCaseData())
            return
        last = parent

    # Execute the nested spec
    spec.parent = last
    await execute_spec(
        spec,
        semaphore,
        reporting,
        metadata=metadata,
        test_names=test_names,
        exclude=exclude
    )

    # Walk down the tree to setup specs
    parents.reverse()
    for parent in parents:
        successful = await teardown_spec(parent, semaphore)
        if successful is False:
            reporting.case_finished(spec, TestCaseData())
            return


async def execute_spec(spec, spec_semaphore, test_semaphore, reporting,
                       metadata=None, test_names=None, exclude=None):
    if spec.__CASE_CONCURRENCY__:
        test_semaphore = spec.__CASE_CONCURRENCY__
    if spec.__SPEC_CONCURRENCY__:
        spec_semaphore = spec.__SPEC_CONCURRENCY__

    if not spec.parent:
        filter_cases_by_data(spec, metadata, test_names, exclude)

    # Limit spec setups to max concurrency level
    async with spec_semaphore:
        successful = await setup_spec(spec, test_semaphore, reporting)
        if successful is False:
            reporting.case_finished(spec, TestCaseData())
            return

        test_futures = [
            execute_test_case(spec, func, test_semaphore, reporting)
            for func in spec.__test_cases__
        ]
        await asyncio.gather(*test_futures)

    spec_futures = [
        execute_spec(
            child,
            spec_semaphore,
            test_semaphore,
            reporting,
            metadata,
            test_names,
            exclude
        )
        for child in spec.children
    ]
    await asyncio.gather(*spec_futures)

    async with spec_semaphore:
        successful = await teardown_spec(spec, test_semaphore)
        if successful is False:
            reporting.case_finished(spec, TestCaseData())


async def setup_spec(spec, semaphore, reporting):
    reporting.track_spec(spec)
    if spec.has_dependencies:
        return await execute_method(spec.before_all, semaphore)


async def teardown_spec(spec, semaphore):
    if spec.has_dependencies:
        return await execute_method(spec.after_all, semaphore)


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

            return False

    return True


async def execute_test_case(spec, case, semaphore, reporting, *args, **kwargs):
    data = get_case_data(case)
    if data.incomplete:
        reporting.case_finished(spec, case)
        return

    # If we're executing a data-driven case we need to override the kwargs
    if data.type == 'data-driven':
        kwargs = data.data_kwargs

    if not (data.skip or data.incomplete):
        successful = await execute_method(spec.before_each, semaphore)
        if successful is False:
            data.before_each_traces.extend(spec.before_each.__tracebacks__)
            reporting.case_finished(spec, case)
            return

    data.start_time = time.time()
    await execute_method(getattr(spec, case.__name__), semaphore, *args, **kwargs)
    data.end_time = time.time()

    if not (data.skip or data.incomplete):
        successful = await execute_method(spec.after_each, semaphore)
        if successful is False:
            data.after_each_traces.extend(spec.after_each.__tracebacks__)

    reporting.case_finished(spec, case)


def filter_cases_by_data(spec, metadata, test_names, exclude):
    # I Don't really like messing with the test list after the fact.
    # This should really get fixed at somepoint

    if test_names:
        spec.__test_cases__ = utils.find_by_names(
            test_names, spec.__test_cases__)
    if metadata:
        spec.__test_cases__ = utils.find_by_metadata(
            metadata, spec.__test_cases__)
    if exclude:
        spec.__test_cases__ = utils.exclude_by_metadata(
            exclude, spec.__test_cases__)

    for child in spec.children:
        filter_cases_by_data(child, metadata, test_names, exclude)
