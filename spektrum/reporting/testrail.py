from enum import Enum
from datetime import datetime

from spektrum import logger, utils
from spektrum.reporting.data import CaseFormatData, SpecFormatData

import httpx

log = logger.get(__name__)
UNICODE_SKIP = u'\u2607'
UNICODE_SEP = u'\u221F'
UNICODE_ARROW = u'\u2192'
UNICODE_ARROW_BAR = u'\u219B'
UNICODE_CHECK = u'\u2713'
UNICODE_X = u'\u2717'


class TestRailStatus(Enum):
    PASSED = 1
    BLOCKED = 2
    UNTESTED = 3
    RETEST = 4
    FAILED = 5
    SKIPPED = 7


class TestRailRenderer(object):
    def __init__(self, reporting_options=None):
        self.reporting_options = reporting_options or {}
        self.enabled = False
        self.project = self.reporting_options.get('tr_project')
        self.suite = self.reporting_options.get('tr_suite')
        self.template = self.reporting_options.get('tr_template')
        self.run = self.reporting_options.get('tr_run')
        self.sections = {}
        self.specs = {}
        self.tr = TestRailClient(
            endpoint=self.reporting_options.get('tr_endpoint'),
            username=self.reporting_options.get('tr_username'),
            api_key=self.reporting_options.get('tr_apikey'),
        )

        if self.tr.username and self.tr.api_key:
            self.enabled = True
            self.sections = structure_testrail_dict(
                self.tr.get_sections(self.project, self.suite).json()
            )

    def reconcile_spec_and_section(self, spec, metadata, test_names, exclude, sections=None):
        utils.filter_cases_by_data(spec, metadata, test_names, exclude)

        spec = TestRailSpecData(spec)

        tr_section = next(
            (section for section in (sections or []) if section['name'] == spec.name),
            None
        )

        if tr_section:
            spec.section_id = tr_section.get('id')
            spec.suite_id = tr_section.get('suite_id')

        else:
            parent_id = None
            if spec.parent:
                parent_id = self.specs[spec.parent.id].section_id

            resp = self.tr.add_section(
                self.project,
                self.suite,
                name=spec.name,
                description='',
                parent_id=parent_id,
            )

            spec.section_id = resp.json()['id']
            spec.suite_id = resp.json()['suite_id']

        self.specs[spec.id] = spec

        tr_cases = self.tr.get_cases(self.project, spec.suite_id, spec.section_id)
        for case in spec.cases:
            tr_case = next(
                (c for c in tr_cases if c['title'] == case.name),
                None
            )

            if not tr_case:
                resp = self.tr.add_case(
                    spec.section_id,
                    case.name,
                    template=self.template,
                )
                case.case_id = resp.json()['id']
                case.section_id = resp.json()['section_id']

            else:
                case.case_id = tr_case['id']
                case.section_id = tr_case['section_id']
                test_yaml = utils.get_yaml_fragment(case.doc or '')

                case_data = {
                    'title': case.name,
                    'template_id': self.template,
                    'custom_description': test_yaml.get('description'),
                }
                tr_data = utils.extract_dict(tr_case, case_data.keys())
                diff = utils.flat_dict_diff(case_data, tr_data)

                if diff:
                    resp = self.tr.update_case(case.case_id, **diff)

        for child in spec.specs:
            child_sections = []
            if tr_section:
                child_sections = tr_section['children'].values()

            self.reconcile_spec_and_section(child._spec, metadata, test_names, exclude, child_sections)

    def track_top_level(self, specs, metadata, test_names, exclude):
        for spec in specs:
            self.reconcile_spec_and_section(spec, metadata, test_names, exclude, self.sections.values())

    def start_reporting(self, dry_run):
        if dry_run:
            return

        if not self.run:
            time = datetime.now().strftime('%m/%d/%Y, %H:%M:%S%p')
            resp = self.tr.add_run(
                project_id=self.project,
                suite_id=self.suite,
                name=f'Spektrum {time}'
            )
            self.run = resp.json()['id']

    def report_case(self, spec, case):
        cached_data = self.get_cached_case_data(spec, case.__name__)

        case_data = TestRailCaseData(spec, case)
        case_data.case_id = cached_data.case_id
        case_data.section_id = cached_data.section_id

        status = TestRailStatus.FAILED
        if case_data.successful:
            status = TestRailStatus.PASSED
        elif case_data.skipped:
            status = TestRailStatus.SKIPPED

        timespan = int(case_data.elapsed_time) or 1

        lines = []
        mark = UNICODE_CHECK
        for expect in case_data.expects:
            mark = UNICODE_CHECK if expect.success else UNICODE_X
            arrow = UNICODE_ARROW_BAR if expect.required else UNICODE_ARROW

            lines.append(f'{arrow} {mark} {expect.evaluation}')

            if not expect.success:
                lines.append('    Values:')
                lines.append('    -------')
                lines.append(f'    | {expect.target_name}: {expect.target}')

                if str(expect.expected_name) != str(expect.expected):
                    lines.append(f'    | {expect.expected_name}: {expect.expected}')

        self.tr.add_result_for_case(
            run_id=self.run,
            case_id=case_data.case_id,
            status=status,
            elapsed=f'{timespan}s',
            comment='\n'.join(lines),
        )

    def report_spec(self, spec):
        pass
        # import pdb; pdb.set_trace()

    def render(self, report):
        self.report = report

    def get_cached_case_data(self, spec, raw_name):
        return next(
            (case for case in self.specs[spec._id].cases if case.raw_name == raw_name),
            None
        )


