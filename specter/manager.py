import multiprocessing as mp
import threading
from time import time
from specter.spec import TestEvent


class ExecuteTestProcess(mp.Process):
    def __init__(self, work_queue, all_cases, all_parents,
                 pipe):
        super(ExecuteTestProcess, self).__init__()
        self.work_queue = work_queue
        self.all_cases = all_cases
        self.all_parents = all_parents
        self.worked = mp.Value('i', 0)
        self.pipe = pipe

    def run(self):
        last_time = time()
        completed = []
        while True:
            # Get item and get real function to execute
            case_wrapper = self.work_queue.get()
            if case_wrapper == 'STOP':
                # Make sure buffer is cleared
                if len(completed) > 0:
                    self.pipe.send(completed)
                    #self.completed_queue.put(completed)
                    self.completed = []
                self.pipe.send(None)
                #self.completed_queue.put(None)
                return

            case_wrapper.case_func = self.all_cases[case_wrapper.case_func]
            case_wrapper.parent = self.all_parents[case_wrapper.parent]
            case_wrapper.execute()
            self.worked.value += 1
            completed.append(case_wrapper)

            # Flush completed buffer to queue
            if completed and time() >= (last_time + 0.01):
                self.pipe.send(completed)
                #self.completed_queue.put(completed)
                completed = []
                last_time = time()


class TestManager(object):

    def __init__(self, num_processes=6):
        self.processes = []
        self.num_processes = num_processes
        self.stops_hit = 0
        self.thead_lock = threading.Lock()
        self.work_queue = mp.Queue()
        self.active_pipes = []
        self.case_functions = {}
        self.case_parents = {}

    def add_to_queue(self, case_wrapper):
        self.work_queue.put(case_wrapper)

        # Keep track of wrappers and parents
        self.case_functions[case_wrapper.id] = case_wrapper.case_func
        self.case_parents[case_wrapper.parent.id] = case_wrapper.parent

    def sync_wrappers(self, wrapper_list):
        for wrapper in wrapper_list:
            parent_id = wrapper.parent
            wrapper_id = wrapper.case_func

            wrapper.parent = self.case_parents[parent_id]
            wrapper.case_func = self.case_functions[wrapper_id]
            wrapper.parent.cases[wrapper_id] = wrapper
            wrapper.parent.top_parent.dispatch(TestEvent(wrapper))

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
                self.case_parents, child_pipe)
            self.active_pipes.append(parent_pipe)
            self.processes.append(test_process)
            self.work_queue.put('STOP')
            test_process.start()

        self.sync_wrappers_from_pipes()

        # Join already completed processes for good measure
        total_tests = 0
        for test_process in list(self.processes):
            test_process.join()
            total_tests += test_process.worked.value
            self.processes.remove(test_process)

        print 'Total Tests Processed:', total_tests

        for pipe in self.active_pipes:
            pipe.close()
