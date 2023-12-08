import pygame
from pygame.sprite import Sprite
from pygame.sprite import Group
 
class Laser(Sprite):
    """A class to manage bullets fired from the ship"""

    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # Create a bullet rect at (0, 0) and then set correct position.
        self.rect = pygame.Rect(0, 0, self.settings.laser_width,
            self.settings.laser_height)

        self.rect.topleft = (ai_game.lship.rect.midright[0], 0)
        self.x = self.rect.x

    def update(self):
        """Move the bullet up the screen."""
        # Update the decimal position of the bullet.
        self.x += self.settings.laser_speed
        # Update the rect position.
        self.rect.x = self.x

    def draw_laser(self):
        """Draw the bullet to the screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)

class LaserGroup(Group):
    def __init__(self):
        pass
