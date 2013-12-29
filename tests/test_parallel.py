import multiprocessing as mp
from unittest import TestCase

import six
from specter.spec import Spec, CaseWrapper
from specter.parallel import ParallelManager, ExecuteTestProcess


def _create_testing_spec():
    def sample_func():
        pass
    spec = Spec()
    wrapper = CaseWrapper(sample_func, spec)
    spec.cases[wrapper.id] = wrapper
    return spec, wrapper


class TestParallelManager(TestCase):

    def setUp(self):
        self.manager = ParallelManager(num_processes=1, track_coverage=True)
        for i in range(5):
            spec, wrapper = _create_testing_spec()
            self.manager.add_to_queue(wrapper)

    def execution(self):
        self.manager.execute_all()
        for parent in six.itervalues(self.manager.case_parents):
            self.assertTrue(parent.complete)


class TestExecuteTestProcess(TestCase):
    def setUp(self):
        spec, wrapper = _create_testing_spec()

        self.parent_pipe, self.child_pipe = mp.Pipe(duplex=False)
        self.work_queue = mp.Queue()
        self.work_queue.put(wrapper)
        self.work_queue.put('STOP')

        self.case_functions = {wrapper.id: wrapper.case_func}
        self.case_parents = {wrapper.parent.id: wrapper.parent}

        self.test_process = ExecuteTestProcess(
            self.work_queue, self.case_functions,
            self.case_parents, self.child_pipe, track_coverage=True,
            coverage_omit=[])

    def test_create_instance_without_coverage(self):
        inst = ExecuteTestProcess(work_queue=None, all_cases=None,
                                  all_parents=None, pipe=None,
                                  track_coverage=True, coverage_omit=[])
        self.assertIsNotNone(inst.coverage)

    def test_execute_a_process(self):
        self.test_process.run()

        result = self.parent_pipe.recv()
        self.assertIsNotNone(result)
        self.assertIsNotNone(self.test_process.coverage)
