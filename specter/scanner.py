from os import path

from pynsive import PluginManager, rlist_classes
from specter.spec import Suite


class SuiteScanner(object):

    def __init__(self, module='spec', base_path='./'):
        super(SuiteScanner, self).__init__()
        self.base_path = base_path
        self.module = module

    def scan(self, module=None, base_path=None):
        base_path = base_path or self.base_path
        module = module or self.module

        if not path.exists(path.join(base_path, module)):
            return []

        plugin_manager = PluginManager()
        plugin_manager.plug_into(path.abspath(base_path))

        return rlist_classes(module, cls_filter=Suite.is_suite)
