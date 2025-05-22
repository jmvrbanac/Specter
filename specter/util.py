import ast
import inspect
import re
import itertools
import sys

from specter.vendor.ast_decompiler import decompile

try:
    import __builtin__
except ImportError:
    import builtins as __builtin__

CAPTURED_TRACEBACKS = []


class ExpectParams(object):
    types_with_args = [
        'equal',
        'almost_equal',
        'be_greater_than',
        'be_less_than',
        'be_almost_equal',
        'be_a',
        'be_an_instance_of',
        'be_in',
        'contain',
        'raise_a'
    ]

    def __init__(self, line, module):
        def distance(node):
            return abs(node.lineno - line)

        tree = ast.parse(inspect.getsource(module))

        # Walk the tree until we get the expression we need
        expect_exp = None
        closest_exp = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr):
                if node.lineno == line:
                    expect_exp = node
                    break

                if (closest_exp is None or
                        distance(node) < distance(closest_exp)):
                    closest_exp = node

        self.expect_exp = expect_exp or closest_exp

    @property
    def cmp_call(self):
        if self.expect_exp:
            return self.expect_exp.value

    @property
    def expect_call(self):
        if self.cmp_call:
            return self.cmp_call.func.value.value

    @property
    def cmp_type(self):
        if self.cmp_call:
            return self.cmp_call.func.attr

    @property
    def cmp_arg(self):
        arg = None
        if self.cmp_type in self.types_with_args:
            arg = decompile(self.cmp_call.args[0])
        return arg

    @property
    def expect_type(self):
        return self.expect_call.func.id

    @property
    def expect_arg(self):
        if self.expect_call:
            return decompile(self.expect_call.args[0])


def convert_camelcase(input_str):
    if input_str is None:
        return ''

    camelcase_tags = '((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))'
    return re.sub(camelcase_tags, r' \1', input_str)


def get_module_and_line(use_child_attr=None):
    last_frame = inspect.currentframe()

    steps = 2
    for i in range(steps):
        last_frame = last_frame.f_back

    self = module = last_frame.f_locals['self']
    # Use an attr instead of self
    if use_child_attr:
        module = getattr(self, use_child_attr, self)

    return last_frame.f_lineno, inspect.getmodule(type(module))


def get_source_from_frame(frame):
    self = frame.f_locals.get('self', None)
    cls = frame.f_locals.get('cls', None)

    # for old style classes, getmodule(type(self)) returns __builtin__, and
    # inspect.getfile(__builtin__) throws an exception
    insp_obj = inspect.getmodule(type(self) if self else cls) or frame.f_code
    if insp_obj == __builtin__:
        insp_obj = frame.f_code

    line_num_modifier = 0
    if inspect.iscode(insp_obj):
        line_num_modifier -= 1

    module_path = inspect.getfile(insp_obj)
    source_lines = inspect.getsourcelines(insp_obj)
    return source_lines[0], module_path, source_lines[1] + line_num_modifier


def get_all_tracebacks(tb, tb_list=[]):
    tb_list.append(tb)
    next_tb = getattr(tb, 'tb_next')
    if next_tb:
        tb_list = get_all_tracebacks(next_tb, tb_list)
    return tb_list


def get_numbered_source(lines, line_num, starting_line=0):
    try:
        center = (line_num - starting_line) - 1
        start = center - 2 if center - 2 > 0 else 0
        end = center + 2 if center + 2 <= len(lines) else len(lines)

        orig_src_lines = [line.rstrip('\n') for line in lines[start:end]]
        line_range = range(start + 1 + starting_line, end + 1 + starting_line)
        nums_and_source = zip(line_range, orig_src_lines)

        traceback_lines = []
        for num, line in nums_and_source:
            prefix = '--> ' if num == line_num else '    '
            traceback_lines.append('{0}{1}: {2}'.format(prefix, num, line))

        return traceback_lines
    except Exception as e:
        return ['Error finding traceback!', e]


def get_real_last_traceback(exception):
    """ An unfortunate evil... All because Python's traceback cannot
    determine where my executed code is coming from...
    """
    traceback_blocks = []
    _n, _n, exc_traceback = sys.exc_info()
    tb_list = get_all_tracebacks(exc_traceback)[1:]

    # Remove already captured tracebacks
    # TODO(jmv): This must be a better way of doing this. Need to revisit.
    tb_list = [tb for tb in tb_list if tb not in CAPTURED_TRACEBACKS]
    CAPTURED_TRACEBACKS.extend(tb_list)

    for traceback in tb_list:
        lines, path, line_num = get_source_from_frame(traceback.tb_frame)
        traceback_lines = get_numbered_source(lines, traceback.tb_lineno,
                                              line_num)

        traceback_lines.insert(0, '  - {0}'.format(path))
        traceback_lines.insert(1, '  ------------------')
        traceback_lines.append('  ------------------')
        traceback_blocks.append(traceback_lines)

    traced_lines = ['Error Traceback:']
    traced_lines.extend(itertools.chain.from_iterable(traceback_blocks))
    traced_lines.append('  - Error | {0}: {1}'.format(
        type(exception).__name__, exception))

    return traced_lines


def find_by_names(names, cases):
    selected_cases = {}
    for case_id, case in cases.items():
        if case.name in names or case.pretty_name in names:
            selected_cases[case_id] = case

    return selected_cases


def children_with_tests_named(names, describe):
    children = []
    for child in describe.describes:
        found = find_by_names(names, child.cases)
        if len(found) > 0:
            children.append(child)
        children.extend(children_with_tests_named(names, child))

    return children


def find_by_metadata(meta, cases):
    selected_cases = {}
    for case_id, case in cases.items():
        matched_keys = set(meta.keys()) & set(case.metadata.keys())

        for key in matched_keys:
            if meta.get(key) == case.metadata.get(key):
                selected_cases[case_id] = case

    return selected_cases


def children_with_tests_with_metadata(meta, describe):
    children = []
    for child in describe.describes:
        found = find_by_metadata(meta, child.cases)
        if len(found) > 0:
            children.append(child)
        children.extend(children_with_tests_with_metadata(meta, child))
    return children


def extract_metadata(case_func):
    # Handle metadata decorator
    metadata = {}
    if 'DECORATOR_ONCALL' in case_func.__name__:
        try:
            decorator_data = case_func()
            case_func = decorator_data[0]
            metadata = decorator_data[1]
        except Exception as e:
            # Doing this old school to avoid dependancy conflicts
            handled = ['TestIncompleteException', 'TestSkippedException']
            if type(e).__name__ in handled:
                case_func = e.func
                metadata = e.other_data.get('metadata')
            else:
                raise e
    return case_func, metadata


def remove_empty_entries_from_dict(input_dict):
    return {k: v for k, v in input_dict.items() if v is not None}
