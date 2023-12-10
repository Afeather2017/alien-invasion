#!/usr/bin/python3
"""这是一个简单的外星人入侵游戏。
基本操作如下：
按下空格发射子弹；
当你长按空格的时候，会在左边发射激光；
如果外星人被清空了，你会升级，然后外星人的速度会提升；
如果你的飞船被攻击，或者外星人到达界面底部，你会失去一艘飞船，然后重新开始；
如果你没有飞船了，那么游戏会重新开始。

如果你破记录了，那么你的记录将会存储
"""
import sys
from time import sleep

import time
from enum import Enum
import pygame

from settings import Settings
from widget.game_stats import GameStats
from widget.scoreboard import Scoreboard
from widget.button     import Button
from widget.label      import Label
from widget.background import Background
from widget.records    import Records

from entities.ship      import Ship
from entities.bullet    import BulletGroup
from entities.laser     import LaserGroup
from entities.alien     import AlienGroup

class ShipStat(Enum):
    """船的状态"""
    NORMAL = 1
    PUSHDOWN = 2
    SKILLPREP = 3
    USINGSKILL = 4

class GameStat(Enum):
    """游戏的状态"""
    CONTINUE = 1
    ALIENS_INVADED = 2
    SHIP_DESTROYED = 3
    NEXT_LEVEL = 4

class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()
        mode = (self.settings.screen_width, self.settings.screen_height)
        self.screen   = pygame.display.set_mode(mode)
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.stats = GameStats(self)
        self.stats.high_score = Records().highest_score()
        print('highest score:', self.stats.high_score)
        self.sb    = Scoreboard(self)

        self.ship    = Ship       (self.screen, self.settings)
        self.bullets = BulletGroup(self.screen, self.settings)
        self.lasers  = LaserGroup (self.screen, self.settings)
        self.aliens  = AlienGroup (self.screen, self.settings, self.ship.height())

        self.background = Background(self.screen, self.settings)

        self.stat_time = float('inf')
        self.ship_stat = ShipStat.NORMAL

        self.in_control = True

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
        while self.in_control:
            if   time.time_ns() - self.stat_time >= 1500000000:
                self.ship_stat = ShipStat.NORMAL
                self.stat_time = float('inf')
                self.lasers.fire()
                self.ship.to_bottom()
            elif time.time_ns() - self.stat_time >= 1000000000:
                self.ship_stat = ShipStat.USINGSKILL
            elif time.time_ns() - self.stat_time >=  500000000:
                self.ship_stat = ShipStat.SKILLPREP
                self.ship.to_left()

            # 非阻塞调用
            self._check_events()

            game_stat = self._check_game_stat()
            match game_stat:
                case GameStat.CONTINUE:
                    pass
                case GameStat.NEXT_LEVEL:
                    self._level_up()
                case _:
                    self._ship_hit_action()

            self._collision_check_action()

            if self.stats.game_active:
                self.ship.update()
                self.bullets.update()
                self.lasers.update()
                self.aliens.update()

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
            还有个缺陷，因为线程上下文切换是10ms，所以实际上有没有那么多帧很难说。

            不过在这里表现的不明显。

            由于这里使用120fps，所以是8ms左右
            '''
            t = (8 - time.time_ns() // 1000000 % 8) % 8
            if t != 0:
                time.sleep(t / 1000)

    def _collision_check_action(self):
        collisions = self.aliens.collision_action(self.bullets, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)

        collisions = self.aliens.collision_action(self.lasers, True, False)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)

        self.sb.prep_score()
        self.sb.check_high_score()

    def _new_record(self):
        records = Records()
        records.record_new_entries((self.stats.level, self.stats.score))

    def _level_up(self):
        """下一个等级"""
        self.settings.increase_speed()

        # Increase level.
        self.stats.level += 1
        self.sb.prep_level()
        self._game_reset()

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
        button_clicked = self.play_button.is_clicked(mouse_pos)
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
            self.aliens.create_fleet()
            self.ship.reset()
            self.ship.to_bottom()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.move_right()
        elif event.key == pygame.K_LEFT:
            self.ship.move_left()
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            if self.ship_stat == ShipStat.NORMAL:
                self.stat_time = time.time_ns()
                self.ship_stat = ShipStat.PUSHDOWN

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.stop()
        elif event.key == pygame.K_LEFT:
            self.ship.stop()
        elif event.key == pygame.K_SPACE:
            if self.ship_stat == ShipStat.PUSHDOWN:
                self.bullets.fire(self.ship.shot_port())
                self.ship_stat = ShipStat.NORMAL
                self.stat_time = float('inf')

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.background.draw()
        self.bullets.blitme()
        self.lasers.blitme()
        self.aliens.draw()
        self.ship.blitme()

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
            self.guide_label.draw_label()

        pygame.display.flip()

    def _check_game_stat(self):
        """检测游戏是否可以继续，如果不能，返回不能继续的原因"""
        if not self.aliens.group():
            return GameStat.NEXT_LEVEL

        if self.aliens.is_any_reach_bottom():
            return GameStat.ALIENS_INVADED

        if self.aliens.is_collided_with(self.ship):
            return GameStat.SHIP_DESTROYED

        return GameStat.CONTINUE

    def _game_reset(self):
        """重置游戏"""
        self.sb.prep_ships()

        # Get rid of any remaining aliens and bullets.
        self.aliens.empty()
        self.bullets.empty()
        self.lasers.empty()

        # Create a new fleet and center the ship.
        self.aliens.create_fleet()
        self.ship.reset()

        # Pause.
        sleep(0.5)

    def _ship_hit_action(self):
        """Respond to the ship being hit by an alien."""
        self._new_record()
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self._game_reset()
        else:
            self.stats.game_active = False
            # pygame.mouse.set_visible(True)

    def kill_game(self):
        self.in_control = False

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
