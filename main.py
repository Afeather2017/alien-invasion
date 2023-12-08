#!/usr/bin/python3
import sys
from time import sleep

import pygame

from settings import Settings
from widget.game_stats import GameStats
from widget.scoreboard import Scoreboard
from widget.button     import Button
from widget.label      import Label
from widget.records    import Records

from entities.ship      import Ship
from entities.left_ship import LeftShip
from entities.bullet    import Bullet
from entities.laser     import Laser
from entities.alien     import Alien

import time
import tools.debug
import random


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()
        self.screen   = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.records = Records()
        self.stats   = GameStats(self)
        self.sb      = Scoreboard(self)
        self.star    = pygame.image.load("images/star.bmp")

        self.ship    = Ship(self)
        self.lship   = LeftShip(self)
        self.bullets = pygame.sprite.Group()
        self.aliens  = pygame.sprite.Group()

        self._create_fleet()

        self.state_time = float('inf')
        self.ship_state = 'Normal'

        # Make the Play button.
        self.play_button = Button(self, "Play")
        self.guide_label   = Label(self, """
        Guide:\n
            Press '<-' to move ship to left and '->' to right.\n
            Press SPACE to shot bullet.\n
            Long press SPACE to use skill.\n
        """)

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            if   time.time_ns() - self.state_time >= 1500000000:
                self.ship_state = 'Normal'
                self.state_time = float('inf')
                self._fire_laser()
            elif time.time_ns() - self.state_time >= 1000000000:
                self.ship_state = 'UsingSkill'
            elif time.time_ns() - self.state_time >=  500000000:
                self.ship_state = 'SkillPrep'

            # 非阻塞调用
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self.lship.update()
                self._update_bullets()
                self._update_lasers()
                self._update_aliens()

            self._update_screen()

            '''
            锁帧，大约是120fps。

            比如我希望3ms刷新一次，也就是333fps，如果我希望每到3的倍数时刷新一次，
            那么整个时间序列如下：
            0 1 2 3 4 5 6 7 8 9
            0 1 2 0 1 2 0 1 2 0
            一共9ms，在第二行值为0的时候刷新。

            如果当前毫秒时间模3余2，表明现在需要等1ms。如果余1，需要等2ms。
            所以时间就是，(3 - ms % 3) % 3

            这么做的缺陷是，如果3ms没法刷新好界面，那么就会掉帧。

            不过在这里表现的不明显。

            由于这里使用120fps，所以是8ms左右
            '''
            t = (8 - time.time_ns() // 1000000 % 8) % 8
            if t != 0:
                time.sleep(t / 1000)

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.state_time = time.time_ns()
            self.ship_state = 'PushDown'

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_SPACE:
            if self.ship_state == 'PushDown':
                self._fire_bullet()
                self.ship_state = 'Normal'
                self.state_time = float('inf')

    def _fire_laser(self):
        """发射大范围激光"""
        self.lasers.add(Laser(self))

    def _update_lasers(self):
        """更新激光"""
        self.lasers.update()

        # Get rid of bullets that have disappeared.
        for laser in self.lasers.copy():
            if laser.rect.bottom <= 0:
                 self.lasers.remove(laser)

        self._check_laser_alien_collisions()

    def _check_laser_alien_collisions(self):
        """Respond to laser-alien collisions."""
        # Remove any lasers and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
                self.lasers, self.aliens, False, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.lasers.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                 self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """
        Check if the fleet is at an edge,
          then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                                (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
            
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _draw_background(self):
        """绘制背景"""
        self.screen.fill(self.settings.bg_color)
        width, height = self.screen.get_size()
        b = random.randint(0, height)
        # 图像的中心是界面的中心
        # 也就是解方程(height / 2) = k * (width / 2) + b
        k = (height / 2 - b) / (2 * width)
        for x in range(width // 100):
            x = x * 100 + random.randint(-50, 50)
            y = k * x + b
            offset = random.randint(-height // 200, height // 200)
            self.screen.blit(self.star, (x, y + offset))

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self._draw_background()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        for laser in self.lasers.sprites():
            laser.draw_laser()
        self.aliens.draw(self.screen)
        match self.ship_state:
            case 'Normal':
                self.ship.blitme()
            case 'PushDown':
                self.ship.blitme()
            case 'SkillPrep':
                self.lship.blitme()
            case 'UsingSkill':
                self.lship.blitme()

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
            self.guide_label.draw_label()

        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
