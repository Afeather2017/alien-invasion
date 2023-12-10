"""Alien的实现"""
import pygame
from pygame.sprite import Sprite, Group

class Alien(Sprite):
    """A class to represent a single alien in the fleet."""

    def __init__(self, screen, settings):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = screen
        self.settings = settings

        # Load the alien image and set its rect attribute.
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the alien's exact horizontal position.
        self.x = float(self.rect.x)

    def is_reach_left_right_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        return self.rect.right >= screen_rect.right or self.rect.left <= 0

    def is_reach_bottom_edge(self):
        """检查外星人是否到达屏幕底端"""
        screen_rect = self.screen.get_rect()
        # print(self.rect.bottom, screen_rect.bottom, self.rect.bottom >= screen_rect.bottom)
        return self.rect.bottom >= screen_rect.bottom

    def update(self):
        """Move the alien right or left."""
        self.x += (self.settings.alien_speed *
                        self.settings.fleet_direction)
        self.rect.x = self.x

class AlienGroup:
    """对Group()的包装"""
    def __init__(self, screen, settings, ship_height):
        self.screen = screen
        self.settings = settings
        self.aliens = Group()
        self.ship_height = ship_height

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self.screen, self.settings)
        alien_width, _ = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self.screen, self.settings)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship_height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _is_fleet_reach_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.is_reach_left_right_edges():
                return True
        return False

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def is_any_reach_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        ret = False
        for alien in self.aliens.sprites():
            if alien.is_reach_bottom_edge():
                ret = True
                break
        return ret

    def update(self):
        """
        Check if the fleet is at an edge,
          then update the positions of all aliens in the fleet.
        """
        if self._is_fleet_reach_edges():
            self._change_fleet_direction()
        self.aliens.update()

    def draw(self):
        """绘制所有外星人"""
        self.aliens.draw(self.screen)

    def empty(self):
        """清空所有外星人"""
        return self.aliens.empty()

    def group(self):
        """获得实际的Group对象"""
        return self.aliens

    def collision_action(self, another, kill_alien=False, kill_another=False):
        """和another发生碰撞后，是否删除alien和another，返回碰撞的对象列表"""
        return pygame.sprite.groupcollide(
                self.aliens, another.group(), kill_alien, kill_another)

    def is_collided_with(self, obj):
        """检测当前对象是否和对象有碰撞"""
        if hasattr(obj, 'group'):
            return bool(self.collision_action(obj, False, False))
        if hasattr(obj, 'sprite'):
            return bool(pygame.sprite.spritecollideany(obj.sprite(), self.aliens))
        raise RuntimeError(f'{type(obj)} not supported')

    def __len__(self):
        """获得数量"""
        return len(self.aliens)
