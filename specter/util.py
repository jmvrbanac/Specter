import inspect
import re
import itertools
import sys


def get_called_src_line():
    src_line = None
    try:
        last_frame = inspect.currentframe().f_back.f_back
        last_module = inspect.getmodule(type(last_frame.f_locals['self']))
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
    module = inspect.getmodule(type(self) if self else cls)
    module_path = module.__file__
    lines = inspect.getsourcelines(module)[0]
    return lines, module_path


def get_all_tracebacks(tb, tb_list=[]):
    tb_list.append(tb)
    next_tb = getattr(tb, 'tb_next')
    if next_tb:
        tb_list = get_all_tracebacks(next_tb, tb_list)
    return tb_list


def get_numbered_source(lines, line_num):
    try:
        center = line_num - 1
        start = center - 2 if center - 2 > 0 else 0
        end = center + 2 if center + 2 <= len(lines) else len(lines)

        orig_src_lines = [line.rstrip('\n') for line in lines[start:end]]
        line_range = range(start+1, end+1)
        nums_and_source = zip(line_range, orig_src_lines)

        traceback_lines = ['{0}: {1}'.format(num, line)
                           for num, line in nums_and_source]
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

    for traceback in tb_list:
        lines, last_module_path = get_source_from_frame(traceback.tb_frame)
        traceback_lines = get_numbered_source(lines, traceback.tb_lineno)

        traceback_lines.insert(0, ' - {0}'.format(last_module_path))
        traceback_lines.insert(1, '------------------')
        traceback_lines.append('------------------')
        traceback_blocks.append(traceback_lines)

    traceback_blocks[-1].append(' - Error: {0}'.format(exception))
    traced_lines = ['Error Traceback:']
    traced_lines.extend(itertools.chain.from_iterable(traceback_blocks))

    return traced_lines
