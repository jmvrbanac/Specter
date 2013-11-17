from os import path
from itertools import chain

from pynsive import PluginManager, rlist_classes
from specter.spec import Describe


class SuiteScanner(object):

    def __init__(self, search_path='spec'):
        super(SuiteScanner, self).__init__()
        self.search_path = search_path
        self.plugin_manager = PluginManager()

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

    def scan(self, search_path=None, module_name=None):
        search_path = search_path or self.search_path
        search_path = path.abspath(search_path)
        module = path.split(search_path)[1]

        if not path.exists(path.join(search_path)):
            return []

        self.plugin_manager.plug_into(path.split(search_path)[0])

        classes = rlist_classes(module, cls_filter=Describe.plugin_filter)
        if module_name:
            classes = self.filter_by_module_name(classes, module_name)

        return classes

    def destroy(self):
        self.plugin_manager.destroy()
