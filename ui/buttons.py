import pygame
pygame.init()

class Button:
    def __init__(self, label, text_color, bg_color, width, height, pos, shape="rect", manager=None):
        self.label = label
        self.text_color = text_color
        self.bg_color = bg_color
        self.width = width
        self.height = height
        self.x, self.y = pos
        self.shape = shape  # "rect" or "ellipse"
        self.font = pygame.font.SysFont(None, self.height)
        
        self.rect = pygame.Rect(self.x, self.y, self.width + 10, self.height + 10)
        self.text_surface = self.font.render(self.label, True, self.text_color)
        self.text_surface = pygame.transform.scale(self.text_surface, [self.width, self.height])
        
        self.is_created = False
        self.pressed = False

        self.sound = None
        if manager:
            try:
                self.sound = manager.soundmanager
            except Exception as e:
                print(f"[Warning] Could not load button sound: {e}")

    def draw(self, surface):
        if self.shape == "ellipse":
            pygame.draw.ellipse(surface, self.bg_color, self.rect.inflate(5, 5))
        else:
            pygame.draw.rect(surface, self.bg_color, self.rect)

        surface.blit(self.text_surface, (self.rect.x + 5, self.rect.y + 5))
        self.is_created = True

    def is_pressed(self, pos):
        if self.is_created and self.rect.collidepoint(pos):
            if self.sound:
                self.sound.play("click")
            return True
        return False
