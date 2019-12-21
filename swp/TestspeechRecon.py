import unittest
import speechRecon
import time

class TestspeechRecon(unittest.TestCase):

    def setUp(self):
        self.mic_manager = speechRecon.ResumableMicrophoneStream(speechRecon.SAMPLE_RATE, speechRecon.CHUNK_SIZE)

    def tearDown(self):
        pass

    def testGenerator(self):
        pass

if __name__ == '__main__':
    unittest.main()