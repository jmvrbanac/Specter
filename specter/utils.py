import ast
import inspect
import itertools
import re
import sys

from specter import logger

log = logger.get(__name__)

SOURCE_CACHE = {}
TRUE_STRINGS = frozenset(['true', 'True'])
FALSE_STRINGS = frozenset(['false', 'False'])


def get_fullname(obj):
    obj_type = obj

    if not isinstance(obj, type):
        obj_type = type(obj)

    return f'{obj_type.__module__}.{obj_type.__name__}'


def get_tracebacks(exc):
    *_, exc_traceback = sys.exc_info()
    tracebacks = []

    for level in range(5):
        if not exc_traceback:
            break

        path = exc_traceback.tb_frame.f_code.co_filename
        tb_source, _ = load_source_and_ast(path)
        start_line = exc_traceback.tb_lineno - 8
        end_line = exc_traceback.tb_lineno

        if start_line < 0:
            start_line = 0

        tracebacks.append({
            'exception': exc,
            'frame': exc_traceback.tb_frame,
            'line': exc_traceback.tb_lineno,
            'path': path,
            'source': tb_source.splitlines()[start_line:end_line],
        })

        exc_traceback = exc_traceback.tb_next

    # The only time we want the full list is when specter has a problem
    if len(tracebacks) > 1:
        tracebacks = tracebacks[1:]

    return tracebacks


def log_tracebacks(tracebacks):
    log.error('Error Tracebacks:')
    exc = tracebacks[-1]['exception']

    for tb in tracebacks:
        path = tb['path']
        block = [
            f'- {path}',
            f'{"-" * len(path)}',
            *tb['source'],
            f'{"-" * len(path)}',
        ]

        for line in block:
            log.error(line)

    log.error(f'- Error | {type(exc).__name__}: {exc}')


def load_source_and_ast(filename):
    source = SOURCE_CACHE.get(filename)

    if not source:
        with open(filename, 'r') as fp:
            SOURCE_CACHE[filename] = source = fp.read()

    return source, ast.parse(source)


def tag_as_inherited(f):
    f.__inherited_from_spec__ = True
    return f


def camelcase_to_spaces(value):
    if value is None:
        return ''

    return re.sub(
        '((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))',
        r' \1',
        value
    )


def snakecase_to_spaces(value):
    return value.replace('_', ' ')


def pretty_class_name(value):
    return f'{type(value).__module__}.{type(value).__qualname__}'


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


def get_function_kwargs(old_func, new_args):
    args, _, _, defaults, *_ = inspect.getfullargspec(old_func)
    if 'self' in args:
        args.remove('self')

    # Make sure we take into account required arguments
    kwargs = dict(itertools.zip_longest(args[::-1], list(defaults or ())[::-1], fillvalue=None))
    kwargs.update(new_args)
    return kwargs


def find_by_names(names, cases):
    return [
        case
        for case in cases
        if case.__name__ in names or snakecase_to_spaces(case.__name__) in names
    ]


def find_by_metadata(metadata, cases):
    selected_cases = []

    for case in cases:
        data = getattr(case, '__specter__', None)

        if not data or not data.metadata:
            continue

        matched_keys = set(metadata.keys()) & set(data.metadata.keys())

        for key in matched_keys:
            if metadata.get(key) == data.metadata.get(key):
                selected_cases.append(case)

    return selected_cases


def exclude_by_metadata(metadata, cases):
    selected_cases = []

    for case in cases:
        data = getattr(case, '__specter__', None)

        if not data or not data.metadata:
            selected_cases.append(case)
            continue

        matched_keys = set(metadata.keys()) & set(data.metadata.keys())

        if not matched_keys:
            selected_cases.append(case)

        for key in matched_keys:
            if metadata.get(key) != data.metadata.get(key):
                selected_cases.append(case)

    return selected_cases


def translate_cli_argument(argument):
    converted = argument

    if argument in TRUE_STRINGS:
        converted = True

    elif argument in FALSE_STRINGS:
        converted = False

    return converted


def traceback_occurred_msg(case_type):
    msg = 'Traceback occurred'
    if case_type == 'case':
        return f'{msg} during execution'
    return f'{msg} running {case_type}'
