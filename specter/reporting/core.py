import json

from specter import logger, utils
from specter.spec import get_case_data, spec_as_dict


class ReportManager(object):
    def __init__(self):
        self.version = '2.0'
        self.specs = {}

    def track_spec(self, spec):
        self.specs[spec._id] = spec

    def case_finished(self, spec, case):
        print('.', end='', flush=True)

    def build_tree(self, parents=None):
        parent_specs = [
            spec_as_dict(spec)
            for spec in self.specs.values()
            if not spec.parent
        ]
        print(json.dumps(parent_specs, indent=2))
