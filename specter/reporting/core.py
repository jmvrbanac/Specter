from specter import logger, utils
from specter.spec import get_case_data


class ReportManager(object):
    def __init__(self):
        self.version = '2.0'
        self.specs = {}

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
        print('.', end='', flush=True)

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
    def as_dict(self):
        return {
            'name': self.name,
            'module': self.module,
            'doc': self.doc,
            'successful': self.successful,
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
    def start(self):
        return get_case_data(self._case).start_time

    @property
    def end(self):
        return get_case_data(self._case).end_time

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
    def successful(self):
        tracebacks = getattr(self._case, '__tracebacks__', [])
        return (
            not tracebacks and
            all(expect.success for expect in self.expects)
        )

    @property
    def errors(self):
        tracebacks = getattr(self._case, '__tracebacks__', [])
        formatted_tracebacks = []

        # TODO: Clean this up
        for tb in tracebacks:
            frame = tb['frame']
            filename = frame.f_code.co_filename
            separator = '-' * (len(filename) + 2)

            formatted = ['|  ' + line for line in tb['source']]
            formatted[-1] = f'-->' + formatted[-1][2:]
            formatted_tracebacks.append('\n'.join([
                separator,
                f'- {filename}',
                separator,
                *formatted,
                separator,
            ]))

        return '\n'.join(formatted_tracebacks) or None

    @property
    def as_dict(self):
        return {
            'name': self.name,
            'raw_name': self.raw_name,
            'start': self.start,
            'end': self.end,
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
    def as_dict(self):
        return {
            'evaluation': self.evaluation,
            'required': self.required,
            'success': self.success,
        }
