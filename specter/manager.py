import multiprocessing as mp
import threading
import Queue
import time
from specter.spec import TestEvent


def execute_test(work_queue, completed_queue, all_cases, all_parents):
    while work_queue.qsize() > 0:
        # Get item and get real function to execute
        try:
            case_wrapper = work_queue.get()
            case_wrapper.case_func = all_cases[case_wrapper.case_func]
            case_wrapper.parent = all_parents[case_wrapper.parent]

            #print pid, case_wrapper.case_func
            case_wrapper.execute()
            completed_queue.put_nowait(case_wrapper)
        except:
            break
    return True


def watch_completed(completed_queue):
    while True:
        while completed_queue.qsize() > 0:
            wrapper = completed_queue.get_nowait()
            if wrapper == 'KILL':
                return

            all_cases = enumerate(wrapper.parent.cases)
            for index, val in all_cases:
                if wrapper.parent.cases[index].case_func == wrapper.case_func:
                    wrapper.parent.cases[index] = val

            wrapper.parent.top_parent.dispatch(TestEvent(wrapper))
        time.sleep(0.5)


class TestManager(object):

    def __init__(self, num_processes=4):
        self.processes = []
        self.num_processes = num_processes
        self.manager = mp.Manager()
        self.work_queue = self.manager.Queue()
        self.completed = self.manager.Queue()
        self.case_functions = {}
        self.case_parents = {}
        self.completed_thread_queue = Queue.Queue()

    def add_to_queue(self, case_wrapper):
        self.work_queue.put_nowait(case_wrapper)

        # Keep track of test functions
        key = hash(case_wrapper.case_func)
        self.case_functions[key] = case_wrapper.case_func

        # Keep track of parents
        key = hash(case_wrapper.parent)
        self.case_parents[key] = case_wrapper.parent

    def execute_all(self):
        # Create monitor thread
        self.monitor = threading.Thread(target=watch_completed,
                                        args=(self.completed_thread_queue,))
        self.monitor.start()

        args = (self.work_queue, self.completed, self.case_functions,
                self.case_parents)
        for i in range(0, self.num_processes):
            test_process = mp.Process(target=execute_test, args=args)
            test_process.daemon = True
            self.processes.append(test_process)
            test_process.start()
            test_process.run()

        # Manually block and resolve completed tests
        while True in [proc.is_alive() for proc in self.processes]:
            while self.completed.qsize() > 0:
                wrapper = self.completed.get()
                parent_hash = wrapper.parent
                func_hash = wrapper.case_func

                wrapper.parent = self.case_parents[parent_hash]
                wrapper.case_func = self.case_functions[func_hash]
                self.completed_thread_queue.put(wrapper)
            time.sleep(0.5)

        # Join already completed processes for good measure
        for test_process in list(self.processes):
            test_process.join()
            self.processes.remove(test_process)

        # Join monitor thread
        self.completed_thread_queue.put('KILL')
        self.monitor.join()
