import pygame.font

class Label:
 
    def __init__(self, ai_game, msg):
        """Initialize button attributes."""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.msg = msg
        
        # Set the dimensions and properties of the button.
        self.width, self.height = 700, 250
        self.button_color = (0, 255, 0)
        self.text_color = (255, 255, 255)
        self.font = pygame.font.SysFont(None, 35)
        
        # Build the button's rect object and center it.
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(self.button_color)

    def draw_label(self, color=pygame.Color('black')):
        surface = self.surface
        text = self.msg
        font = self.font
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = self.width, self.height
        x, y = 0, 0
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, self.text_color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = 0  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = 0  # Reset the x.
            y += word_height  # Start on new row.
        x, y = self.screen_rect.center
        self.screen.blit(self.surface, (x - self.width // 2, y - self.height // 2))

