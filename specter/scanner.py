from os import path

from pynsive import PluginManager, rlist_classes
from specter.spec import Describe


class SuiteScanner(object):

    def __init__(self, search_path='spec'):
        super(SuiteScanner, self).__init__()
        self.search_path = search_path
        self.plugin_manager = PluginManager()

    def scan(self, search_path=None):
        search_path = search_path or self.search_path
        search_path = path.abspath(search_path)
        module = path.split(search_path)[1]

        if not path.exists(path.join(search_path)):
            return []


        self.plugin_manager.plug_into(path.split(search_path)[0])

        return rlist_classes(module, cls_filter=Describe.plugin_filter)

    def destroy(self):
        self.plugin_manager.destroy()
