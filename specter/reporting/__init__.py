from six import add_metaclass
from abc import ABCMeta, abstractmethod
from pynsive import rlist_classes


@add_metaclass(ABCMeta)
class AbstractReporterPlugin(object):

    def process_arguments(self, args):
        pass  # pragma: no cover

    def finished(self):
        pass  # pragma: no cover

    @abstractmethod
    def get_name(self):
        pass  # pragma: no cover

    @abstractmethod
    def subscribe_to_describe(self, describe):
        pass  # pragma: no cover


@add_metaclass(ABCMeta)
class AbstractConsoleReporterPlugin(AbstractReporterPlugin):

    @abstractmethod
    def print_summary(self):
        pass  # pragma: no cover


class ReporterPluginManager(object):

    def __init__(self):
        self.reporters = []
        self.load_reporters()

    def get_console_reporters(self):
        return [reporter for reporter in self.reporters
                if issubclass(type(reporter), AbstractConsoleReporterPlugin)]

    def process_arguments(self, args):
        [reporter.process_arguments(args) for reporter in self.reporters]

    def subscribe_all_to_describe(self, describe):
        for reporter in self.reporters:
            reporter.subscribe_to_describe(describe)

    def finish_all(self):
        [reporter.finished() for reporter in self.reporters]

    def reporter_filter(self, class_type):
        return (issubclass(class_type, AbstractReporterPlugin) and
                class_type != AbstractReporterPlugin and
                class_type != AbstractConsoleReporterPlugin)

    def get_reporters_classes(self):
        return rlist_classes('specter.reporting', self.reporter_filter)

    def load_reporters(self, force_reload=False):
        if force_reload:
            self.reporters = []

        if not self.reporters:
            classes = self.get_reporters_classes()
            for klass in classes:
                self.reporters.append(klass())
        return self.reporters
