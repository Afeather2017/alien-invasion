import pygame
import unittest
import os

from widget.records  import Records
from entities.bullet import BulletGroup
from entities.laser  import LaserGroup
from entities.alien  import AlienGroup
from settings import *
import main, threading

pygame.init()

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

    def test_bullet(self):
        settings = Settings()
        mode = (settings.screen_width, settings.screen_height)
        screen = pygame.display.set_mode(mode)
        pygame.display.set_caption("Alien Invasion")
        bullets = BulletGroup(screen, settings)
        for i in range(10):
            self.assertEqual(len(bullets), min(i, 3))
            bullets.fire(screen.get_rect().midbottom)
        bullets.empty()
        self.assertEqual(len(bullets), 0)

    def test_laser(self):
        settings = Settings()
        mode = (settings.screen_width, settings.screen_height)
        screen = pygame.display.set_mode(mode)
        pygame.display.set_caption("Alien Invasion")
        lasers = LaserGroup(screen, settings)
        lasers.fire()
        self.assertEqual(len(lasers), 1)
        aliens = AlienGroup(screen, settings, 10)
        aliens.create_fleet()
        count = len(aliens)

        for i in range(10000):
            lasers.update()
            if aliens.collision_action(lasers, True, False):
                self.assertEqual(len(lasers), 1)
                self.assertGreaterEqual(count, len(aliens))
                count = len(aliens)

        self.assertEqual(len(aliens), 0)
        self.assertEqual(len(lasers), 0)

# 执行测试
if __name__ == '__main__':
    unittest.main()

