"""子弹的实现"""
import pygame
from pygame.sprite import Sprite
from pygame.sprite import Group

class Bullet(Sprite):
    """A class to manage bullets fired from the ship"""

    def __init__(self, screen, settings, position):
        """Create a bullet object at the ship's current position."""
        super().__init__()
        self.screen   = screen
        self.settings = settings
        self.color    = self.settings.bullet_color

        # Create a bullet rect at (0, 0) and then set correct position.
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
            self.settings.bullet_height)
        self.rect.midtop = position

        # Store the bullet's position as a decimal value.
        self.y = float(self.rect.y)

    def update(self):
        """Move the bullet up the screen."""
        # Update the decimal position of the bullet.
        self.y -= self.settings.bullet_speed
        # Update the rect position.
        self.rect.y = self.y

    def draw(self):
        """Draw the bullet to the screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)

class BulletGroup:
    """存放、处理一堆子弹的对象"""
    def __init__(self, screen, settings):
        self.settings = settings
        self.screen   = screen
        self.bullets  = Group()

    def fire(self, position):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self.screen, self.settings, position)
            self.bullets.add(new_bullet)

    def update(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

    def empty(self):
        """清空所有子弹"""
        return self.bullets.empty()

    def blitme(self):
        """绘制所有子弹"""
        for bullet in self.bullets.sprites():
            bullet.draw()

    def group(self):
        """获得Group对象"""
        return self.bullets

    def collision_action(self, another, kill_alien=False, kill_another=False):
        """和another发生碰撞后，是否删除bullet和another，返回碰撞的对象列表"""
        return pygame.sprite.groupcollide(
                self.bullets, another, kill_alien, kill_another)

    def is_collided_with(self, *args):
        """检测当前对象是否和任意对象有碰撞"""
        return pygame.sprite.spritecollideany(aliens, *args)
