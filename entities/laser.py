"""激光的控制与实现"""
import pygame
from pygame.sprite import Sprite
from pygame.sprite import Group

class Laser(Sprite):
    """A class to manage bullets fired from the ship"""

    def __init__(self, screen, settings):
        """Create a bullet object at the ship's current position."""
        super().__init__()
        self.screen = screen
        self.settings = settings
        self.color = settings.bullet_color

        # Create a bullet rect at (0, 0) and then set correct position.
        self.rect = pygame.Rect(0, 0, settings.laser_width, settings.laser_height)

        self.rect.topleft = (0, 0)
        self.x = self.rect.x

    def update(self):
        """Move the bullet up the screen."""
        # Update the decimal position of the bullet.
        self.x += self.settings.laser_speed
        # Update the rect position.
        self.rect.x = self.x

    def draw(self):
        """Draw the bullet to the screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)

class LaserGroup:
    """处理所有激光对象"""
    def __init__(self, screen, settings):
        """传入游戏界面对象"""
        self.screen   = screen
        self.settings = settings
        self.lasers    = Group()

    def update(self):
        """更新激光"""
        self.lasers.update()

        # Get rid of bullets that have disappeared.
        for laser in self.lasers.copy():
            if laser.rect.right > self.settings.screen_width:
                self.lasers.remove(laser)

    def fire(self):
        """发射大范围激光"""
        self.lasers.add(Laser(self.screen, self.settings))

    def collisions_with(self, aliens):
        """Respond to laser-alien collisions."""
        # Remove any lasers and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
                self.lasers, aliens, False, True)

        score = 0
        if collisions:
            for collided_aliens in collisions.values():
                score += self.settings.alien_points * len(collided_aliens)

        return score

    def blitme(self):
        """绘制所有激光"""
        for laser in self.lasers.sprites():
            laser.draw()

    def group(self):
        """获得Group对象"""
        return self.lasers

    def is_collided_with(self, *args):
        """检测当前对象是否和任意对象有碰撞"""
        return pygame.sprite.spritecollideany(self.group(), *args)

    def empty(self):
        """清空所有激光"""
        return self.lasers.empty()

    def __len__(self):
        """获得激光数量"""
        return len(self.lasers)
