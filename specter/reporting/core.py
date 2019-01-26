import json

from specter import logger, utils
from specter.spec import get_case_data


class ReportManager(object):
    def __init__(self):
        self.version = '2.0'
        self.specs = {}

    def track_spec(self, spec):
        self.specs[spec._id] = spec

    def case_finished(self, spec, case):
        print('.', end='', flush=True)

    def report_specter_format(self):
        data = [
            SpecFormatData(spec).as_dict
            for spec in self.specs.values()
            if not spec.parent
        ]
        print(json.dumps(data, indent=2))
        return data


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
    def successful(self):
        tracebacks = getattr(self._case, '__tracebacks__', [])
        return (
            not tracebacks and
            all(
                expect.success
                for expect in self._spec.__expects__[self._case]
            )
        )

    @property
    def expects(self):
        return [
            {
                'evaluation': str(exp),
                'required': exp.required,
                'success': exp.success,
            }
            for exp in self._spec.__expects__[self._case]
        ]

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
            'skipped': False,
            'metadata': self.metadata,
            'expects': self.expects,
            'errors': self.errors,
        }
