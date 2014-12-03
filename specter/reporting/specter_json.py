import json

from specter import _
from specter.spec import DescribeEvent
from specter.reporting import AbstractParallelReporter, AbstractSerialReporter


class SpecterJsonReporter(AbstractSerialReporter, AbstractParallelReporter):
    """ A Specter JSON format report generator for the Specter framework. """

    def __init__(self):
        self.top_most_specs = []
        self.filename = ''

    def add_arguments(self, argparser):
        argparser.add_argument(
            '--json-results', dest='json_results', metavar='',
            help=_('Saves Specter JSON results into a specifed file'))

    def process_arguments(self, args):
        if args.json_results:
            self.filename = args.json_results

    def get_name(self):
        return 'Specter JSON report generator'

    def subscribe_to_spec(self, spec):
        spec.add_listener(DescribeEvent.COMPLETE, self.spec_complete)

    def spec_complete(self, evt):
        spec = evt.payload
        if not spec.parent:
            self.top_most_specs.append(spec)

    def finished(self, fp=None):
        if not self.filename:
            return

        serialized_specs = []
        for spec in self.top_most_specs:
            serialized_specs.append(spec.serialize())

        output = {
            'format': 'specter',
            'version': '0.1.0',
            'specs': serialized_specs
        }

        # Open and Write to file
        if not fp:
            fp = open(self.filename, 'w')

        json.dump(output, fp)
        fp.close()
