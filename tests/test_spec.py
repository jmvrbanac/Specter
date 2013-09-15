from time import sleep
from unittest2 import TestCase

from specter.spec import TimedObject


class TestTimedObject(TestCase):

    def test_creation_of_timed_object(self):
        obj = TimedObject()
        self.assertEqual(obj.start_time, 0)
        self.assertEqual(obj.end_time, 0)

    def test_start_stop(self):
        obj = TimedObject()
        obj.start()
        sleep(0.05)
        obj.stop()

        self.assertGreater(obj.start_time, 0)
        self.assertGreater(obj.end_time, 0)

    def test_elapsed_time(self):
        obj = TimedObject()
        obj.start()
        sleep(0.05)
        obj.stop()

        self.assertGreater(obj.elapsed_time, 0.05)