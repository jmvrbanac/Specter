import json

from specter import logger, utils
from specter.spec import get_case_data


class ReportManager(object):
    def __init__(self):
        self.version = '2.0'
        self.specs = {}

    def track_spec(self, spec):
        self.specs[spec._id] = {
            'name': utils.camelcase_to_spaces(type(spec).__name__),
            'module': spec.__module__,
            'doc': spec.__doc__,
            'cases': [],
        }

    def case_finished(self, spec, case):
        parent = None
        data = get_case_data(case)
        tracebacks = getattr(case, '__tracebacks__', [])
        successful = (
            not tracebacks and
            all(expect.success for expect in spec.__expects__[case])
        )

        # TODO: Clean this up
        for tb in tracebacks:
            frame = tb['frame']
            filename = frame.f_code.co_filename
            separator = '-' * (len(filename) + 2)

            formatted = ['|  ' + line for line in tb['source']]
            formatted[-1] = f'-->' + formatted[-1][2:]
            tb['formatted'] = '\n'.join([
                separator,
                f'- {filename}',
                separator,
                *formatted,
                separator,
            ])

        if spec.parent and spec.parent._id in self.specs:
            parent = spec.parent._id

        self.specs[spec._id]['cases'].append({
            'name': utils.snakecase_to_spaces(case.__name__),
            'raw_name': case.__name__,
            'start': data.start_time,
            'end': data.end_time,
            'parent': parent,
            'success': successful,
            'skipped': False,
            'metadata': data.metadata,
            'expects': [
                {
                    'evaluation': str(exp),
                    'required': exp.required,
                    'success': exp.success,
                }
                for exp in spec.__expects__[case]
            ],
            'error': '\n'.join([tb['formatted'] for tb in tracebacks]) or None
        })

    def output(self):
        print(json.dumps(self.specs, indent=2))
