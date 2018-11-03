import ast
import sys

from specter import logger

log = logger.get(__name__)

SOURCE_CACHE = {}


def get_fullname(obj):
    obj_type = obj

    if not isinstance(obj, type):
        obj_type = type(obj)

    return f'{obj_type.__module__}.{obj_type.__name__}'


def get_tracebacks(exc):
    *_, exc_traceback = sys.exc_info()
    tracebacks = []

    for level in range(5):
        exc_traceback = exc_traceback.tb_next
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
