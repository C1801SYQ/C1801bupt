import pygame

class Input:
    def __init__(self):
        self.keys = {
            pygame.K_w: False,
            pygame.K_s: False,
            pygame.K_a: False,
            pygame.K_d: False,
        }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.keys:
                self.keys[event.key] = True

        elif event.type == pygame.KEYUP:
            if event.key in self.keys:
                self.keys[event.key] = False

    def is_pressed(self, key):
        return self.keys.get(key, False)
