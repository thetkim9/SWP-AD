import unittest
from Trans import Translation
import os
class TestTrans(unittest.TestCase):

    def setUp(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/user/PycharmProjects/swp/TakeClass-16ca2bd11db5.json'
        self.trans = Translation()

    def tearDown(self):
        pass

    def testTranslate(self):
        result = self.trans.translate("hi", "Korean")
        self.assertTrue(result, "안녕")
        result = self.trans.translate("안녕", "English")
        self.assertTrue(result, "안녕")

if __name__ == '__main__':
    unittest.main()
