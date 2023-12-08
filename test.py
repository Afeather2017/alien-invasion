import pygame
import unittest
import os

from widget.records import Records
from entities.laser import Laser
import main, threading

# 要测试的函数
def add(a, b):
    return a + b

# 编写测试用例
class TestGameStats(unittest.TestCase):

    def test_score_records(self):
        if os.path.exists('./score_record.sqlite3'):
            os.remove('./score_record.sqlite3')
        rec = Records()
        self.assertEqual(rec.highest_score(), 0)
        rec.record_new_entries((1, 9), (2, 10), (3, 11))
        self.assertEqual(rec.highest_score(), 11)

        del rec
        rec = Records()
        self.assertEqual(rec.highest_score(), 11)

    def test_laser_and_level(self):
        ai = main.AlienInvasion()
        th = threading.Thread(target=ai.run_game)
        th.start()
        th.join()

# 执行测试
if __name__ == '__main__':
    unittest.main()

