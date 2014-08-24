import multiprocessing as mp
import threading
from time import time

from coverage import coverage
from specter.spec import TestEvent, DescribeEvent


class ExecuteTestProcess(mp.Process):
    def __init__(self, work_queue, all_cases, all_parents,
                 pipe, track_coverage=False, coverage_omit=None):
        super(ExecuteTestProcess, self).__init__()
        self.work_queue = work_queue
        self.all_cases = all_cases
        self.all_parents = all_parents
        self.worked = mp.Value('i', 0)
        self.pipe = pipe
        self.coverage = None

        if track_coverage:
            self.coverage = coverage(omit=coverage_omit, data_suffix=True)
            self.coverage._warn_no_data = False

    def run(self):  # pragma: no cover
        """ Note: CI Coverage is turned off due to it not showing covered
        even with there being tests that run this function.
        """
        last_time = time()
        completed = []

        if self.coverage:
            self.coverage.start()

        while True:
            # Get item and get real function to execute
            case_wrapper = self.work_queue.get()
            if case_wrapper == 'STOP':
                # Make sure buffer is cleared
                if len(completed) > 0:
                    self.pipe.send(completed)
                    self.completed = []
                self.pipe.send(None)

                if self.coverage:
                    self.coverage.stop()
                    self.coverage.save()
                return

            case_wrapper.case_func = self.all_cases[case_wrapper.case_func]
            case_wrapper.parent = self.all_parents[case_wrapper.parent]
            case_wrapper.parent._state.before_each()
            case_wrapper.execute(case_wrapper.parent._state)
            case_wrapper.parent._state.after_each()
            self.worked.value += 1
            completed.append(case_wrapper)

            # Flush completed buffer to queue
            if completed and time() >= (last_time + 0.01):
                self.pipe.send(completed)
                completed = []
                last_time = time()


class ParallelManager(object):

    def __init__(self, num_processes=6, track_coverage=False,
                 coverage_omit=None):
        self.processes = []
        self.num_processes = num_processes
        self.stops_hit = 0
        self.thead_lock = threading.Lock()
        self.work_queue = mp.Queue()
        self.active_pipes = []
        self.case_functions = {}
        self.case_parents = {}
        self.track_coverage = track_coverage
        self.coverage_omit = coverage_omit

    def add_to_queue(self, case_wrapper):
        self.work_queue.put(case_wrapper)

        # Keep track of wrappers and parents
        self.case_functions[case_wrapper.id] = case_wrapper.case_func
        self.case_parents[case_wrapper.parent.id] = case_wrapper.parent

    def sync_wrappers(self, wrapper_list):
        for wrapper in wrapper_list:
            parent_id = wrapper.parent
            wrapper_id = wrapper.case_func

            parent = wrapper.parent = self.case_parents[parent_id]
            wrapper.case_func = self.case_functions[wrapper_id]
            wrapper.parent.cases[wrapper_id] = wrapper
            wrapper.parent.top_parent.dispatch(TestEvent(wrapper))
            parent._num_completed_cases += 1

            while parent:
                if parent.complete:
                    evt = DescribeEvent(DescribeEvent.COMPLETE, parent)
                    parent._state.after_all()
                    parent.top_parent.dispatch(evt)
                    parent = parent.parent
                else:
                    parent = None

    def sync_wrappers_from_pipes(self):
        stops = 0
        while stops < self.num_processes:
            for pipe in self.active_pipes:
                if pipe.poll(0.01):
                    received = pipe.recv()
                    if received is None:
                        stops += 1
                    else:
                        self.sync_wrappers(received)
                    if stops >= self.num_processes:
                        break

    def execute_all(self):
        for i in range(0, self.num_processes):
            parent_pipe, child_pipe = mp.Pipe(duplex=False)
            test_process = ExecuteTestProcess(
                self.work_queue, self.case_functions,
                self.case_parents, child_pipe,
                track_coverage=self.track_coverage,
                coverage_omit=self.coverage_omit)
            self.active_pipes.append(parent_pipe)
            self.processes.append(test_process)
            self.work_queue.put('STOP')
            test_process.start()

        self.sync_wrappers_from_pipes()

        # Join processes for good measure
        total_tests = 0
        for test_process in list(self.processes):
            test_process.join()
            total_tests += test_process.worked.value
            self.processes.remove(test_process)

        for pipe in self.active_pipes:
            pipe.close()
