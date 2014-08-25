import inspect
import re
import itertools
import sys
import six

CAPTURED_TRACEBACKS = []


def convert_camelcase(input_str):
    if input_str is None:
        return ''

    camelcase_tags = '((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))'
    return re.sub(camelcase_tags, r' \1', input_str)


def get_called_src_line(steps=2, use_child_attr=None):
    src_line, last_frame = None, inspect.currentframe()

    for i in range(steps):
        last_frame = last_frame.f_back

    self = module = last_frame.f_locals['self']
    # Use an attr instead of self
    if use_child_attr:
        module = getattr(self, use_child_attr)

    try:
        last_module = inspect.getmodule(type(module))
        line = last_frame.f_lineno - 1
        src_line = inspect.getsourcelines(last_module)[0][line]
    except:
        pass
    return src_line


def get_expect_param_strs(src_line):
    matches = re.search('\((.*?)\)\..*\((.*?)\)', src_line)
    return (matches.group(1), matches.group(2)) if matches else None


def get_source_from_frame(frame):
    self = frame.f_locals.get('self', None)
    cls = frame.f_locals.get('cls', None)
    insp_obj = inspect.getmodule(type(self) if self else cls) or frame.f_code

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
        line_range = range(start+1+starting_line, end+1+starting_line)
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


def find_by_metadata(meta, cases):
    selected_cases = {}
    for case_id, case in six.iteritems(cases):
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
