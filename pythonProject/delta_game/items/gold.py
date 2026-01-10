import pygame

class Gold:
    def __init__(self, x, y, value=1):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.value = value
        self.collected = False

    def update(self, player_rect):
        if self.rect.colliderect(player_rect):
            self.collected = True
            return self.value
        return 0

    def draw(self, screen):
        pygame.draw.rect(screen, (220, 200, 0), self.rect)
