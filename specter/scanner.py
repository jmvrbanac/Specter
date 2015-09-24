from os import path
from itertools import chain

# from pynsive import PluginManager, rlist_classes
from pike.manager import PikeManager
from specter.spec import Describe


class SuiteScanner(object):

    def __init__(self, search_path):
        super(SuiteScanner, self).__init__()
        self.search_path = path.abspath(search_path)
        self.plugin_manager = PikeManager([self.search_path])

    def filter_by_module_name(self, classes, name):
        found = [cls for cls in classes
                 if name in '{}.{}'.format(cls.__module__, cls.__name__)]

        # Only search children if the class cannot be found at the package lvl
        if not found:
            children = [cls.__get_all_child_describes__() for cls in classes]
            children = chain.from_iterable(children)
            found = [cls for cls in children
                     if name in '{}.{}'.format(cls.__module__, cls.__name__)]

        return found

    def scan(self, module_name=None):
        if not path.exists(path.join(self.search_path)):
            return []

        classes = self.plugin_manager.get_classes(Describe.plugin_filter)
        if module_name:
            classes = self.filter_by_module_name(classes, module_name)

        return classes

    def destroy(self):
        self.plugin_manager.cleanup()
