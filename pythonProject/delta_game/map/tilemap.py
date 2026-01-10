import pygame
from settings import TILE_SIZE

class TileMap:
    def __init__(self):
        self.map_data = [
            "11111111111111111111",
            "10000000000000000001",
            "1P0011111000000C0001",
            "10000000000001100001",
            "1000000000000000C001",
            "11111111111111111111",
        ]

        self.walls = []
        self.player_spawn = (0, 0)
        self.chest_spawns = []   # ⭐ 新增：宝箱生成点

        self._load_map()

    def _load_map(self):
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                world_x = x * TILE_SIZE
                world_y = y * TILE_SIZE

                if tile == "1":
                    self.walls.append(
                        pygame.Rect(
                            world_x,
                            world_y,
                            TILE_SIZE,
                            TILE_SIZE
                        )
                    )

                elif tile == "P":
                    self.player_spawn = (world_x, world_y)

                elif tile == "C":
                    self.chest_spawns.append((world_x, world_y))

    def draw(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, (100, 100, 100), wall)

    @property
    def width(self):
        return len(self.map_data[0]) * TILE_SIZE

    @property
    def height(self):
        return len(self.map_data) * TILE_SIZE
