from spektrum import logger
from spektrum.reporting.data import CaseFormatData, SpecFormatData
from spektrum.reporting.testrail import TestRailRenderer

log = logger.get(__name__)


class ReportManager(object):
    def __init__(self, reporting_options=None):
        self.version = '2.0'
        self.specs = {}
        self.reporting_options = reporting_options or {}
        self.success = True
        self.reporters = {
            'testrail': TestRailRenderer(reporting_options),
        }

    @property
    def parent_specs(self):
        return [
            spec
            for spec in self.specs.values()
            if not spec.parent
        ]

    def track_top_level(self, specs, all_inherited, metadata, test_names, exclude):
        for reporter in self.reporters.values():
            if reporter.enabled:
                reporter.track_top_level(specs, all_inherited, metadata, test_names, exclude)

    def start_reporting(self, dry_run):
        for reporter in self.reporters.values():
            if reporter.enabled:
                reporter.start_reporting(dry_run)

    def track_spec(self, spec):
        self.specs[spec._id] = spec

    def case_finished(self, spec, case):
        if not case:
            return

        data = CaseFormatData(spec, case)
        indicator = '.'

        if not data.successful:
            indicator = 'F'
            self.success = False

        elif data.skipped:
            indicator = 'S'

        for _, reporter in self.reporters.items():
            if reporter.enabled:
                reporter.report_case(spec, case)

        print(indicator, end='', flush=True)

    def spec_finished(self, spec):
        for _, reporter in self.reporters.items():
            if reporter.enabled:
                reporter.report_spec(spec)

    def build_report(self):
        return [
            SpecFormatData(spec)
            for spec in self.parent_specs
        ]
