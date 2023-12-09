"""船的两种模式的实现"""
import pygame
from pygame.sprite import Sprite

class BottomShip(Sprite):
    """A class to manage the ship."""

    def __init__(self, screen, settings):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = screen
        self.settings = settings
        self.screen_rect = screen.get_rect()

        # Load the ship image and get its rect.
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()

        # Start each new ship at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom

        # Store a decimal value for the ship's horizontal position.
        self.x = float(self.rect.x)

        # Movement flags
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Update the ship's position based on movement flags."""
        # Update the ship's x value, not the rect.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # Update rect object from self.x.
        self.rect.x = self.x

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """Center the ship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

class LeftShip(Sprite):
    """A class to manage the ship."""

    def __init__(self, screen, settings):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = screen
        self.settings = settings
        self.screen_rect = screen.get_rect()

        # Load the ship image and get its rect.
        self.image = pygame.image.load('images/left_ship.bmp')
        self.rect = self.image.get_rect()

        # Start each new ship at the bottom center of the screen.
        self.rect.midleft = self.screen_rect.midleft

        # Store a decimal value for the ship's horizontal position.
        self.x = float(self.rect.x)

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """Center the ship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

class Ship:
    """The class contains 2 modes of ship"""
    def __init__(self, screen, settings):
        self.left = LeftShip(screen, settings)
        self.bott = BottomShip(screen, settings)
        self.stat = 'None'

    def to_left(self):
        """设置模式"""
        self.stat = 'Left'

    def to_bottom(self):
        """设置模式"""
        self.stat = 'Button'

    def stop(self):
        """让船停下来"""
        self.bott.moving_left  = False
        self.bott.moving_right = False

    def hide(self):
        """设置模式"""
        self.stat = 'None'

    def blitme(self):
        """绘制船"""
        if self.stat == 'Button':
            self.bott.blitme()
        elif self.stat == 'Left':
            self.left.blitme()

    def update(self):
        """更新船"""
        if self.stat == 'Button':
            self.bott.update()
        else:
            pass

    def reset(self):
        """设置移动方向。船设置到中间"""
        self.stat = 'Button'
        self.bott.center_ship()
        self.stop()

    def move_left(self):
        """设置移动方向。船在左边无法移动"""
        if self.stat == 'Button':
            self.bott.moving_left  = True
            self.bott.moving_right = False

    def move_right(self):
        """设置移动方向。船在左边无法移动"""
        if self.stat == 'Button':
            self.bott.moving_left  = False
            self.bott.moving_right = True

    def height(self):
        """获得船高度"""
        return self.bott.rect.height

    def width(self):
        """获得船宽度"""
        return self.bott.rect.width

    def shot_port(self):
        """获得船的尖端，这里是发射子弹的地方"""
        return self.bott.rect.midtop

    def sprite(self):
        """获得船自身"""
        return self.bott
