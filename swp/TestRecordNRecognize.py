import unittest
from RecordNRecognize import Recorder
import time

class TestRecordNRecognize(unittest.TestCase):

    def setUp(self):
        self.record = Recorder()
        self.recfile = self.record.open("./unittest/" + str(int(time.time())) + ".wav", 'wb')

    def tearDown(self):
        pass

    def testStart_recording(self):
        pass

    def testStop_recording(self):
        pass

    def testClose(self):
        pass

if __name__ == '__main__':
    unittest.main()
