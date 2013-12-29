from six import add_metaclass
from abc import ABCMeta, abstractmethod
from pynsive import rlist_classes


@add_metaclass(ABCMeta)
class AbstractReporterPlugin(object):
    """ Do not use a plugin base. Use the appropriate parallel and/or
    serial reporter abstracts depending on your use case.
    """

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
class AbstractParallelReporter(AbstractReporterPlugin):
    pass


@add_metaclass(ABCMeta)
class AbstractSerialReporter(AbstractReporterPlugin):
    pass


@add_metaclass(ABCMeta)
class AbstractConsoleReporter(AbstractReporterPlugin):

    @abstractmethod
    def print_summary(self):
        pass  # pragma: no cover


class ReporterPluginManager(object):

    def __init__(self, parallel=False):
        self.reporters = []
        self.load_reporters()
        self.parallel = parallel

    def get_console_reporters(self):
        return [reporter for reporter in self.reporters
                if issubclass(type(reporter), AbstractConsoleReporter) and
                self.can_use_reporter(reporter, self.parallel)]

    def process_arguments(self, args):
        self.parallel = args.parallel
        [reporter.process_arguments(args) for reporter in self.reporters]

    def can_use_reporter(self, reporter, parallel):
        can_use = False
        if parallel:
            if isinstance(reporter, AbstractParallelReporter):
                can_use = True
        else:
            if isinstance(reporter, AbstractSerialReporter):
                can_use = True
        return can_use

    def subscribe_all_to_describe(self, describe):
        """ Will automatically not subscribe reporters that are not parallel
        or serial depending on the current mode.
        """
        for reporter in self.reporters:
            if self.can_use_reporter(reporter, self.parallel):
                reporter.subscribe_to_describe(describe)

    def finish_all(self):
        [reporter.finished() for reporter in self.reporters]

    def reporter_filter(self, class_type):
        abstracts = [AbstractReporterPlugin, AbstractParallelReporter,
                     AbstractSerialReporter, AbstractConsoleReporter]

        return (issubclass(class_type, AbstractReporterPlugin) and
                class_type not in abstracts)

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
