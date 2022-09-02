from spektrum import logger, utils
from spektrum.reporting.data import SpecFormatData

import httpx

log = logger.get(__name__)


class TestRailRenderer(object):
    def __init__(self, reporting_options=None):
        self.reporting_options = reporting_options or {}
        self.enabled = False
        self.project = 1
        self.suite = 4
        self.template = 4
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

    def reconcile_spec_and_section(self, spec, sections=None):
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
                test_yaml = utils.get_yaml_fragment(case.doc)

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

            self.reconcile_spec_and_section(child._spec, child_sections)

    def track_top_level(self, specs):
        for spec in specs:
            self.reconcile_spec_and_section(spec, self.sections.values())

    def report_case(self, spec, case):
        pass

    def report_spec(self, spec):
        pass
        # import pdb; pdb.set_trace()

    def render(self, report):
        self.report = report


class TestRailSpecData(SpecFormatData):
    def __init__(self, spec):
        super().__init__(spec)
        self.section_id = None
        self.suite_id = None


class TestRailClient(object):
    def __init__(self, endpoint, username, api_key):
        self.endpoint = f'{endpoint}/index.php?'
        self.username = username
        self.api_key = api_key

    def _get_paginated(self, item_collection, url=None, auth=None, params=None):
        resp = httpx.get(url, auth=auth, params=params)
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
            auth=(self.username, self.api_key)
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
            auth=(self.username, self.api_key)
        )

    def update_case(self, case_id, **kwargs):
        body = utils.clean_dictionary(kwargs)

        return httpx.post(
            f'{self.endpoint}/api/v2/update_case/{case_id}',
            json=body,
            auth=(self.username, self.api_key)
        )

    def get_sections(self, project_id, suite_id):
        return httpx.get(
            f'{self.endpoint}/api/v2/get_sections/{project_id}/&suite_id={suite_id}',
            auth=(self.username, self.api_key)
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
