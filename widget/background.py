import pygame.image
import random

class Background:
    """绘制背景"""

    def __init__(self, screen, settings):
        """使用游戏界面进行初始化"""
        self.star  = pygame.image.load("images/star.bmp")
        self.screen = screen
        self.settings = settings
    
    def draw(self):
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


