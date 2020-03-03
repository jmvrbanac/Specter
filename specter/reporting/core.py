from specter import logger, utils
from specter.spec import get_case_data

log = logger.get(__name__)


class ReportManager(object):
    def __init__(self, reporting_options=None):
        self.version = '2.0'
        self.specs = {}
        self.reporting_options = reporting_options or {}
        self.success = True

    @property
    def parent_specs(self):
        return [
            spec
            for spec in self.specs.values()
            if not spec.parent
        ]

    def track_spec(self, spec):
        self.specs[spec._id] = spec

    def case_finished(self, spec, case):
        data = CaseFormatData(spec, case)
        indicator = '.'

        if not data.successful:
            indicator = 'F'
            self.success = False

        elif data.skipped:
            indicator = 'S'

        print(indicator, end='', flush=True)

    def build_report(self):
        return [
            SpecFormatData(spec)
            for spec in self.parent_specs
        ]


class SpecFormatData(object):
    def __init__(self, spec):
        self._spec = spec
        self.cases = [
            CaseFormatData(spec, case)
            for case in spec.__test_cases__
        ]
        self.specs = [
            SpecFormatData(child)
            for child in spec.children
        ]

    @property
    def successful(self):
        return all([case.successful for case in self.cases])

    @property
    def name(self):
        return utils.camelcase_to_spaces(type(self._spec).__name__)

    @property
    def module(self):
        return self._spec.__module__

    @property
    def doc(self):
        return self._spec.__doc__

    @property
    def elapsed_time(self):
        elapsed = 0
        for case in self.cases:
            elapsed += case.elapsed_time
        return elapsed

    @property
    def as_dict(self):
        return {
            'name': self.name,
            'module': self.module,
            'doc': self.doc,
            'successful': self.successful,
            'elapsed_time': self.elapsed_time,
            'cases': [case.as_dict for case in self.cases],
            'specs': [spec.as_dict for spec in self.specs],
        }


class CaseFormatData(object):
    def __init__(self, spec, case):
        self._spec = spec
        self._case = case
        self.expects = [
            ExpectFormatData(expect)
            for expect in self._spec.__expects__[self._case]
        ]

    @property
    def name(self):
        return utils.snakecase_to_spaces(self.raw_name)

    @property
    def raw_name(self):
        return self._case.__name__

    @property
    def class_name(self):
        return utils.pretty_class_name(self._spec)

    @property
    def start(self):
        return get_case_data(self._case).start_time

    @property
    def end(self):
        return get_case_data(self._case).end_time

    @property
    def elapsed_time(self):
        elapsed = self.end - self.start
        return elapsed if elapsed >= 0 else 0

    @property
    def metadata(self):
        return get_case_data(self._case).metadata

    @property
    def incomplete(self):
        return get_case_data(self._case).incomplete

    @property
    def skipped(self):
        return get_case_data(self._case).skipped

    @property
    def skip_reason(self):
        return get_case_data(self._case).skip_reason

    @property
    def before_each_traces(self):
        return get_case_data(self._case).before_each_traces

    @property
    def after_each_traces(self):
        return get_case_data(self._case).after_each_traces

    @property
    def successful(self):
        tracebacks = self.gather_tracebacks
        return (
            not tracebacks and all(expect.success for expect in self.expects)
        )

    @property
    def error_type(self):
        if getattr(self._spec.before_all, '__tracebacks__', []):
            return 'before_all'
        elif self.before_each_traces:
            return 'before_each'
        elif getattr(self._spec.after_all, '__tracebacks__', []):
            return 'after_all'
        elif self.after_each_traces:
            return 'after_each'
        else:
            return 'case'

    @property
    def errors(self):
        tracebacks = self.gather_tracebacks
        formatted_tracebacks = []

        # TODO: Clean this up
        for tb in tracebacks:
            frame = tb['frame']
            filename = frame.f_code.co_filename
            separator = '-' * 40

            formatted = ['|  ' + line for line in tb['source']]
            formatted[-1] = f'->' + formatted[-1][2:]
            formatted_tracebacks.append([
                f'- {filename}:{tb["line"]}',
                separator,
                *formatted,
                separator,
            ])

        # Add the actual exception on the last one
        if formatted_tracebacks:
            exc = tb["exception"]
            formatted_tracebacks[-1].extend([
                f'- {type(exc).__name__}: {exc}',
                separator,
            ])

        return formatted_tracebacks or []

    @property
    def gather_tracebacks(self):
        tracebacks = []
        tracebacks.extend(getattr(self._case, '__tracebacks__', []))
        tracebacks.extend(getattr(self._spec.before_all, '__tracebacks__', []))
        tracebacks.extend(self.before_each_traces)
        tracebacks.extend(getattr(self._spec.after_all, '__tracebacks__', []))
        tracebacks.extend(self.after_each_traces)
        return tracebacks

    @property
    def as_dict(self):
        return {
            'name': self.name,
            'raw_name': self.raw_name,
            'class_name': self.class_name,
            'start': self.start,
            'end': self.end,
            'elapsed_time': self.elapsed_time,
            'success': self.successful,
            'skipped': self.skipped,
            'skip_reason': self.skip_reason,
            'metadata': self.metadata,
            'expects': [expect.as_dict for expect in self.expects],
            'errors': self.errors,
        }


class ExpectFormatData(object):
    def __init__(self, expect):
        self._expect = expect

    @property
    def evaluation(self):
        return str(self._expect)

    @property
    def required(self):
        return self._expect.required

    @property
    def success(self):
        return self._expect.success

    @property
    def target(self):
        return self._expect.target

    @property
    def expected(self):
        return self._expect.expected

    @property
    def target_name(self):
        return self._expect.src_params.expect_arg

    @property
    def expected_name(self):
        return self._expect.src_params.cmp_arg

    @property
    def as_dict(self):
        return {
            'evaluation': self.evaluation,
            'required': self.required,
            'success': self.success,
            'target': self.target,
            'target_name': self.target_name,
            'expected': self.expected,
            'expected_name': self.expected_name,
        }
