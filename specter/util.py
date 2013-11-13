import inspect
import re
import traceback
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


def get_real_last_traceback(exception):
    """ An unfortunate evil... All because Python's traceback cannot
    determine where my executed code is coming from...
    """
    last_module_path = 'Couldn\'t locate module'
    try:
        last_frame = inspect.currentframe().f_back.f_back
        last_module = inspect.getmodule(type(last_frame.f_locals['self']))
        last_module_path = last_module.__file__
        lines = inspect.getsourcelines(last_module)[0]
        exc_type, exc_value, exc_traceback = sys.exc_info()

        center = traceback.extract_tb(exc_traceback)[-1][1] - 1
        start = center - 2 if center - 2 > 0 else 0
        end = center + 2 if center + 2 <= len(lines) else len(lines)
        orig_src_lines = [line.rstrip('\n') for line in lines[start:end]]

        line_range = range(start+1, end+1)
        nums_and_source = zip(line_range, orig_src_lines)

        traceback_lines = ['{0}: {1}'.format(num, line)
                     for num, line in nums_and_source]
    except Exception as e:
        traceback_lines = ['Error finding traceback!', e]

    traceback_lines.insert(0, 'Error:')
    traceback_lines.insert(1, ' - {0}'.format(last_module_path))
    traceback_lines.insert(2, '------------------')
    traceback_lines.append('------------------')
    traceback_lines.append(exception)

    return traceback_lines
