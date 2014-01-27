import gettext
import sys

gettext_kwargs = {}
if sys.version_info[0] < 3:
    # Python 2 requires the unicode argument to be set
    gettext_kwargs['unicode'] = 1

gettext.install('specter', **gettext_kwargs)


def _(msg):
    """ Dealing with pylint problems"""
    return gettext.gettext(msg)

# Aliasing commonly used classes
from specter.spec import Describe, Spec, fixture   # NOQA
from specter.spec import DataDescribe, DataSpec  # NOQA
from specter.expect import expect, require, skip, skip_if  # NOQA
from specter.expect import incomplete, metadata  # NOQA
