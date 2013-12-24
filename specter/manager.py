import multiprocessing as mp
import threading
import Queue
from time import time, sleep
from specter.spec import TestEvent


class ExecuteTestProcess(mp.Process):
    def __init__(self, work_queue, completed_queue, all_cases, all_parents):
        super(ExecuteTestProcess, self).__init__()
        self.work_queue = work_queue
        self.completed_queue = completed_queue
        self.all_cases = all_cases
        self.all_parents = all_parents

    def run(self):
        last_time = time()
        completed = []
        while True:
            # Get item and get real function to execute
            case_wrapper = self.work_queue.get()
            if case_wrapper == 'STOP':
                # Make sure buffer is cleared
                if completed:
                    self.completed_queue.put(completed)
                    self.completed = []
                return

            case_wrapper.case_func = self.all_cases[case_wrapper.case_func]
            case_wrapper.parent = self.all_parents[case_wrapper.parent]

            case_wrapper.execute()
            completed.append(case_wrapper)

            # Flush completed buffer to queue
            if completed and time() >= (last_time + 0.01):
                self.completed_queue.put(completed)
                completed = []
                last_time = time()


def watch_completed(completed_queue, all_cases, all_parents):
    ticks = 0
    while True:
        wrapper_list = completed_queue.get()
        ticks += 1
        if wrapper_list == 'STOP':
            return

        for wrapper in wrapper_list:
            parent_hash = wrapper.parent
            func_hash = wrapper.case_func

            wrapper.parent = all_parents[parent_hash]
            wrapper.case_func = all_cases[func_hash]

            # parent_cases = enumerate(wrapper.parent.cases)
            # for index, val in parent_cases:
            #     if val.case_func == wrapper.case_func:
            #         wrapper.parent.cases[index] = wrapper

            wrapper.parent.top_parent.dispatch(TestEvent(wrapper))


class TestManager(object):

    def __init__(self, num_processes=6):
        self.processes = []
        self.num_processes = num_processes
        self.work_queue = mp.Queue()
        self.completed = mp.JoinableQueue()
        self.case_functions = {}
        self.case_parents = {}

    def add_to_queue(self, case_wrapper):
        self.work_queue.put(case_wrapper)

        # Keep track of test functions
        key = hash(case_wrapper.case_func)
        self.case_functions[key] = case_wrapper.case_func

        # Keep track of parents
        key = hash(case_wrapper.parent)
        self.case_parents[key] = case_wrapper.parent

    def execute_all(self):
        # Create monitor threads
        self.monitors = []
        for i in range(0, 6):
            args = (self.completed,
                    self.case_functions,
                    self.case_parents)
            monitor = threading.Thread(target=watch_completed, args=args)
            self.monitors.append(monitor)
            monitor.start()

        for i in range(0, self.num_processes):
            test_process = ExecuteTestProcess(
                self.work_queue, self.completed, self.case_functions,
                self.case_parents)
            self.processes.append(test_process)
            self.work_queue.put('STOP')
            test_process.start()

        # Join already completed processes for good measure
        for test_process in list(self.processes):
            test_process.join()
            self.processes.remove(test_process)

        # Adding stop in separate for to avoid a queue race condition
        for monitor in self.monitors:
            self.completed.put('STOP')

        # Make sure we wait until the queue has been emptied
        while self.completed.qsize() > 0:
            sleep(0.1)

        self.completed.close()
        self.completed.join_thread()

        # Join monitor thread
        for monitor in self.monitors:
            monitor.join()