class TestRailCaseData(CaseFormatData):
    def __init__(self, spec, case):
        super().__init__(spec, case)
        self.case_id = None
        self.section_id = None


class TestRailSpecData(SpecFormatData):
    _case_format_cls = TestRailCaseData

    def __init__(self, spec):
        super().__init__(spec)
        self.section_id = None
        self.suite_id = None


class TestRailClient(object):
    def __init__(self, endpoint, username, api_key):
        self.endpoint = f'{endpoint}/index.php?'
        self.username = username
        self.api_key = api_key

    def _get_paginated(self, item_collection, url=None, auth=None, params=None, timeout=None):
        resp = httpx.get(url, auth=auth, params=params, timeout=timeout)
        data = resp.json()
        offset = data.get('offset', 0)
        limit = data.get('limit', 150)
        items = data.get(item_collection, [])

        if data.get('_links', {}).get('next'):
            params.update({
                'offset': offset + limit,
                'limit': limit,
            })
            items.extend(
                self._get_paginated(item_collection, url=url, auth=auth, params=params)
            )

        return items

    def add_result_for_case(self, run_id, case_id, status, elapsed, comment):
        body = utils.clean_dictionary({
            'status_id': status.value,
            'elapsed': elapsed,
            'comment': comment,
        })

        return httpx.post(
            f'{self.endpoint}/api/v2/add_result_for_case/{run_id}/{case_id}',
            json=body,
            auth=(self.username, self.api_key),
            timeout=30,
        )

    def add_run(self, project_id, suite_id, name):
        body = utils.clean_dictionary({
            'suite_id': suite_id,
            'name': name,
        })

        return httpx.post(
            f'{self.endpoint}/api/v2/add_run/{project_id}',
            json=body,
            auth=(self.username, self.api_key),
            timeout=30,
        )

    def add_section(self, project_id, suite_id, name, description='', parent_id=None):
        body = utils.clean_dictionary({
            'suite_id': suite_id,
            'name': name,
            'description': description,
            'parent_id': parent_id,
        })

        return httpx.post(
            f'{self.endpoint}/api/v2/add_section/{project_id}',
            json=body,
            auth=(self.username, self.api_key),
            timeout=30,
        )

    def add_case(self, section_id, title, template=None, description=None):
        body = utils.clean_dictionary({
            'title': title,
            'template_id': template,
            'custom_description': description,
        })

        return httpx.post(
            f'{self.endpoint}/api/v2/add_case/{section_id}',
            json=body,
            auth=(self.username, self.api_key),
            timeout=30,
        )

    def update_case(self, case_id, **kwargs):
        body = utils.clean_dictionary(kwargs)

        return httpx.post(
            f'{self.endpoint}/api/v2/update_case/{case_id}',
            json=body,
            auth=(self.username, self.api_key),
            timeout=30
        )

    def get_sections(self, project_id, suite_id):
        return httpx.get(
            f'{self.endpoint}/api/v2/get_sections/{project_id}/&suite_id={suite_id}',
            auth=(self.username, self.api_key),
            timeout=30,
        )

    def get_cases(self, project_id, suite_id, section_id=None):
        parameters = {
            f'/api/v2/get_cases/{project_id}': None,
            'suite_id': suite_id,
            'limit': 50,
        }
        if section_id:
            parameters['section_id'] = section_id

        return self._get_paginated(
            'cases',
            url=f'{self.endpoint}',
            auth=(self.username, self.api_key),
            params=parameters,
            timeout=30
        )


def restructure(sections, level=0, structured=None):
    structured = structured or {}

    at_depth = {k: v for k, v in sections.items() if v['depth'] == level}

    for section_id, section in at_depth.items():
        parent_id = section['parent_id']

        if parent_id and parent_id not in structured:
            parent = sections[parent_id]
            structured[parent['id']] = parent

            if 'children' not in structured[parent['id']]:
                structured[parent['id']]['children'] = {}

            structured[parent_id]['children'][section_id] = section

        elif parent_id and parent_id in structured:
            structured[parent_id]['children'][section_id] = section

        elif parent_id is None and section_id not in structured:
            structured[section_id] = section
            structured[section_id]['children'] = {}

    return structured


def flatten_testrail_dict(data):
    return {section['id']: section for section in data.get('sections')}


def structure_testrail_dict(data):
    flattened = flatten_testrail_dict(data)
    depth_list = [v['depth'] for _, v in flattened.items()]
    max_depth = 1

    if len(depth_list) > 0:
        max_depth = max(depth_list)

    restructured = None
    for i in range(max_depth, -1, -1):
        restructured = restructure(flattened, i, restructured)

    return restructured
